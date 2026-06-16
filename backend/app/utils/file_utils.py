import os
import uuid
import shutil
from pathlib import Path

UPLOAD_DIR = "app/storage/uploads"

def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(file_bytes: bytes, original_filename: str) -> str:
    ensure_upload_dir()
    ext = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path

def delete_file(file_path: str) -> bool:
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def get_file_size_kb(file_path: str) -> float:
    if os.path.exists(file_path):
        return round(os.path.getsize(file_path) / 1024, 2)
    return 0.0

def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")

def is_allowed_extension(filename: str, allowed: list) -> bool:
    return get_file_extension(filename) in allowed
