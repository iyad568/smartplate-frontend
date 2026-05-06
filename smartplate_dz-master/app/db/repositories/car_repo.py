"""
Repository for Car database operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.car import Car


class CarRepository:
    """Repository for Car database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, car_data: dict) -> Car:
        """Create a new car."""
        # Generate unique ID and QR code
        car_data['id'] = str(uuid4())
        car_data['qr_code'] = f"QR-{car_data['plate_number'].upper()}-{car_data['id'][:8]}"
        car_data['created_at'] = datetime.utcnow()
        car_data['updated_at'] = datetime.utcnow()
        
        car = Car(**car_data)
        self.db.add(car)
        await self.db.flush()
        return car
    
    async def get_by_id(self, car_id: str) -> Optional[Car]:
        """Get a car by ID."""
        stmt = select(Car).where(Car.id == car_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_plate_number(self, plate_number: str) -> Optional[Car]:
        """Get a car by plate number."""
        stmt = select(Car).where(Car.plate_number == plate_number.upper())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_qr_code(self, qr_code: str) -> Optional[Car]:
        """Get a car by QR code."""
        stmt = select(Car).where(Car.qr_code == qr_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
        
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> List[Car]:
        """Get cars with optional filters."""
        stmt = select(Car)
        
        # Apply filters
        conditions = []
        
        if user_id:
            conditions.append(Car.user_id == user_id)
        if status:
            conditions.append(Car.status == status)
        if is_active is not None:
            conditions.append(Car.is_active == is_active)
        if date_from:
            conditions.append(Car.created_at >= date_from)
        if date_to:
            conditions.append(Car.created_at <= date_to)
        if search:
            conditions.append(
                or_(
                    Car.plate_number.ilike(f"%{search}%"),
                    Car.qr_code.ilike(f"%{search}%")
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Apply ordering and pagination
        stmt = stmt.order_by(Car.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def count(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> int:
        """Count cars with optional filters."""
        stmt = select(func.count(Car.id))
        
        # Apply filters (same as get_all)
        conditions = []
        
        if user_id:
            conditions.append(Car.user_id == user_id)
        if status:
            conditions.append(Car.status == status)
        if is_active is not None:
            conditions.append(Car.is_active == is_active)
        if date_from:
            conditions.append(Car.created_at >= date_from)
        if date_to:
            conditions.append(Car.created_at <= date_to)
        if search:
            conditions.append(
                or_(
                    Car.plate_number.ilike(f"%{search}%"),
                    Car.qr_code.ilike(f"%{search}%")
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        result = await self.db.execute(stmt)
        return result.scalar()
    
    async def update(self, car_id: str, update_data: dict) -> Optional[Car]:
        """Update a car."""
        update_data['updated_at'] = datetime.utcnow()
        
        stmt = select(Car).where(Car.id == car_id)
        result = await self.db.execute(stmt)
        car = result.scalar_one_or_none()
        
        if car:
            for key, value in update_data.items():
                if hasattr(car, key):
                    setattr(car, key, value)
            await self.db.flush()
        
        return car
    
    async def delete(self, car_id: str) -> bool:
        """Delete a car."""
        stmt = select(Car).where(Car.id == car_id)
        result = await self.db.execute(stmt)
        car = result.scalar_one_or_none()
        
        if car:
            await self.db.delete(car)
            await self.db.flush()
            return True
        
        return False
    
    async def get_user_cars(self, user_id: str, limit: int = 100) -> List[Car]:
        """Get all cars for a specific user."""
        return await self.get_all(user_id=user_id, limit=limit)
    
    async def get_recent_cars(self, limit: int = 10) -> List[Car]:
        """Get recent cars."""
        return await self.get_all(limit=limit)
    
        
    async def get_stats(self, user_id: Optional[str] = None) -> dict:
        """Get car statistics."""
        # Base conditions
        base_conditions = []
        if user_id:
            base_conditions.append(Car.user_id == user_id)
        
        # Count total cars
        stmt_total = select(func.count(Car.id))
        
        # Apply base conditions
        if base_conditions:
            stmt_total = stmt_total.where(and_(*base_conditions))
        
        # Execute count query
        total_result = await self.db.execute(stmt_total)
        
        return {
            "total_cars": total_result.scalar()
        }
