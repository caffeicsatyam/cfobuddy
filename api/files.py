from fastapi import APIRouter, BackgroundTasks, File, UploadFile

from api.main import (
    FileResponse,
    UploadResponse,
    list_files,
    upload_file,
)

router = APIRouter()


@router.get("/files", response_model=FileResponse)
async def files_proxy() -> FileResponse:
    return await list_files()


@router.post("/upload", response_model=UploadResponse)
async def upload_proxy(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> UploadResponse:
    return await upload_file(file=file, background_tasks=background_tasks)
