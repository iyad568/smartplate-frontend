"""
Order repository for database operations - matching PlaqueStandard.jsx form data.
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderSearch


class OrderRepository:
    """Repository for Order database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, order_data: dict) -> Order:
        """Create a new order."""
        # Generate unique ID and timestamps
        order_data['id'] = str(uuid4())
        order_data['created_at'] = datetime.utcnow()
        order_data['updated_at'] = datetime.utcnow()
        
        # Create order
        order = Order(**order_data)
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get an order by ID."""
        stmt = select(Order).where(Order.id == order_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str) -> List[Order]:
        """Get all orders for a user."""
        stmt = select(Order).where(Order.user_id == user_id).order_by(desc(Order.created_at))
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_by_plate(self, plate: str) -> Optional[Order]:
        """Get an order by plate number."""
        stmt = select(Order).where(Order.plate == plate.upper())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        search: Optional[OrderSearch] = None,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[Order], int]:
        """Get all orders with optional search and pagination."""
        # Build base query
        stmt = select(Order)
        count_stmt = select(func.count(Order.id))
        
        # Apply filters
        conditions = []
        
        if search:
            if search.query:
                conditions.append(
                    or_(
                        Order.plate.ilike(f"%{search.query}%"),
                        Order.name.ilike(f"%{search.query}%"),
                        Order.email.ilike(f"%{search.query}%"),
                        Order.chassis.ilike(f"%{search.query}%")
                    )
                )
            
            if search.user_id:
                conditions.append(Order.user_id == search.user_id)
            
            if search.order_type:
                conditions.append(Order.order_type == search.order_type)
            
            if search.plate_type:
                conditions.append(Order.plate_type == search.plate_type)
            
            if search.status:
                conditions.append(Order.status == search.status)
            
            if search.payment_status:
                conditions.append(Order.payment_status == search.payment_status)
            
            if search.plate:
                conditions.append(Order.plate == search.plate.upper())
            
            if search.created_after:
                conditions.append(Order.created_at >= search.created_after)
            
            if search.created_before:
                conditions.append(Order.created_at <= search.created_before)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))
        
        # Order by created_at desc
        stmt = stmt.order_by(desc(Order.created_at))
        
        # Apply pagination
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)
        
        # Execute queries
        result = await self.db.execute(stmt)
        orders = result.scalars().all()
        
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return orders, total
    
    async def update(self, order_id: str, update_data: dict) -> Optional[Order]:
        """Update an order."""
        update_data['updated_at'] = datetime.utcnow()
        
        stmt = select(Order).where(Order.id == order_id)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if order:
            for key, value in update_data.items():
                setattr(order, key, value)
            
            await self.db.commit()
            await self.db.refresh(order)
        
        return order
    
    async def delete(self, order_id: str) -> bool:
        """Delete an order."""
        stmt = select(Order).where(Order.id == order_id)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if order:
            await self.db.delete(order)
            await self.db.commit()
            return True
        
        return False
    
    async def get_stats(self, user_id: Optional[str] = None) -> dict:
        """Get order statistics."""
        # Build base conditions
        conditions = []
        if user_id:
            conditions.append(Order.user_id == user_id)
        
        # Total orders
        total_stmt = select(func.count(Order.id))
        if conditions:
            total_stmt = total_stmt.where(and_(*conditions))
        total_result = await self.db.execute(total_stmt)
        total_orders = total_result.scalar() or 0
        
        # Orders by status
        status_stmt = select(Order.status, func.count(Order.id))
        if conditions:
            status_stmt = status_stmt.where(and_(*conditions))
        status_stmt = status_stmt.group_by(Order.status)
        status_result = await self.db.execute(status_stmt)
        orders_by_status = dict(status_result.all())
        
        # Orders by plate type
        plate_type_stmt = select(Order.plate_type, func.count(Order.id))
        if conditions:
            plate_type_stmt = plate_type_stmt.where(and_(*conditions))
        plate_type_stmt = plate_type_stmt.group_by(Order.plate_type)
        plate_type_result = await self.db.execute(plate_type_stmt)
        orders_by_plate_type = dict(plate_type_result.all())
        
        # Total revenue (from completed orders)
        revenue_stmt = select(func.sum(Order.total_price))
        revenue_conditions = conditions + [Order.status == 'completed', Order.payment_status == 'paid']
        if revenue_conditions:
            revenue_stmt = revenue_stmt.where(and_(*revenue_conditions))
        revenue_result = await self.db.execute(revenue_stmt)
        total_revenue = float(revenue_result.scalar() or 0)
        
        return {
            'total_orders': total_orders,
            'pending_orders': orders_by_status.get('pending', 0),
            'processing_orders': orders_by_status.get('processing', 0),
            'completed_orders': orders_by_status.get('completed', 0),
            'cancelled_orders': orders_by_status.get('cancelled', 0),
            'paid_orders': orders_by_status.get('paid', 0),
            'total_revenue': total_revenue,
            'orders_by_plate_type': orders_by_plate_type,
            'orders_by_status': orders_by_status
        }
