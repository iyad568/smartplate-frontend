"""
Product service for business logic and operations.
"""
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.product_repo import ProductRepository
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductSearch,
    StockUpdate,
    BulkStockUpdate,
    ProductStats
)


class ProductService:
    """Service for Product business operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        # Create product
        product = await self.repo.create(product_data.dict())
        return product
    
    async def get_product(self, product_id: UUID) -> Product:
        """Get a product by ID."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    
        
    async def get_products(
        self,
        page: int = 1,
        size: int = 50,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_active: Optional[bool] = None,
        in_stock: Optional[bool] = None,
        low_stock: Optional[bool] = None
    ) -> tuple[List[Product], int]:
        """Get products with filtering and pagination."""
        # Validate pagination
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 50
        
        skip = (page - 1) * size
        
        # Apply additional filters for stock status
        if in_stock is not None:
            if in_stock:
                # This would require custom query logic
                pass
            else:
                # Out of stock
                pass
        
        if low_stock is not None:
            if low_stock:
                # Low stock items
                pass
        
        products = await self.repo.get_all(
            skip=skip,
            limit=size,
            search=search,
            min_price=min_price,
            max_price=max_price,
            is_active=is_active
        )
        
        total = await self.repo.count(
            search=search,
            min_price=min_price,
            max_price=max_price,
            is_active=is_active
        )
        
        return products, total
    
    async def update_product(self, product_id: UUID, update_data: ProductUpdate) -> Product:
        """Update a product with validation."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        update_dict = update_data.dict(exclude_unset=True)
        
        updated_product = await self.repo.update(product_id, update_dict)
        return updated_product
    
    async def delete_product(self, product_id: UUID) -> bool:
        """Delete a product."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return await self.repo.delete(product_id)
    
    async def update_stock(self, product_id: UUID, stock_update: StockUpdate) -> Product:
        """Update product stock quantity."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        if stock_update.quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock quantity cannot be negative"
            )
        
        await self.repo.update(product_id, {"stock_quantity": stock_update.quantity})
        return await self.repo.get_by_id(product_id)
    
    async def bulk_update_stock(self, bulk_update: BulkStockUpdate) -> List[Product]:
        """Update stock for multiple products."""
        updated_products = []
        errors = []
        
        for update in bulk_update.updates:
            try:
                product_id = update.get("product_id")
                quantity = update.get("quantity")
                
                if not product_id or quantity is None:
                    errors.append(f"Invalid update data: {update}")
                    continue
                
                product = await self.repo.get_by_id(product_id)
                if not product:
                    errors.append(f"Product {product_id} not found")
                    continue
                
                if quantity < 0:
                    errors.append(f"Negative stock for product {product_id}")
                    continue
                
                await self.repo.update(product_id, {"stock_quantity": quantity})
                updated_products.append(product)
                
            except Exception as e:
                errors.append(f"Error updating {update.get('product_id')}: {str(e)}")
        
        if errors and not updated_products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bulk update failed: {'; '.join(errors)}"
            )
        
        return updated_products
    
    async def get_low_stock_products(self, limit: int = 50) -> List[Product]:
        """Get products with low stock."""
        return await self.repo.get_low_stock_products(limit)
    
    async def get_out_of_stock_products(self, limit: int = 50) -> List[Product]:
        """Get products that are out of stock."""
        return await self.repo.get_out_of_stock_products(limit)
    
    async def get_stats(self) -> ProductStats:
        """Get product statistics."""
        stats = await self.repo.get_stats()
        return ProductStats(**stats)
    
    async def search_products(self, search_params: ProductSearch) -> tuple[List[Product], int]:
        """Search products with advanced filters."""
        products = await self.repo.get_all(
            search=search_params.query,
            min_price=search_params.min_price,
            max_price=search_params.max_price,
            is_active=search_params.is_active
        )
        
        # Apply additional filters
        if search_params.in_stock is not None:
            if search_params.in_stock:
                products = [p for p in products if p.is_in_stock]
            else:
                products = [p for p in products if not p.is_in_stock]
        
        if search_params.low_stock is not None:
            if search_params.low_stock:
                products = [p for p in products if p.is_low_stock]
            else:
                products = [p for p in products if not p.is_low_stock]
        
        total = len(products)
        return products, total
