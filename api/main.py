import asyncio
import os
import json
import jwt
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Security
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from langchain_core.messages import HumanMessage 
from build_index import build_index         
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from cfobuddy_logging import configure_logging
from load_data import load_csvs_to_neon

load_dotenv()

logger = configure_logging()

EXPECTED_API_KEY = os.getenv("CFO_BUDDY_API_KEY")
if not EXPECTED_API_KEY:
    logger.error("CFO_BUDDY_API_KEY is not set; refusing to start.")
    raise RuntimeError("CFO_BUDDY_API_KEY is not set")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", EXPECTED_API_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day expiration

app = FastAPI(
    title="CFOBuddy AI",
    description="AI Powered Financial Assistant API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_scheme = HTTPBearer(auto_error=False)


def require_api_key(
    credentials: HTTPAuthorizationCredentials = Security(api_key_scheme),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid API key")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Global variable to track indexing status
indexing_status = {"status": "ready", "message": "........"}
def build_index_with_status():
    global indexing_status
    indexing_status = {"status": "indexing", "message": "Building index"}
    try:
        build_index()
        indexing_status = {"status" : "ready", "message": "Index built successfully"}
    except Exception as e:
        indexing_status = {"status": "error", "message": str(e)}
    

router = APIRouter(dependencies=[Depends(require_api_key)])

DATA_FOLDER = "data"
ALLOWED_EXTENSIONS = {"csv", "pdf", "xlsx", "xls", "docx"}

# ==========================
# SCHEMAS
# ==========================

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "main"

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    chart: Optional[dict] = None

class ThreadResponse(BaseModel):
    threads: list[str]

class FileInfo(BaseModel):
    name: str       # ← fix #2
    type: str
    size: str

class FileResponseModels(BaseModel):
    files: list[FileInfo]

class UploadResponse(BaseModel):
    message: str
    filename: str

class ErrorResponse(BaseModel):
    error: str

class LoginRequest(BaseModel):
    username: str
    password: str

# ==========================
# AUTH
# ==========================

@app.post("/token", tags=["Auth"])
async def login(form_data: LoginRequest):
    if form_data.username != "admin" or form_data.password != EXPECTED_API_KEY:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires
    to_encode = {"sub": form_data.username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}

# ==========================
# HEALTH
# ==========================

@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "CFO Buddy API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

# ==========================
# PARSER
# ==========================

def parse_response(messages):
    text = ""
    chart = None
    for msg in messages:
        content = msg.content
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text += block.get("text", "")
        elif isinstance(content, str):
            if "CHART_DATA:" in content:
                try:
                    json_str = content.split("CHART_DATA:")[1].strip()
                    chart = json.loads(json_str)
                except Exception:
                    pass
            else:
                if hasattr(msg, "type") and msg.type == "ai":
                    text = content
    return text.strip(), chart

# ==========================
# ROUTES
# ==========================

@router.get("/threads", response_model=ThreadResponse)
async def get_threads():
    from core.memory import retrieve_all_threads
    try:
        threads = retrieve_all_threads()
        return ThreadResponse(threads=threads if threads else ["main"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)    # ← fix #4
async def chat(request: ChatRequest):
    from core import CFOBuddy
    config = {"configurable": {"thread_id": request.thread_id}}
    try:
        # LangGraph invoke is synchronous; run it in a thread to avoid
        # blocking the FastAPI event loop.
        response = await asyncio.to_thread(
            CFOBuddy.invoke,
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
        )
        text, chart = parse_response(response["messages"])
        return ChatResponse(response=text, thread_id=request.thread_id, chart=chart)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files", response_model=FileResponseModels)
async def list_files():
    if not os.path.exists(DATA_FOLDER):
        return FileResponseModels(files=[])
    files = []
    for f in os.listdir(DATA_FOLDER):
        ext = os.path.splitext(f)[1].lower()
        if ext.lstrip(".") in ALLOWED_EXTENSIONS:
            size = os.path.getsize(os.path.join(DATA_FOLDER, f))
            files.append(FileInfo(name=f, type=ext.lstrip(".").upper(), size=f"{size/1024:.1f} KB"))
    return FileResponseModels(files=files)


#Uploading the file and building the index can take some time, so we run build_index in the background after a file is uploaded. This way, the user gets an immediate response that their file was received, and the indexing happens asynchronously without blocking the API.
@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    
    filepath = os.path.join(DATA_FOLDER, file.filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    ext = os.path.splitext(file.filename)[1].lower()

    if ext == ".csv":
        logger.info("CSV file uploaded!")
        background_tasks.add_task(load_csvs_to_neon)
        background_tasks.add_task(build_index_with_status)

    else:
        logger.info("File uploaded: %s | type: %s | size: %.1f KB", file.filename, ext, len(content)/1024)
        background_tasks.add_task(build_index_with_status)

    return UploadResponse(
        message= f" '{file.filename}' uploaded Successfully!",
        filename=file.filename
    )

@router.get("/threads/{thread_id}/history")
async def get_history(thread_id: str):
    from core import CFOBuddy
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = CFOBuddy.get_state(config)
        messages = state.values.get("messages", [])
        return {
            "thread_id": thread_id,
            "messages": [
                {
                    "role": msg.type,
                    "content": msg.content if isinstance(msg.content, str) else str(msg.content)
                }
                for msg in messages
                if msg.type in ["human", "ai"]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/indexing_status")
async def get_indexing_status():
    return indexing_status

app.include_router(router)


@app.get('/charts/{filename}')
async def serve_chart(filename: str):
    """Serve chart images."""
    chart_path = Path("static/charts") / filename
    if chart_path.exists():
        return FileResponse(chart_path, media_type='image/png')
    raise HTTPException(status_code=404, detail="Chart not found")