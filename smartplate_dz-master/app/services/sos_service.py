"""
Service for SOS request business operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.sos_repo import SOSRepository
from app.schemas.sos import (
    SOSRequestCreate,
    SOSRequestForm,
    SOSRequestUpdate,
    SOSRequestResponse,
    SOSRequestList,
    SOSRequestSearch,
    SOSStats,
    DashboardData
)
from app.models.sos_request import SOSRequest


class SOSService:
    """Service for SOS request business operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SOSRepository(db)
    
    async def create_request(self, request_data: SOSRequestCreate) -> SOSRequestResponse:
        """Create a new SOS request."""
        # Create the request
        sos_request = await self.repo.create(request_data.dict())
        return SOSRequestResponse.model_validate(sos_request)
    
    async def create_request_from_form(self, form_data: SOSRequestForm, user_id: str, user_email: str, user_phone: Optional[str] = None) -> SOSRequestResponse:
        """Create a new SOS request from form submission with auto-populated user data."""
        # Create request data with user information
        request_data = {
            "user_id": user_id,
            "full_name": form_data.full_name,
            "email": user_email,  # Use authenticated user's email
            "phone": user_phone,  # Use authenticated user's phone if available
            "license_plate": form_data.license_plate,
            "emergency_description": form_data.emergency_description,
            "current_location": form_data.current_location,
            "gps_coordinates": form_data.gps_coordinates
        }
        
        # Create the request
        sos_request = await self.repo.create(request_data)
        return SOSRequestResponse.model_validate(sos_request)
    
    async def get_request(self, request_id: str) -> SOSRequestResponse:
        """Get an SOS request by ID."""
        sos_request = await self.repo.get_by_id(request_id)
        if not sos_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SOS request not found"
            )
        return SOSRequestResponse.model_validate(sos_request)
    
    async def get_requests(
        self,
        page: int = 1,
        size: int = 50,
        search_params: Optional[SOSRequestSearch] = None
    ) -> SOSRequestList:
        """Get SOS requests with filtering and pagination."""
        # Validate pagination
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 50
        
        skip = (page - 1) * size
        
        # Prepare filters
        filters = {}
        if search_params:
            filters = {
                'status': search_params.status,
                'user_id': search_params.user_id if hasattr(search_params, 'user_id') else None,
                'is_active': search_params.is_active,
                'date_from': search_params.date_from,
                'date_to': search_params.date_to,
                'search': search_params.query
            }
        
        # Get requests and total count
        requests = await self.repo.get_all(skip=skip, limit=size, **filters)
        total = await self.repo.count(**filters)
        
        pages = (total + size - 1) // size if total > 0 else 0
        
        return SOSRequestList(
            requests=[SOSRequestResponse.model_validate(req) for req in requests],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    async def update_request(self, request_id: str, update_data: SOSRequestUpdate) -> SOSRequestResponse:
        """Update an SOS request."""
        # Check if request exists
        existing_request = await self.repo.get_by_id(request_id)
        if not existing_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SOS request not found"
            )
        
        # Update the request
        updated_request = await self.repo.update(request_id, update_data.dict(exclude_unset=True))
        return SOSRequestResponse.model_validate(updated_request)
    
    async def delete_request(self, request_id: str) -> bool:
        """Delete an SOS request."""
        # Check if request exists
        existing_request = await self.repo.get_by_id(request_id)
        if not existing_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SOS request not found"
            )
        
        return await self.repo.delete(request_id)
    
    async def get_pending_requests(self, limit: int = 100) -> List[SOSRequestResponse]:
        """Get all pending SOS requests."""
        requests = await self.repo.get_pending_requests(limit)
        return [SOSRequestResponse.model_validate(req) for req in requests]
    
        
    async def get_recent_requests(self, limit: int = 10) -> List[SOSRequestResponse]:
        """Get recent SOS requests."""
        requests = await self.repo.get_recent_requests(limit)
        return [SOSRequestResponse.model_validate(req) for req in requests]
    
    async def get_stats(self) -> SOSStats:
        """Get SOS request statistics."""
        stats = await self.repo.get_stats()
        return SOSStats(**stats)
    
    async def get_dashboard_data(self, operator_id: str) -> DashboardData:
        """Get comprehensive dashboard data for SOS operators."""
        # Get statistics
        stats = await self.get_stats()
        
        # Get recent requests
        recent_requests = await self.get_recent_requests(limit=5)
        
        # Get pending requests
        pending_requests = await self.get_pending_requests(limit=10)
        
        return DashboardData(
            stats=stats,
            recent_requests=recent_requests,
            pending_requests=pending_requests
        )
    
    async def search_requests(self, search_params: SOSRequestSearch) -> SOSRequestList:
        """Search SOS requests with advanced filters."""
        return await self.get_requests(search_params=search_params)
    
    async def update_request_status(self, request_id: str, new_status: str) -> SOSRequestResponse:
        """Update SOS request status."""
        # Validate status
        allowed_statuses = ["en attente", "en cours", "résolu", "annulé"]
        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"
            )
        
        # Check if request exists
        sos_request = await self.repo.get_by_id(request_id)
        if not sos_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SOS request not found"
            )
        
        # Validate status transition
        if new_status == "en cours" and sos_request.status != "en attente":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only en attente requests can be marked as en cours"
            )
        
        if new_status == "résolu" and sos_request.status not in ["en cours"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only en cours requests can be marked as résolu"
            )
        
        # Update status
        update_data = {"status": new_status}
        
        # Add operator info for status changes
        if new_status == "en cours":
            update_data["claimed_by"] = operator_id
            update_data["claimed_at"] = datetime.utcnow()
        elif new_status == "résolu":
            update_data["resolved_at"] = datetime.utcnow()
            if not sos_request.claimed_by:
                update_data["claimed_by"] = operator_id
        
        updated_request = await self.repo.update(request_id, update_data)
        return SOSRequestResponse.model_validate(updated_request)
