"""
Car model for SmartPlate vehicle management system.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.session import Base


class Car(Base):
    """Car model for SmartPlate vehicle management."""
    __tablename__ = "cars"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    
    # Foreign key to user
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Plate information
    plate_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    qr_code: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  # QR code URL/data
    plate_photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # URL to plate photo
    
    # Vehicle information
    chassis_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Vehicle chassis number
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Vehicle type
    vehicle_brand: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Vehicle brand
    power_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Power type (essence/diesel)
    
    # Owner information (from PlaqueStandard form)
    cni_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # CNI/ID number
    owner_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Owner address
    owner_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Owner full name
    owner_first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Owner first name
    owner_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Owner phone
    owner_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Owner email
    
    # Document URLs
    assurance_paper_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # URL to assurance paper
    license_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # URL to driver license
    vignette_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # URL to vignette document
    controle_technique_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # URL to contrôle technique document
    cart_grise_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # URL to cart grise (gray card) document
    
    # Status and metadata
    status: Mapped[str] = mapped_column(
        String(20), 
        default="active", 
        nullable=False, 
        index=True
    )  # active, not_active
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cars")
    
    # Properties for status checking
    @hybrid_property
    def is_active_status(self) -> bool:
        """Check if car status is active."""
        return self.status == "active"
    
    @hybrid_property
    def is_not_active_status(self) -> bool:
        """Check if car status is not_active."""
        return self.status == "not_active"
    
        
    @property
    def ownership_duration_days(self) -> int:
        """Calculate ownership duration in days."""
        if self.created_at:
            return int((datetime.utcnow() - self.created_at).total_seconds() / (24 * 3600))
        return 0
    
        
    def __repr__(self) -> str:
        """String representation of Car model."""
        return f"<Car(plate_number='{self.plate_number}', status='{self.status}', user_id='{self.user_id}')>"
