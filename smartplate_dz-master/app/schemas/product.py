"""
Pydantic schemas for Product API requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator
from app.models.product import Product


class ProductBase(BaseModel):
    """Base schema for Product with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    price: float = Field(..., gt=0, description="Selling price")
    cost_price: Optional[float] = Field(None, ge=0, description="Cost price")
    stock_quantity: int = Field(default=0, ge=0, description="Current stock quantity")
    min_stock_level: int = Field(default=0, ge=0, description="Minimum stock level")
    is_active: bool = Field(default=True, description="Whether product is active")
    image_url: Optional[str] = Field(None, description="Product image URL")

    @validator('price', 'cost_price')
    def validate_prices(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    image_url: Optional[str] = None

    @validator('price', 'cost_price')
    def validate_prices(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_in_stock: bool = Field(description="Whether product is in stock")
    is_low_stock: bool = Field(description="Whether product stock is low")

    class Config:
        from_attributes = True


class ProductList(BaseModel):
    """Schema for paginated product list response."""
    products: list[ProductResponse]
    total: int = Field(description="Total number of products")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")


class ProductSearch(BaseModel):
    """Schema for product search parameters."""
    query: Optional[str] = Field(None, description="Search query")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    in_stock: Optional[bool] = Field(None, description="Filter by stock availability")
    low_stock: Optional[bool] = Field(None, description="Filter by low stock items")


class StockUpdate(BaseModel):
    """Schema for updating product stock."""
    quantity: int = Field(..., description="New stock quantity")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for stock update")


class BulkStockUpdate(BaseModel):
    """Schema for bulk stock updates."""
    updates: list[dict] = Field(..., description="List of product updates")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for bulk update")


class ProductStats(BaseModel):
    """Schema for product statistics."""
    total_products: int
    active_products: int
    inactive_products: int
    low_stock_products: int
    out_of_stock_products: int
    total_value: float


