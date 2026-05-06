"""
Product model for SmartPlate products management.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Numeric, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Product(Base):
    """Product model representing items in the SmartPlate system."""
    
    __tablename__ = "products"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pricing
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cost_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Inventory
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_stock_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    
    # Media
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"
    
    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.stock_quantity > self.min_stock_level
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product stock is below minimum level."""
        return self.stock_quantity <= self.min_stock_level and self.stock_quantity > 0
