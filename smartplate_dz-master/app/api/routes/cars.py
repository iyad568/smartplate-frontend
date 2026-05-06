"""
API routes for Car management.
"""
from typing import List

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.car import (
    CarCreate,
    CarUpdate,
    CarResponse,
    CarList,
    CarSearch,
    CarStats,
    DashboardData,
    QRCodeResponse,
    DocumentUploadResponse
)
from app.services.car_service import CarService

router = APIRouter(prefix="/cars", tags=["Cars"])


# ─── Car Management ───────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new car",
    responses={
        201: {"description": "Car created successfully"},
        400: {"description": "Plate number already exists"},
        401: {"description": "Authentication required"},
    },
)
async def create_car(
    car_data: CarCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> CarResponse:
    """Create a new car for the current user."""
    service = CarService(db)
    return await service.create_car(car_data, user.id)


@router.get(
    "/",
    response_model=CarList,
    summary="Get cars with pagination",
    responses={
        200: {"description": "Cars retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_cars(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    user_id: str = Query(None, description="Filter by user ID (admin only)"),
    status: str = Query(None, description="Filter by status"),
    has_complete_documents: bool = Query(None, description="Filter by document completion"),
    is_complete_profile: bool = Query(None, description="Filter by profile completion"),
    search: str = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> CarList:
    """Get cars with optional filters and pagination."""
    service = CarService(db)
    
    # Prepare search parameters
    search_params = CarSearch(
        plate_number=search,
        status=status,
        has_complete_documents=has_complete_documents,
        is_complete_profile=is_complete_profile
    )
    
    # If user is not admin, only show their own cars
    target_user_id = user_id if user.role == UserRole.ADMIN else user.id
    
    return await service.get_cars(
        user_id=target_user_id,
        page=page,
        size=size,
        search_params=search_params
    )


@router.get(
    "/public/{qr_code}",
    summary="Get public vehicle info by QR code",
    responses={
        200: {"description": "Public vehicle info returned"},
        404: {"description": "Vehicle not found"},
    },
)
async def get_public_vehicle_info(
    qr_code: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Public QR scan endpoint — returns vehicle data only (no personal info)."""
    service = CarService(db)
    car = await service.get_car_by_qr_code(qr_code)
    return {
        "qr_code": car.qr_code,
        "plate_number": car.plate_number,
        "vehicle_type": car.vehicle_type,
        "vehicle_brand": car.vehicle_brand,
        "power_type": car.power_type,
        "plate_photo_url": car.plate_photo_url,
        "status": car.status,
        "is_active": car.is_active,
    }


@router.get(
    "/{car_id}",
    response_model=CarResponse,
    summary="Get a car by ID",
    responses={
        200: {"description": "Car retrieved successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def get_car(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> CarResponse:
    """Get a car by ID."""
    service = CarService(db)
    # Admin can see any car, users can only see their own
    user_id = None if user.role == UserRole.ADMIN else user.id
    return await service.get_car(car_id, user_id)


@router.get(
    "/plate/{plate_number}",
    response_model=CarResponse,
    summary="Get a car by plate number",
    responses={
        200: {"description": "Car retrieved successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def get_car_by_plate(
    plate_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> CarResponse:
    """Get a car by plate number."""
    service = CarService(db)
    # Admin can see any car, users can only see their own
    user_id = None if user.role == UserRole.ADMIN else user.id
    return await service.get_car_by_plate(plate_number, user_id)


@router.get(
    "/qr/{qr_code}",
    response_model=CarResponse,
    summary="Get a car by QR code",
    responses={
        200: {"description": "Car retrieved successfully"},
        404: {"description": "Car not found"},
    },
)
async def get_car_by_qr_code(
    qr_code: str,
    db: AsyncSession = Depends(get_db)
) -> CarResponse:
    """Get a car by QR code (public endpoint)."""
    service = CarService(db)
    return await service.get_car_by_qr_code(qr_code)


@router.put(
    "/{car_id}",
    response_model=CarResponse,
    summary="Update a car",
    responses={
        200: {"description": "Car updated successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def update_car(
    car_id: str,
    update_data: CarUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> CarResponse:
    """Update a car."""
    service = CarService(db)
    # Admin can update any car, users can only update their own
    user_id = None if user.role == UserRole.ADMIN else user.id
    return await service.update_car(car_id, update_data, user_id)


@router.delete(
    "/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a car",
    responses={
        204: {"description": "Car deleted successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def delete_car(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> None:
    """Delete a car."""
    service = CarService(db)
    # Admin can delete any car, users can only delete their own
    user_id = None if user.role == UserRole.ADMIN else user.id
    await service.delete_car(car_id, user_id)


@router.get(
    "/{car_id}/qr-code",
    response_model=QRCodeResponse,
    summary="Get QR code for a car",
    responses={
        200: {"description": "QR code retrieved successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def get_qr_code(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> QRCodeResponse:
    """Get QR code for a car."""
    service = CarService(db)
    # Admin can see any QR code, users can only see their own
    user_id = None if user.role == UserRole.ADMIN else user.id
    return await service.get_qr_code(car_id, user_id)


# ─── Document Management ─────────────────────────────────────────────────

@router.put(
    "/{car_id}/documents/{document_type}",
    response_model=DocumentUploadResponse,
    summary="Update a document for a car",
    responses={
        200: {"description": "Document updated successfully"},
        400: {"description": "Invalid document type"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def update_document(
    car_id: str,
    document_type: str,
    document_url: str = Query(..., description="URL to the uploaded document"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> DocumentUploadResponse:
    """Update a document for a car."""
    service = CarService(db)
    return await service.update_document(car_id, document_type, document_url, user.id)


@router.get(
    "/{car_id}/documents",
    response_model=dict,
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
) -> dict:
    """Get all documents for a car."""
    service = CarService(db)
    car = await service.get_car(car_id, user.id)
    
    # Return all document URLs
    return {
        "plate_photo_url": car.plate_photo_url,
        "assurance_paper_url": car.assurance_paper_url,
        "license_url": car.license_url,
        "vignette_url": car.vignette_url,
        "controle_technique_url": car.controle_technique_url,
    }


# ─── Status Management ─────────────────────────────────────────────────

@router.put(
    "/{car_id}/status",
    response_model=CarResponse,
    summary="Update car status",
    responses={
        200: {"description": "Car status updated successfully"},
        400: {"description": "Invalid status"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def update_car_status(
    car_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> CarResponse:
    """Update car status."""
    service = CarService(db)
    # Admin can update any car status, users can only update their own
    user_id = None if user.role == UserRole.ADMIN else user.id
    return await service.update_car_status(car_id, new_status, user_id)


# ─── Search and Filtering ─────────────────────────────────────────────────

@router.post(
    "/search",
    response_model=CarList,
    summary="Search cars with advanced filters",
    responses={
        200: {"description": "Search completed successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def search_cars(
    search_params: CarSearch,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.USER))
) -> CarList:
    """Search cars with advanced filtering options."""
    service = CarService(db)
    return await service.search_cars(search_params, page, size)


# ─── Dashboard and Statistics ─────────────────────────────────────────────

@router.get(
    "/dashboard",
    response_model=DashboardData,
    summary="Get car dashboard data",
    responses={
        200: {"description": "Dashboard data retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> DashboardData:
    """Get comprehensive dashboard data for cars."""
    service = CarService(db)
    return await service.get_dashboard_data(user.id)


@router.get(
    "/stats",
    response_model=CarStats,
    summary="Get car statistics",
    responses={
        200: {"description": "Statistics retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_stats(
    user_id: str = Query(None, description="Get stats for specific user (admin only)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> CarStats:
    """Get car statistics."""
    service = CarService(db)
    target_user_id = user_id if user.role == UserRole.ADMIN else user.id
    return await service.get_stats(target_user_id)


# ─── Utility Endpoints ─────────────────────────────────────────────────────

@router.get(
    "/my-cars",
    response_model=List[CarResponse],
    summary="Get current user's cars",
    responses={
        200: {"description": "Cars retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
async def get_my_cars(
    limit: int = Query(100, ge=1, le=100, description="Maximum number of cars"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[CarResponse]:
    """Get all cars for the current user."""
    service = CarService(db)
    return await service.get_user_cars(user.id, limit)


@router.get(
    "/recent",
    response_model=List[CarResponse],
    summary="Get recent cars",
    responses={
        200: {"description": "Recent cars retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_recent_cars(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of cars"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN))
) -> List[CarResponse]:
    """Get recent cars (admin only)."""
    service = CarService(db)
    return await service.get_recent_cars(limit)


@router.get(
    "/check-availability/{plate_number}",
    summary="Check if plate number is available",
    responses={
        200: {"description": "Plate availability checked"},
    },
)
async def check_plate_availability(
    plate_number: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Check if a plate number is available for registration."""
    service = CarService(db)
    return await service.verify_plate_number_availability(plate_number)
