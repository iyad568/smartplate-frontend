"""
Order model for SmartPlate order management system - matching PlaqueStandard.jsx form data.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Order(Base):
    """Order model for SmartPlate order management."""
    __tablename__ = "orders"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    
    # Foreign key to user
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Order information
    order_type: Mapped[str] = mapped_column(String(20), nullable=False, default="plate_order")  # plate_order, product_order, service_order
    plate_type: Mapped[str] = mapped_column(String(20), nullable=False)  # standard, commercial, special
    
    # Order details
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="DZD")
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, processing, completed, cancelled
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, paid, failed
    
    # Document uploads
    cart_grise_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Cart grise (gray card) upload URL
    
    # Exact fields from PlaqueStandard.jsx form
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # owner full name
    first: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # owner first name
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # owner phone
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # owner email
    cni: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # CNI/ID number
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # owner address
    chassis: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # vehicle chassis number
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # vehicle type
    brand: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # vehicle brand
    plate: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # license plate number
    power: Mapped[str] = mapped_column(String(20), nullable=False, default="essence")  # power type (essence/diesel)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    
    def __repr__(self) -> str:
        """String representation of Order model."""
        return f"<Order(id='{self.id}', user_id='{self.user_id}', plate_type='{self.plate_type}', status='{self.status}')>"
    
    @property
    def is_pending(self) -> bool:
        """Check if order is pending."""
        return self.status == "pending"
    
    @property
    def is_processing(self) -> bool:
        """Check if order is processing."""
        return self.status == "processing"
    
    @property
    def is_completed(self) -> bool:
        """Check if order is completed."""
        return self.status == "completed"
    
    @property
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.status == "cancelled"
    
    @property
    def is_paid(self) -> bool:
        """Check if payment is completed."""
        return self.payment_status == "paid"
    
    @property
    def payment_pending(self) -> bool:
        """Check if payment is pending."""
        return self.payment_status == "pending"
    
    @property
    def payment_failed(self) -> bool:
        """Check if payment failed."""
        return self.payment_status == "failed"
    
    def mark_as_processing(self):
        """Mark order as processing."""
        self.status = "processing"
        self.processed_at = datetime.utcnow()
    
    def mark_as_completed(self):
        """Mark order as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
    
    def mark_as_cancelled(self):
        """Mark order as cancelled."""
        self.status = "cancelled"
    
    def mark_payment_as_paid(self):
        """Mark payment as paid."""
        self.payment_status = "paid"
    
    def mark_payment_as_failed(self):
        """Mark payment as failed."""
        self.payment_status = "failed"
    
    def get_car_data(self) -> dict:
        """Get car data from order for Step 2 car creation."""
        return {
            'plate_number': self.plate,
            'chassis_number': self.chassis,
            'vehicle_type': self.type,
            'vehicle_brand': self.brand,
            'power_type': self.power,
            'cni_number': self.cni,
            'owner_address': self.address,
            'status': 'active'
        }
