"""
Depannage roadside assistance API routes.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.depannage import (
    DepannageRequestCreate,
    DepannageRequestForm,
    DepannageRequestUpdate,
    DepannageRequestResponse,
    DepannageRequestList,
    DepannageRequestSearch,
    DepannageStats,
    DashboardData,
    OperatorInfo
)
from app.services.depannage_service import DepannageService

router = APIRouter(prefix="/depannage", tags=["Depannage"])


# ─── Depannage Form (Public Access) ─────────────────────────────────────────────

@router.post(
    "/submit",
    response_model=DepannageRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Depannage assistance request (any authenticated user)",
    responses={
        201: {"description": "Depannage request submitted successfully"},
        401: {"description": "Authentication required"},
        422: {"description": "Validation error"},
    },
)
async def submit_depannage_request(
    form_data: DepannageRequestForm,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> DepannageRequestResponse:
    """Submit a Depannage roadside assistance request from any authenticated user."""
    service = DepannageService(db)
    return await service.create_request_from_form(form_data, user.id)


# ─── Depannage Request Management (Admin/Depannage Role) ─────────────────────

@router.post(
    "/requests",
    response_model=DepannageRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Depannage request (admin/depannage role)",
    responses={
        201: {"description": "Depannage request created successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"},
    },
)
async def create_request(
    request_data: DepannageRequestCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN))
) -> DepannageRequestResponse:
    """Create a new Depannage roadside assistance request (admin only)."""
    service = DepannageService(db)
    return await service.create_request(request_data)


@router.get(
    "/requests",
    response_model=DepannageRequestList,
    summary="Get Depannage requests with filtering and pagination",
    responses={
        200: {"description": "Depannage requests retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_requests(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: str = Query(None, description="Filter by status"),
    breakdown_type: str = Query(None, description="Filter by breakdown type"),
    search: str = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN))
) -> DepannageRequestList:
    """Get Depannage requests with filtering and pagination."""
    service = DepannageService(db)
    
    search_params = DepannageRequestSearch(
        query=search,
        status=status,
        breakdown_type=breakdown_type
    )
    
    return await service.get_requests(page=page, size=size, search_params=search_params)






@router.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Depannage request",
    responses={
        204: {"description": "Depannage request deleted successfully"},
        404: {"description": "Depannage request not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def delete_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DEPANAGE))
) -> None:
    """Delete a Depannage request (admin or depannage role)."""
    service = DepannageService(db)
    await service.delete_request(request_id)


# ─── Depannage Request Actions ───────────────────────────────────────────────────





@router.get(
    "/pending",
    response_model=List[DepannageRequestResponse],
    summary="Get pending Depannage requests",
    responses={
        200: {"description": "Pending requests retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_pending_requests(
    limit: int = Query(100, ge=1, le=100, description="Maximum number of requests"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN))
) -> List[DepannageRequestResponse]:
    """Get all pending Depannage requests that need to be claimed."""
    service = DepannageService(db)
    return await service.get_pending_requests(limit)




@router.get(
    "/recent",
    response_model=List[DepannageRequestResponse],
    summary="Get recent Depannage requests",
    responses={
        200: {"description": "Recent requests retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_recent_requests(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of requests"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN))
) -> List[DepannageRequestResponse]:
    """Get recent Depannage requests."""
    service = DepannageService(db)
    return await service.get_recent_requests(limit)


# ─── Search and Filtering ─────────────────────────────────────────────────────

@router.post(
    "/search",
    response_model=DepannageRequestList,
    summary="Search Depannage requests with advanced filters",
    responses={
        200: {"description": "Search completed successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def search_requests(
    search_params: DepannageRequestSearch,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN))
) -> DepannageRequestList:
    """Search Depannage requests with advanced filtering options."""
    service = DepannageService(db)
    return await service.search_requests(search_params)


# ─── Legacy Endpoints (for backward compatibility) ─────────────────────────────

@router.get(
    "/active",
    summary="Get active Depannage requests (admin role)",
    responses={
        200: {"description": "Active Depannage requests retrieved"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_active_requests(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    """Get all active Depannage requests for operators (legacy endpoint)."""
    service = DepannageService(db)
    pending_requests = await service.get_pending_requests(limit=50)
    
    return {
        "message": "Active Depannage requests retrieved",
        "operator": OperatorInfo(id=user.id, email=user.email, role=user.role),
        "active_requests": pending_requests,
        "total_count": len(pending_requests)
    }
