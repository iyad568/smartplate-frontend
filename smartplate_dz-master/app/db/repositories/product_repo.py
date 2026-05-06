"""
Repository for Product database operations.
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product


class ProductRepository:
    """Repository for Product model operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, product_data: dict) -> Product:
        """Create a new product."""
        product = Product(**product_data)
        self.db.add(product)
        await self.db.flush()
        return product
    
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get a product by ID."""
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
        
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None
    ) -> List[Product]:
        """Get all products with optional filters."""
        stmt = select(Product)
        
        # Apply filters
        conditions = []
        
        if is_active is not None:
            conditions.append(Product.is_active == is_active)
        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)
        if search:
            conditions.append(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Apply pagination and ordering
        stmt = stmt.order_by(Product.name).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def count(
        self,
        is_active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None
    ) -> int:
        """Count products with optional filters."""
        stmt = select(func.count(Product.id))
        
        # Apply filters (same as get_all)
        conditions = []
        
        if is_active is not None:
            conditions.append(Product.is_active == is_active)
        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)
        if search:
            conditions.append(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        result = await self.db.execute(stmt)
        return result.scalar()
    
    async def update(self, product_id: UUID, update_data: dict) -> Optional[Product]:
        """Update a product."""
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if product:
            for field, value in update_data.items():
                setattr(product, field, value)
            await self.db.flush()
        
        return product
    
    async def delete(self, product_id: UUID) -> bool:
        """Delete a product."""
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if product:
            await self.db.delete(product)
            return True
        return False
    
    async def get_low_stock_products(self, limit: int = 100) -> List[Product]:
        """Get products with low stock."""
        stmt = select(Product).where(
            and_(
                Product.stock_quantity <= Product.min_stock_level,
                Product.stock_quantity > 0
            )
        ).order_by(Product.stock_quantity).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_out_of_stock_products(self, limit: int = 100) -> List[Product]:
        """Get products that are out of stock."""
        stmt = select(Product).where(
            Product.stock_quantity == 0
        ).order_by(Product.name).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
        
    async def get_stats(self) -> dict:
        """Get product statistics."""
        stmt_total = select(func.count(Product.id))
        stmt_active = select(func.count(Product.id)).where(Product.is_active == True)
        stmt_inactive = select(func.count(Product.id)).where(Product.is_active == False)
        stmt_low_stock = select(func.count(Product.id)).where(
            and_(
                Product.stock_quantity <= Product.min_stock_level,
                Product.stock_quantity > 0
            )
        )
        stmt_out_of_stock = select(func.count(Product.id)).where(Product.stock_quantity == 0)
        stmt_total_value = select(func.sum(Product.price * Product.stock_quantity))
        
        # Execute all queries
        total_result = await self.db.execute(stmt_total)
        active_result = await self.db.execute(stmt_active)
        inactive_result = await self.db.execute(stmt_inactive)
        low_stock_result = await self.db.execute(stmt_low_stock)
        out_of_stock_result = await self.db.execute(stmt_out_of_stock)
        total_value_result = await self.db.execute(stmt_total_value)
        
        return {
            "total_products": total_result.scalar(),
            "active_products": active_result.scalar(),
            "inactive_products": inactive_result.scalar(),
            "low_stock_products": low_stock_result.scalar(),
            "out_of_stock_products": out_of_stock_result.scalar(),
            "total_value": float(total_value_result.scalar() or 0)
        }
    
    
