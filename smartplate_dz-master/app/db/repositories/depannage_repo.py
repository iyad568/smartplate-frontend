"""
Repository for Depannage request database operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.depannage_request import DepannageRequest


class DepannageRepository:
    """Repository for Depannage request database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, request_data: dict) -> DepannageRequest:
        """Create a new Depannage request."""
        request_data['id'] = str(uuid4())
        request_data['created_at'] = datetime.utcnow()
        request_data['updated_at'] = datetime.utcnow()
        
        depannage_request = DepannageRequest(**request_data)
        self.db.add(depannage_request)
        await self.db.flush()
        return depannage_request
    
    async def get_by_id(self, request_id: str) -> Optional[DepannageRequest]:
        """Get a Depannage request by ID."""
        stmt = select(DepannageRequest).where(DepannageRequest.id == request_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        breakdown_type: Optional[str] = None,
        user_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> List[DepannageRequest]:
        """Get Depannage requests with optional filters."""
        stmt = select(DepannageRequest)
        
        conditions = []
        
        if status:
            conditions.append(DepannageRequest.status == status)
        if breakdown_type:
            conditions.append(DepannageRequest.breakdown_type == breakdown_type)
        if user_id:
            conditions.append(DepannageRequest.user_id == user_id)
        if is_active is not None:
            conditions.append(DepannageRequest.is_active == is_active)
        if date_from:
            conditions.append(DepannageRequest.created_at >= date_from)
        if date_to:
            conditions.append(DepannageRequest.created_at <= date_to)
        if search:
            conditions.append(
                or_(
                    DepannageRequest.full_name.ilike(f"%{search}%"),
                    DepannageRequest.phone.ilike(f"%{search}%"),
                    DepannageRequest.license_plate.ilike(f"%{search}%"),
                    DepannageRequest.breakdown_type.ilike(f"%{search}%"),
                    DepannageRequest.location_address.ilike(f"%{search}%")
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(DepannageRequest.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def count(
        self,
        status: Optional[str] = None,
        breakdown_type: Optional[str] = None,
        user_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> int:
        """Count Depannage requests with optional filters."""
        stmt = select(func.count(DepannageRequest.id))
        
        conditions = []
        
        if status:
            conditions.append(DepannageRequest.status == status)
        if breakdown_type:
            conditions.append(DepannageRequest.breakdown_type == breakdown_type)
        if user_id:
            conditions.append(DepannageRequest.user_id == user_id)
        if is_active is not None:
            conditions.append(DepannageRequest.is_active == is_active)
        if date_from:
            conditions.append(DepannageRequest.created_at >= date_from)
        if date_to:
            conditions.append(DepannageRequest.created_at <= date_to)
        if search:
            conditions.append(
                or_(
                    DepannageRequest.full_name.ilike(f"%{search}%"),
                    DepannageRequest.phone.ilike(f"%{search}%"),
                    DepannageRequest.license_plate.ilike(f"%{search}%"),
                    DepannageRequest.breakdown_type.ilike(f"%{search}%"),
                    DepannageRequest.location_address.ilike(f"%{search}%")
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        result = await self.db.execute(stmt)
        return result.scalar()
    
    async def update(self, request_id: str, update_data: dict) -> Optional[DepannageRequest]:
        """Update a Depannage request."""
        update_data['updated_at'] = datetime.utcnow()
        
        stmt = select(DepannageRequest).where(DepannageRequest.id == request_id)
        result = await self.db.execute(stmt)
        depannage_request = result.scalar_one_or_none()
        
        if depannage_request:
            for key, value in update_data.items():
                if hasattr(depannage_request, key):
                    setattr(depannage_request, key, value)
            await self.db.flush()
        
        return depannage_request
    
    async def delete(self, request_id: str) -> bool:
        """Delete a Depannage request."""
        stmt = select(DepannageRequest).where(DepannageRequest.id == request_id)
        result = await self.db.execute(stmt)
        depannage_request = result.scalar_one_or_none()
        
        if depannage_request:
            await self.db.delete(depannage_request)
            await self.db.flush()
            return True
        
        return False
    
    async def get_pending_requests(self, limit: int = 100) -> List[DepannageRequest]:
        """Get all pending Depannage requests."""
        return await self.get_all(status="en attente", is_active=True, limit=limit)
    
    async def get_recent_requests(self, limit: int = 10) -> List[DepannageRequest]:
        """Get recent Depannage requests."""
        return await self.get_all(limit=limit)
    
    async def get_stats(self) -> dict:
        """Get Depannage request statistics."""
        # Count by status
        stmt_total = select(func.count(DepannageRequest.id))
        stmt_pending = select(func.count(DepannageRequest.id)).where(DepannageRequest.status == 'en attente')
        stmt_in_progress = select(func.count(DepannageRequest.id)).where(DepannageRequest.status == 'en cours')
        stmt_resolved = select(func.count(DepannageRequest.id)).where(DepannageRequest.status == 'résolu')
        stmt_cancelled = select(func.count(DepannageRequest.id)).where(DepannageRequest.status == 'annulé')
        
        # Execute count queries
        total_result = await self.db.execute(stmt_total)
        pending_result = await self.db.execute(stmt_pending)
        in_progress_result = await self.db.execute(stmt_in_progress)
        resolved_result = await self.db.execute(stmt_resolved)
        cancelled_result = await self.db.execute(stmt_cancelled)
        
                
        # Count by status
        stmt_status = select(
            DepannageRequest.status,
            func.count(DepannageRequest.id)
        ).where(DepannageRequest.is_active == True).group_by(DepannageRequest.status)
        
        status_result = await self.db.execute(stmt_status)
        requests_by_status = {row[0]: row[1] for row in status_result.all()}
        
        # Count by breakdown type
        stmt_breakdown = select(
            DepannageRequest.breakdown_type,
            func.count(DepannageRequest.id)
        ).where(DepannageRequest.is_active == True).group_by(DepannageRequest.breakdown_type)
        
        breakdown_result = await self.db.execute(stmt_breakdown)
        requests_by_breakdown_type = {row[0]: row[1] for row in breakdown_result.all()}
        
        return {
            "total_requests": total_result.scalar(),
            "pending_requests": pending_result.scalar(),
            "in_progress_requests": in_progress_result.scalar(),
            "resolved_requests": resolved_result.scalar(),
            "cancelled_requests": cancelled_result.scalar(),
            "requests_by_status": requests_by_status,
            "requests_by_breakdown_type": requests_by_breakdown_type
        }
