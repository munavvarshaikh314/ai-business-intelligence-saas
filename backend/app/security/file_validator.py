from fastapi import HTTPException

ALLOWED_EXTENSIONS = {"csv", "pdf"}
MAX_FILE_SIZE_MB = 20


class FileValidator:

    @staticmethod
    def validate_file(filename: str, file_size_bytes: int):

        ext = filename.split(".")[-1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV/PDF allowed.")

        max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024

        if file_size_bytes > max_bytes:
            raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB} MB allowed.")

        return True