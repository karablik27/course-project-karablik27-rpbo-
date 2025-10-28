# app/middleware/files.py
import imghdr
import os
import uuid

from fastapi import HTTPException, UploadFile

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


def secure_save_upload(file: UploadFile) -> str:
    """Сохраняет файл безопасно: проверяет тип, ограничивает размер и имя."""
    # 1. Проверяем размер
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > 5 * 1024 * 1024:  # лимит 5MB
        raise HTTPException(status_code=413, detail="File too large")

    # 2. Проверяем magic bytes (только изображения)
    head = file.file.read(512)
    file.file.seek(0)
    kind = imghdr.what(None, head)
    if kind not in {"jpeg", "png", "gif"}:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # 3. Генерируем безопасное UUID-имя
    filename = f"{uuid.uuid4()}.{kind}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, filename)

    # 4. Сохраняем в безопасной директории (без path traversal)
    with open(path, "wb") as out_file:
        out_file.write(file.file.read())

    return filename
