"""
General file upload API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.file_storage import save_upload
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Upload a file",
    responses={
        200: {"description": "File uploaded successfully"},
        401: {"description": "Authentication required"},
        422: {"description": "Validation error"},
    },
)
async def upload_file(
    file: UploadFile = File(...),
    service_type: str = "general",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload a file and return its URL."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    file_url = await save_upload(file, service_type)

    return {
        "url": file_url,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size,
        "service_type": service_type
    }
