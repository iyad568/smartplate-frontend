"""
Pydantic schemas for Depannage request API requests and responses.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.depannage_request import DepannageRequest


class DepannageRequestBase(BaseModel):
    """Base schema for Depannage request."""
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name of person requesting assistance")
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number")
    license_plate: str = Field(..., min_length=1, max_length=50, description="License plate number")
    breakdown_type: str = Field(..., description="Type of breakdown")
    location_address: Optional[str] = Field(None, max_length=500, description="Location address")
    gps_coordinates: Optional[str] = Field(None, max_length=100, description="GPS coordinates")
    additional_notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    @validator('breakdown_type')
    def validate_breakdown_type(cls, v):
        allowed_types = ["Batterie", "Pneu crevé", "Moteur", "Autre"]
        if v not in allowed_types:
            raise ValueError(f"Breakdown type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if len(v) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        return v


class DepannageRequestCreate(DepannageRequestBase):
    """Schema for creating a new Depannage request."""
    user_id: str = Field(..., description="User ID")
    
    class Config:
        from_attributes = True


class DepannageRequestForm(DepannageRequestBase):
    """Schema for Depannage form submission by any authenticated user."""
    
    class Config:
        from_attributes = True


class DepannageRequestUpdate(BaseModel):
    """Schema for updating a Depannage request (all fields optional)."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    license_plate: Optional[str] = Field(None, min_length=1, max_length=50)
    breakdown_type: Optional[str] = Field(None)
    location_address: Optional[str] = Field(None, max_length=500)
    gps_coordinates: Optional[str] = Field(None, max_length=100)
    additional_notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    
    @validator('breakdown_type')
    def validate_breakdown_type(cls, v):
        if v is not None:
            allowed_types = ["Batterie", "Pneu crevé", "Moteur", "Autre"]
            if v not in allowed_types:
                raise ValueError(f"Breakdown type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["en attente", "en cours", "résolu", "annulé"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and len(v) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        return v


class DepannageRequestResponse(DepannageRequestBase):
    """Schema for Depannage request response."""
    id: str
    user_id: str
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    waiting_time_minutes: int = Field(description="Waiting time in minutes")
    can_be_claimed: bool = Field(description="Whether request can be claimed")
    can_be_resolved: bool = Field(description="Whether request can be resolved")
    
    class Config:
        from_attributes = True


class DepannageRequestList(BaseModel):
    """Schema for paginated Depannage request list response."""
    requests: List[DepannageRequestResponse]
    total: int = Field(description="Total number of requests")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")


class DepannageRequestSearch(BaseModel):
    """Schema for Depannage request search parameters."""
    query: Optional[str] = Field(None, description="Search query")
    status: Optional[str] = Field(None, description="Filter by status")
    breakdown_type: Optional[str] = Field(None, description="Filter by breakdown type")
    license_plate: Optional[str] = Field(None, description="Filter by license plate")
    phone: Optional[str] = Field(None, description="Filter by phone")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    date_from: Optional[datetime] = Field(None, description="Filter requests from this date")
    date_to: Optional[datetime] = Field(None, description="Filter requests to this date")
    is_active: Optional[bool] = Field(None, description="Filter by active status")


class DepannageStats(BaseModel):
    """Schema for Depannage request statistics."""
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    resolved_requests: int
    cancelled_requests: int
    requests_by_status: dict[str, int] = Field(description="Request count by status")
    requests_by_breakdown_type: dict[str, int] = Field(description="Request count by breakdown type")


class DashboardData(BaseModel):
    """Schema for Depannage dashboard data."""
    stats: DepannageStats
    recent_requests: List[DepannageRequestResponse]
    pending_requests: List[DepannageRequestResponse]


class OperatorInfo(BaseModel):
    """Schema for operator information."""
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    
    class Config:
        from_attributes = True
