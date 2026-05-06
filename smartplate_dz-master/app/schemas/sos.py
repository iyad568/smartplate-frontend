"""
Pydantic schemas for SOS request API requests and responses.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.sos_request import SOSRequest


class SOSRequestBase(BaseModel):
    """Base schema for SOS request with common fields."""
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name of person requesting help")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    license_plate: str = Field(..., min_length=1, max_length=50, description="License plate number")
    emergency_description: str = Field(..., min_length=10, max_length=2000, description="Description of emergency")
    current_location: Optional[str] = Field(None, max_length=500, description="Current location description")
    gps_coordinates: Optional[str] = Field(None, max_length=100, description="GPS coordinates")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError("Invalid email format")
        return v.lower()


class SOSRequestCreate(SOSRequestBase):
    """Schema for creating a new SOS request (user_id auto-populated from current user)."""
    
    class Config:
        from_attributes = True


class SOSRequestForm(BaseModel):
    """Schema for SOS form submission by any authenticated user."""
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name of person requesting help")
    license_plate: str = Field(..., min_length=1, max_length=50, description="License plate number")
    emergency_description: str = Field(..., min_length=10, max_length=2000, description="Description of emergency")
    current_location: Optional[str] = Field(None, max_length=500, description="Current location description")
    gps_coordinates: Optional[str] = Field(None, max_length=100, description="GPS coordinates")


class SOSRequestUpdate(BaseModel):
    """Schema for updating an SOS request (all fields optional)."""
    emergency_description: Optional[str] = Field(None, min_length=10, max_length=2000)
    current_location: Optional[str] = Field(None, max_length=500)
    gps_coordinates: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None)
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["en attente", "en cours", "résolu", "annulé"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class SOSRequestResponse(SOSRequestBase):
    """Schema for SOS request response."""
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


class SOSRequestList(BaseModel):
    """Schema for paginated SOS request list response."""
    requests: List[SOSRequestResponse]
    total: int = Field(description="Total number of requests")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")


class SOSRequestSearch(BaseModel):
    """Schema for SOS request search parameters."""
    query: Optional[str] = Field(None, description="Search query")
    status: Optional[str] = Field(None, description="Filter by status")
    license_plate: Optional[str] = Field(None, description="Filter by license plate")
    email: Optional[str] = Field(None, description="Filter by email")
    date_from: Optional[datetime] = Field(None, description="Filter requests from this date")
    date_to: Optional[datetime] = Field(None, description="Filter requests to this date")
    is_active: Optional[bool] = Field(None, description="Filter by active status")




class SOSStats(BaseModel):
    """Schema for SOS request statistics."""
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    resolved_requests: int
    cancelled_requests: int
    requests_by_status: dict[str, int] = Field(description="Request count by status")


class DashboardData(BaseModel):
    """Schema for SOS dashboard data."""
    stats: SOSStats
    recent_requests: List[SOSRequestResponse]
    pending_requests: List[SOSRequestResponse]


class OperatorInfo(BaseModel):
    """Schema for operator information."""
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    
    class Config:
        from_attributes = True
