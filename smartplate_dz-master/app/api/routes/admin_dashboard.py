"""
API routes for Admin Dashboard functionality.
"""
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.car import CarResponse
from app.services.car_service import CarService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/dashboard/admin", tags=["Admin Dashboard"])


# ─── Admin Overview ─────────────────────────────────────────────────────

@router.get(
    "/overview",
    response_model=dict,
    summary="Get admin dashboard overview",
    responses={
        200: {"description": "Admin dashboard data retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def get_admin_overview(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get comprehensive admin dashboard data."""
    car_service = CarService(db)
    auth_service = AuthService(db)
    
    # Get system-wide car statistics
    car_stats = await car_service.get_stats()  # No user_id for system-wide stats
    
    # Get user statistics
    from app.db.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    total_users = await user_repo.count()
    
    return {
        "system_stats": {
            "total_cars": car_stats.total_cars,
            "total_users": total_users
        },
        "recent_cars": await car_service.get_recent_cars(limit=5),
        "admin_info": {
            "admin_id": admin.id,
            "admin_name": admin.full_name,
            "admin_email": admin.email
        }
    }


# ─── Admin Car Management ─────────────────────────────────────────────────

@router.get(
    "/cars",
    response_model=List[CarResponse],
    summary="Get all cars (admin only)",
    responses={
        200: {"description": "All cars retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def get_all_cars_admin(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of cars"),
    status: str = Query(None, description="Filter by status"),
    search: str = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> List[CarResponse]:
    """Get all cars in the system (admin only)."""
    car_service = CarService(db)
    
    # Prepare search parameters
    from app.schemas.car import CarSearch
    search_params = CarSearch(
        plate_number=search,
        status=status
    )
    
    cars = await car_service.get_cars(search_params=search_params, limit=limit)
    return cars.cars


@router.get(
    "/cars/{car_id}",
    response_model=CarResponse,
    summary="Get specific car details (admin only)",
    responses={
        200: {"description": "Car details retrieved successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def get_car_details_admin(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> CarResponse:
    """Get detailed information about a specific car (admin only)."""
    car_service = CarService(db)
    return await car_service.get_car(car_id, user_id=None)  # Admin can access any car


@router.put(
    "/cars/{car_id}/status",
    response_model=CarResponse,
    summary="Update car status (admin only)",
    responses={
        200: {"description": "Car status updated successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
        400: {"description": "Invalid status"},
    },
)
async def update_car_status_admin(
    car_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> CarResponse:
    """Update the status of any car (admin only)."""
    car_service = CarService(db)
    return await car_service.update_car_status(car_id, new_status, user_id=None)


@router.delete(
    "/cars/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete car (admin only)",
    responses={
        204: {"description": "Car deleted successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def delete_car_admin(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> None:
    """Delete any car from the system (admin only)."""
    car_service = CarService(db)
    await car_service.delete_car(car_id, user_id=None)


# ─── Admin User Management ─────────────────────────────────────────────────

@router.get(
    "/users",
    summary="Get all users (admin only)",
    responses={
        200: {"description": "Users retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def get_all_users_admin(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of users"),
    role: str = Query(None, description="Filter by role"),
    is_verified: bool = Query(None, description="Filter by verification status"),
    search: str = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all users in the system (admin only)."""
    from app.db.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    
    users = await user_repo.get_all(
        limit=limit,
        role=role,
        is_verified=is_verified,
        search=search
    )
    
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "last_login": getattr(user, 'last_login', None)
        }
        for user in users
    ]


@router.get(
    "/users/{user_id}",
    summary="Get specific user details (admin only)",
    responses={
        200: {"description": "User details retrieved successfully"},
        404: {"description": "User not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def get_user_details_admin(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get detailed information about a specific user (admin only)."""
    from app.db.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's cars
    car_service = CarService(db)
    user_cars = await car_service.get_user_cars(user_id)
    
    return {
        "user_info": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_verified": user.is_verified,
            "profile_picture": user.profile_picture,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        },
        "cars": [CarResponse.model_validate(car) for car in user_cars],
        "car_count": len(user_cars)
    }


@router.put(
    "/users/{user_id}/status",
    summary="Update user verification status (admin only)",
    responses={
        200: {"description": "User status updated successfully"},
        404: {"description": "User not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def update_user_status_admin(
    user_id: str,
    is_verified: bool,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update user verification status (admin only)."""
    auth_service = AuthService(db)
    
    updated_user = await auth_service.update_user_profile(user_id, {"is_verified": is_verified})
    
    return {
        "user_id": updated_user.id,
        "full_name": updated_user.full_name,
        "email": updated_user.email,
        "is_verified": updated_user.is_verified,
        "message": f"User verification status updated to {is_verified}"
    }


# ─── Admin Statistics ─────────────────────────────────────────────────────

@router.get(
    "/statistics",
    summary="Get system statistics (admin only)",
    responses={
        200: {"description": "Statistics retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def get_system_statistics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get comprehensive system statistics (admin only)."""
    car_service = CarService(db)
    car_stats = await car_service.get_stats()
    
    from app.db.repositories.user_repo import UserRepository
    user_repo = UserRepository(db)
    
    # Get user statistics
    total_users = await user_repo.count()
    verified_users = await user_repo.count(is_verified=True)
    
    # Get recent registrations
    recent_cars = await car_service.get_recent_cars(limit=10)
    recent_users = await user_repo.get_recent(limit=10)
    
    return {
        "car_statistics": car_stats,
        "user_statistics": {
            "total_users": total_users,
            "verified_users": verified_users,
            "unverified_users": total_users - verified_users,
            "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
        },
        "recent_activity": {
            "recent_cars": [CarResponse.model_validate(car) for car in recent_cars],
            "recent_users": [
                {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at
                }
                for user in recent_users
            ]
        }
    }


# ─── Admin Document Verification ───────────────────────────────────────────

@router.get(
    "/documents/pending",
    summary="Get pending document verifications (admin only)",
    responses={
        200: {"description": "Pending documents retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
    },
)
async def get_pending_documents(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of documents"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get cars with incomplete documents for admin review."""
    car_service = CarService(db)
    
    # Get all cars and filter for incomplete documents
    cars = await car_service.get_all(limit=limit)
    
    pending_docs = []
    for car in cars:
        missing_docs = []
        if not car.plate_photo_url:
            missing_docs.append("plate_photo")
        if not car.assurance_paper_url:
            missing_docs.append("insurance")
        if not car.license_url:
            missing_docs.append("license")
        
        if missing_docs:  # Only include cars with missing documents
            pending_docs.append({
                "car_id": car.id,
                "plate_number": car.plate_number,
                "user_id": car.user_id,
                "missing_documents": missing_docs,
                "created_at": car.created_at,
                "status": car.status
            })
    
    return pending_docs
