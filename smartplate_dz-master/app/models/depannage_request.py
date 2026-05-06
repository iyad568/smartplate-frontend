"""
Depannage Request model for SmartPlate roadside assistance system.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class DepannageRequest(Base):
    """Depannage roadside assistance request model."""
    __tablename__ = "depannage_requests"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    
    # User information
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Request details
    license_plate: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    breakdown_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    location_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gps_coordinates: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status and management
    status: Mapped[str] = mapped_column(
        String(20), 
        default="en attente", 
        nullable=False, 
        index=True
    )  # en attente, en cours, résolu, annulé
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Properties for status checking
    @property
    def is_pending(self) -> bool:
        """Check if request is en attente."""
        return self.status == "en attente"
    
    @property
    def is_in_progress(self) -> bool:
        """Check if request is en cours."""
        return self.status == "en cours"
    
    @property
    def is_resolved(self) -> bool:
        """Check if request is résolu."""
        return self.status == "résolu"
    
    @property
    def is_cancelled(self) -> bool:
        """Check if request is annulé."""
        return self.status == "annulé"
    
    @property
    def can_be_claimed(self) -> bool:
        """Check if request can be claimed."""
        return self.status == "en attente" and self.is_active
    
    @property
    def can_be_resolved(self) -> bool:
        """Check if request can be resolved."""
        return self.status in ["en cours"] and self.is_active
    
    @property
    def waiting_time_minutes(self) -> int:
        """Calculate waiting time in minutes."""
        return int((datetime.utcnow() - self.created_at).total_seconds() / 60)
