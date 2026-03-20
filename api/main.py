import os
import json
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
from langchain_core.messages import HumanMessage 
from build_index import build_index         
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="CFO Buddy API",
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

router = APIRouter()

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

class FileResponse(BaseModel):
    files: list[FileInfo]

class UploadResponse(BaseModel):
    message: str
    filename: str

class ErrorResponse(BaseModel):
    error: str

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

@router.post("/upload")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    # Save file first
    filepath = os.path.join(DATA_FOLDER, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # Rebuild index in background — user doesn't wait
    background_tasks.add_task(build_index)
    
    return {"message": "File uploaded! Indexing in progress...", "filename": file.filename}

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
        response = CFOBuddy.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        )
        text, chart = parse_response(response["messages"])
        return ChatResponse(response=text, thread_id=request.thread_id, chart=chart)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files", response_model=FileResponse)
async def list_files():
    if not os.path.exists(DATA_FOLDER):
        return FileResponse(files=[])
    files = []
    for f in os.listdir(DATA_FOLDER):
        ext = os.path.splitext(f)[1].lower()
        if ext.lstrip(".") in ALLOWED_EXTENSIONS:
            size = os.path.getsize(os.path.join(DATA_FOLDER, f))
            files.append(FileInfo(name=f, type=ext.lstrip(".").upper(), size=f"{size/1024:.1f} KB"))
    return FileResponse(files=files)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Supported types: {', '.join(ALLOWED_EXTENSIONS)}")
    os.makedirs(DATA_FOLDER, exist_ok=True)
    filepath = os.path.join(DATA_FOLDER, file.filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    return UploadResponse(message=f"'{file.filename}' uploaded!", filename=file.filename)


app.include_router(router)