"""
Service for Depannage request business operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.depannage_repo import DepannageRepository
from app.schemas.depannage import (
    DepannageRequestCreate,
    DepannageRequestForm,
    DepannageRequestUpdate,
    DepannageRequestResponse,
    DepannageRequestList,
    DepannageRequestSearch,
    DepannageStats,
    DashboardData
)
from app.models.depannage_request import DepannageRequest


class DepannageService:
    """Service for Depannage request business operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DepannageRepository(db)
    
    async def create_request(self, request_data: DepannageRequestCreate) -> DepannageRequestResponse:
        """Create a new Depannage request."""
        depannage_request = await self.repo.create(request_data.dict())
        return DepannageRequestResponse.model_validate(depannage_request)
    
    async def create_request_from_form(self, form_data: DepannageRequestForm, user_id: str) -> DepannageRequestResponse:
        """Create a new Depannage request from form submission with auto-populated user data."""
        request_data = {
            "user_id": user_id,
            "full_name": form_data.full_name,
            "phone": form_data.phone,
            "license_plate": form_data.license_plate,
            "breakdown_type": form_data.breakdown_type,
            "location_address": form_data.location_address,
            "gps_coordinates": form_data.gps_coordinates,
            "additional_notes": form_data.additional_notes
        }
        
        depannage_request = await self.repo.create(request_data)
        return DepannageRequestResponse.model_validate(depannage_request)
    
    async def get_request(self, request_id: str) -> DepannageRequestResponse:
        """Get a Depannage request by ID."""
        depannage_request = await self.repo.get_by_id(request_id)
        if not depannage_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Depannage request not found"
            )
        return DepannageRequestResponse.model_validate(depannage_request)
    
    async def get_requests(
        self,
        page: int = 1,
        size: int = 50,
        search_params: Optional[DepannageRequestSearch] = None
    ) -> DepannageRequestList:
        """Get Depannage requests with filtering and pagination."""
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 50
        
        skip = (page - 1) * size
        
        filters = {}
        if search_params:
            filters = {
                'status': search_params.status,
                'breakdown_type': search_params.breakdown_type,
                'user_id': search_params.user_id if hasattr(search_params, 'user_id') else None,
                'is_active': search_params.is_active,
                'date_from': search_params.date_from,
                'date_to': search_params.date_to,
                'search': search_params.query
            }
        
        requests = await self.repo.get_all(skip=skip, limit=size, **filters)
        total = await self.repo.count(**filters)
        
        pages = (total + size - 1) // size if total > 0 else 0
        
        return DepannageRequestList(
            requests=[DepannageRequestResponse.model_validate(req) for req in requests],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    async def update_request(self, request_id: str, update_data: DepannageRequestUpdate) -> DepannageRequestResponse:
        """Update a Depannage request."""
        existing_request = await self.repo.get_by_id(request_id)
        if not existing_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Depannage request not found"
            )
        
        updated_request = await self.repo.update(request_id, update_data.dict(exclude_unset=True))
        return DepannageRequestResponse.model_validate(updated_request)
    
    async def delete_request(self, request_id: str) -> bool:
        """Delete a Depannage request."""
        existing_request = await self.repo.get_by_id(request_id)
        if not existing_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Depannage request not found"
            )
        
        return await self.repo.delete(request_id)
    
        
    async def get_pending_requests(self, limit: int = 100) -> List[DepannageRequestResponse]:
        """Get all pending Depannage requests."""
        requests = await self.repo.get_pending_requests(limit)
        return [DepannageRequestResponse.model_validate(req) for req in requests]
    
        
    async def get_recent_requests(self, limit: int = 10) -> List[DepannageRequestResponse]:
        """Get recent Depannage requests."""
        requests = await self.repo.get_recent_requests(limit)
        return [DepannageRequestResponse.model_validate(req) for req in requests]
    
    async def get_stats(self) -> DepannageStats:
        """Get Depannage request statistics."""
        stats = await self.repo.get_stats()
        return DepannageStats(**stats)
    
    async def get_dashboard_data(self, operator_id: str) -> DashboardData:
        """Get comprehensive dashboard data for Depannage operators."""
        stats = await self.get_stats()
        recent_requests = await self.get_recent_requests(limit=5)
        pending_requests = await self.get_pending_requests(limit=10)
        
        return DashboardData(
            stats=stats,
            recent_requests=recent_requests,
            pending_requests=pending_requests
        )
    
    async def search_requests(self, search_params: DepannageRequestSearch) -> DepannageRequestList:
        """Search Depannage requests with advanced filters."""
        return await self.get_requests(search_params=search_params)
    
    async def update_request_status(self, request_id: str, new_status: str) -> DepannageRequestResponse:
        """Update Depannage request status."""
        allowed_statuses = ["en attente", "en cours", "résolu", "annulé"]
        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"
            )
        
        depannage_request = await self.repo.get_by_id(request_id)
        if not depannage_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Depannage request not found"
            )
        
        if new_status == "en cours" and depannage_request.status != "en attente":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only en attente requests can be marked as en cours"
            )
        
        if new_status == "résolu" and depannage_request.status not in ["en cours"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only en cours requests can be marked as résolu"
            )
        
        update_data = {"status": new_status}
        
        updated_request = await self.repo.update(request_id, update_data)
        return DepannageRequestResponse.model_validate(updated_request)
