import os
import re
from fastapi import APIRouter, UploadFile, File, HTTPException

from api.main import FilesResponse, FileInfo, UploadResponse

router = APIRouter()

DATA_FOLDER="data"
ALLOWED_EXTENSIONS= {"csv","pdf","xlsx","xls","docx"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _secure_filename(filename: str) -> str:
    """Simple filename sanitiser (strips path separators and dangerous chars)."""
    filename = os.path.basename(filename)
    filename = re.sub(r"[^\w.\-]", "_", filename)
    return filename or "upload"


@router.get("/files", response_model=FilesResponse)
async def list_files():
    if not os.path.exists(DATA_FOLDER):
        return FilesResponse(files=[])
 
    files = []
    for f in os.listdir(DATA_FOLDER):
        ext = os.path.splitext(f)[1].lower()
        if ext.lstrip(".") in ALLOWED_EXTENSIONS:
            size = os.path.getsize(os.path.join(DATA_FOLDER, f))
            files.append(FileInfo(
                name=f,
                type=ext.lstrip(".").upper(),
                size=f"{size / 1024:.1f} KB"
            ))
    return FilesResponse(files=files)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
 
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
 
    filename = _secure_filename(file.filename)
    os.makedirs(DATA_FOLDER, exist_ok=True)
 
    filepath = os.path.join(DATA_FOLDER, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
 
    return UploadResponse(
        message=f"'{filename}' uploaded successfully. Run build_index.py to index it.",
        filename=filename
    )

