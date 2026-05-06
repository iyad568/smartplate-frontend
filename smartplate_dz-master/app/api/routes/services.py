"""
Services API routes for document uploads.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.file_storage import save_upload
from app.db.session import get_db
from app.models.user import User
from app.models.car import Car
from app.schemas.car import DocumentUploadResponse
from app.services.car_service import CarService

router = APIRouter(prefix="/services", tags=["Services"])


@router.post(
    "/documents/vignette",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload vignette document",
    responses={
        200: {"description": "Vignette uploaded successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
        422: {"description": "Validation error"},
    },
)
async def upload_vignette_document(
    car_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload vignette document for a specific car."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images and PDF files are allowed."
        )
    
    car_service = CarService(db)
    document_url = await save_upload(file, "vignettes")
    return await car_service.update_document(
        car_id, "vignette_url", document_url, user.id
    )


@router.post(
    "/documents/controle-technique",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload contrôle technique document",
    responses={
        200: {"description": "Contrôle technique uploaded successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
        422: {"description": "Validation error"},
    },
)
async def upload_controle_technique_document(
    car_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload contrôle technique document for a specific car."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images and PDF files are allowed."
        )
    
    car_service = CarService(db)
    document_url = await save_upload(file, "controle-technique")
    return await car_service.update_document(
        car_id, "controle_technique_url", document_url, user.id
    )


@router.post(
    "/documents/assurance",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload assurance document",
    responses={
        200: {"description": "Assurance uploaded successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
        422: {"description": "Validation error"},
    },
)
async def upload_assurance_document(
    car_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload assurance document for a specific car."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images and PDF files are allowed."
        )
    
    car_service = CarService(db)
    document_url = await save_upload(file, "assurance")
    return await car_service.update_document(
        car_id, "assurance_paper_url", document_url, user.id
    )


@router.post(
    "/documents/cart-grise",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload carte grise document",
)
async def upload_cart_grise_document(
    car_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload carte grise document for a specific car."""
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images and PDF files are allowed."
        )

    car_service = CarService(db)
    document_url = await save_upload(file, "cart-grise")
    return await car_service.update_document(
        car_id, "cart_grise_url", document_url, user.id
    )


@router.get(
    "/documents/{car_id}",
    summary="Get all documents for a car",
    responses={
        200: {"description": "Documents retrieved successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def get_car_documents(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all uploaded documents for a specific car."""
    car_service = CarService(db)
    car = await car_service.get_car(car_id, user.id)
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Return all document URLs for the car
    documents = {
        "plate_photo_url": car.plate_photo_url,
        "license_url": car.license_url,
        "assurance_paper_url": car.assurance_paper_url,
        "vignette_url": car.vignette_url,
        "controle_technique_url": car.controle_technique_url,
    }
    
    return {
        "car_id": car.id,
        "plate_number": car.plate_number,
        "documents": {k: v for k, v in documents.items() if v is not None}
    }
