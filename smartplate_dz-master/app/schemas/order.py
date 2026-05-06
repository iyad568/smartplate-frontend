"""
Pydantic schemas for Order API requests and responses - matching PlaqueStandard.jsx form data.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

# Remove circular import
# from app.models.order import Order


class OrderBase(BaseModel):
    """Base schema for Order with common fields - matching PlaqueStandard.jsx form."""
    order_type: str = Field(default="plate_order", description="Type of order: plate_order, product_order, service_order")
    plate_type: str = Field(description="Type of plate: standard, commercial, special")
    total_price: float = Field(default=0.00, ge=0, description="Total price of the order")
    currency: str = Field(default="DZD", description="Currency code")
    
    # Exact fields from PlaqueStandard.jsx form
    name: Optional[str] = Field(None, description="Owner full name")
    first: Optional[str] = Field(None, description="Owner first name")
    phone: Optional[str] = Field(None, description="Owner phone number")
    email: Optional[str] = Field(None, description="Owner email address")
    cni: Optional[str] = Field(None, description="CNI/ID number")
    address: Optional[str] = Field(None, description="Owner address")
    chassis: Optional[str] = Field(None, description="Vehicle chassis number")
    type: Optional[str] = Field(None, description="Vehicle type")
    brand: Optional[str] = Field(None, description="Vehicle brand")
    plate: Optional[str] = Field(None, description="License plate number")
    power: str = Field(default="essence", description="Power type (essence/diesel)")
    
    # Document uploads
    cart_grise_url: Optional[str] = Field(None, description="Cart grise (gray card) upload URL")
    
    # Simplify validators to avoid issues
    @validator('order_type', pre=True, always=True)
    def validate_order_type(cls, v):
        if not v:
            return "plate_order"
        allowed_types = ["plate_order", "product_order", "service_order"]
        if v not in allowed_types:
            raise ValueError(f"Order type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('plate_type', pre=True, always=True)
    def validate_plate_type(cls, v):
        if not v or v == "string":
            return "standard"
        allowed_types = ["standard", "silver", "gold"]
        if v not in allowed_types:
            raise ValueError(f"Plate type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('plate')
    def validate_plate_number(cls, v):
        if not v or v == "string":
            return None
        if len(v.strip()) < 5:
            raise ValueError("Plate number must be at least 5 characters")
        return v.strip().upper() if v else v


class OrderCreate(OrderBase):
    """Schema for creating a new order (user_id auto-populated from current user)."""
    pass


class OrderUpdate(BaseModel):
    """Schema for updating an order (all fields optional)."""
    order_type: Optional[str] = Field(None, description="Type of order")
    plate_type: Optional[str] = Field(None, description="Type of plate")
    total_price: Optional[float] = Field(None, ge=0, description="Total price of the order")
    currency: Optional[str] = Field(None, description="Currency code")
    status: Optional[str] = Field(None, description="Order status")
    payment_status: Optional[str] = Field(None, description="Payment status")
    
    # PlaqueStandard form fields
    name: Optional[str] = Field(None, description="Owner full name")
    first: Optional[str] = Field(None, description="Owner first name")
    phone: Optional[str] = Field(None, description="Owner phone number")
    email: Optional[str] = Field(None, description="Owner email address")
    cni: Optional[str] = Field(None, description="CNI/ID number")
    address: Optional[str] = Field(None, description="Owner address")
    chassis: Optional[str] = Field(None, description="Vehicle chassis number")
    type: Optional[str] = Field(None, description="Vehicle type")
    brand: Optional[str] = Field(None, description="Vehicle brand")
    plate: Optional[str] = Field(None, description="License plate number")
    power: Optional[str] = Field(None, description="Power type")


class OrderResponse(OrderBase):
    """Schema for order response including system fields."""
    id: str = Field(description="Order ID")
    user_id: str = Field(description="User ID")
    status: str = Field(description="Order status")
    payment_status: str = Field(description="Payment status")
    created_at: datetime = Field(description="Order creation timestamp")
    updated_at: datetime = Field(description="Order last update timestamp")
    processed_at: Optional[datetime] = Field(None, description="Order processing timestamp")
    completed_at: Optional[datetime] = Field(None, description="Order completion timestamp")
    cart_grise_url: Optional[str] = Field(None, description="Cart grise (gray card) upload URL")
    
    class Config:
        from_attributes = True


class OrderSearch(BaseModel):
    """Schema for order search parameters."""
    query: Optional[str] = Field(None, description="Search query")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    order_type: Optional[str] = Field(None, description="Filter by order type")
    plate_type: Optional[str] = Field(None, description="Filter by plate type")
    status: Optional[str] = Field(None, description="Filter by status")
    payment_status: Optional[str] = Field(None, description="Filter by payment status")
    plate: Optional[str] = Field(None, description="Filter by plate number")
    created_after: Optional[datetime] = Field(None, description="Filter orders created after this date")
    created_before: Optional[datetime] = Field(None, description="Filter orders created before this date")


class OrderList(BaseModel):
    """Schema for order list response."""
    orders: list[OrderResponse] = Field(description="List of orders")
    total: int = Field(description="Total number of orders")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Number of orders per page")
    total_pages: int = Field(description="Total number of pages")


class OrderStats(BaseModel):
    """Schema for order statistics."""
    total_orders: int = Field(description="Total number of orders")
    pending_orders: int = Field(description="Number of pending orders")
    processing_orders: int = Field(description="Number of processing orders")
    completed_orders: int = Field(description="Number of completed orders")
    cancelled_orders: int = Field(description="Number of cancelled orders")
    paid_orders: int = Field(description="Number of paid orders")
    total_revenue: float = Field(description="Total revenue from completed orders")
    orders_by_plate_type: Dict[str, int] = Field(description="Orders count by plate type")
    orders_by_status: Dict[str, int] = Field(description="Orders count by status")
