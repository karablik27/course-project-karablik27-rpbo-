# app/routers/upload.py

from fastapi import APIRouter, UploadFile

from app.middleware.files import secure_save_upload

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile) -> dict[str, str]:
    name = secure_save_upload(file)
    return {"filename": name}
