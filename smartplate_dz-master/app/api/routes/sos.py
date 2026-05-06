"""
SOS endpoints — accessible only to users with role=sos (or admin).

These are placeholders showing how to wire RBAC; replace the bodies with
real SOS emergency assistance API routes.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.sos import (
    SOSRequestCreate,
    SOSRequestForm,
    SOSRequestUpdate,
    SOSRequestResponse,
    SOSRequestList,
    SOSRequestSearch,
    SOSStats,
    DashboardData,
    OperatorInfo
)
from app.services.sos_service import SOSService

router = APIRouter(prefix="/sos", tags=["SOS"])


# ─── SOS Form (Public Access) ─────────────────────────────────────────────────────

@router.post(
    "/submit",
    response_model=SOSRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit SOS emergency request (any authenticated user)",
    responses={
        201: {"description": "SOS request submitted successfully"},
        401: {"description": "Authentication required"},
        422: {"description": "Validation error"},
    },
)
async def submit_sos_request(
    form_data: SOSRequestForm,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> SOSRequestResponse:
    """Submit an SOS emergency assistance request from any authenticated user."""
    service = SOSService(db)
    return await service.create_request_from_form(
        form_data=form_data,
        user_id=user.id,
        user_email=user.email,
        user_phone=user.phone
    )


# ─── SOS Request Management (Admin/SOS Role) ─────────────────────────────────────

@router.post(
    "/requests",
    response_model=SOSRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new SOS request (admin/SOS role)",
    responses={
        201: {"description": "SOS request created successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"},
    },
)
async def create_request(
    request_data: SOSRequestCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.SOS, UserRole.ADMIN))
) -> SOSRequestResponse:
    """Create a new SOS emergency assistance request (admin/SOS role only)."""
    service = SOSService(db)
    return await service.create_request(request_data)


@router.get(
    "/requests",
    response_model=SOSRequestList,
    summary="Get SOS requests with filtering and pagination",
    responses={
        200: {"description": "SOS requests retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_requests(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: str = Query(None, description="Filter by status"),
    search: str = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.SOS, UserRole.ADMIN))
) -> SOSRequestList:
    """Get SOS requests with filtering and pagination."""
    service = SOSService(db)
    
    search_params = SOSRequestSearch(
        query=search,
        status=status
    )
    
    return await service.get_requests(page=page, size=size, search_params=search_params)






@router.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete SOS request",
    responses={
        204: {"description": "SOS request deleted successfully"},
        404: {"description": "SOS request not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def delete_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN))
) -> None:
    """Delete an SOS request (admin only)."""
    service = SOSService(db)
    await service.delete_request(request_id)


# ─── SOS Request Actions ───────────────────────────────────────────────────────





@router.get(
    "/pending",
    response_model=List[SOSRequestResponse],
    summary="Get pending SOS requests",
    responses={
        200: {"description": "Pending requests retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_pending_requests(
    limit: int = Query(100, ge=1, le=100, description="Maximum number of requests"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.SOS))
) -> List[SOSRequestResponse]:
    """Get all pending SOS requests that need to be claimed."""
    service = SOSService(db)
    return await service.get_pending_requests(limit)




@router.get(
    "/recent",
    response_model=List[SOSRequestResponse],
    summary="Get recent SOS requests",
    responses={
        200: {"description": "Recent requests retrieved successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_recent_requests(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of requests"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.SOS, UserRole.ADMIN))
) -> List[SOSRequestResponse]:
    """Get recent SOS requests."""
    service = SOSService(db)
    return await service.get_recent_requests(limit)


# ─── Search and Filtering ─────────────────────────────────────────────────────

@router.post(
    "/search",
    response_model=SOSRequestList,
    summary="Search SOS requests with advanced filters",
    responses={
        200: {"description": "Search completed successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def search_requests(
    search_params: SOSRequestSearch,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.SOS, UserRole.ADMIN))
) -> SOSRequestList:
    """Search SOS requests with advanced filtering options."""
    service = SOSService(db)
    return await service.search_requests(search_params)


# ─── Legacy Endpoints (for backward compatibility) ─────────────────────────────

@router.get(
    "/active",
    summary="Get active SOS requests (sos role)",
    responses={
        200: {"description": "Active SOS requests retrieved"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_active_requests(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.SOS)),
):
    """Get all active SOS requests for operators (legacy endpoint)."""
    service = SOSService(db)
    pending_requests = await service.get_pending_requests(limit=50)
    
    return {
        "message": "Active SOS requests retrieved",
        "operator": OperatorInfo(id=user.id, email=user.email, role=user.role),
        "active_requests": pending_requests,
        "total_count": len(pending_requests)
    }
