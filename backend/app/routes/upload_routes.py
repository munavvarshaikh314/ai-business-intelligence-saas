from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, File
from app.dependencies import get_current_user
from app.services.upload_service import UploadService
from app.services.background_index_service import BackgroundIndexService
from app.security.file_validator import FileValidator

router = APIRouter()


@router.post("/csv/{dataset_id}")
async def upload_csv(
    dataset_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    file_bytes = await file.read()

    FileValidator.validate_file(
        file.filename,
        len(file_bytes)
    )

    await file.seek(0)

    return await UploadService.upload_csv(
        dataset_id,
        current_user.id,
        file
    )


@router.post("/pdf/{dataset_id}")
async def upload_pdf(
    dataset_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    file_bytes = await file.read()

    FileValidator.validate_file(
        file.filename,
        len(file_bytes)
    )

    await file.seek(0)

    result = await UploadService.save_pdf_file_only(
        dataset_id,
        current_user.id,
        file
    )

    background_tasks.add_task(
        BackgroundIndexService.index_pdf,
        dataset_id,
        current_user.id,
        result["file_path"],
        result["file_id"],
    )

    return {
        "message": "PDF uploaded successfully. Indexing started in the background.",
        "status": "QUEUED"
    }


@router.get("/status/{dataset_id}")
def upload_status(
    dataset_id: str,
    current_user=Depends(get_current_user)
):
    return UploadService.get_upload_status(
        dataset_id,
        current_user.id
    )
