"""
Pydantic schemas for Car API requests and responses.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.car import Car


class CarBase(BaseModel):
    """Base schema for Car with common fields."""
    plate_number: str = Field(..., min_length=5, max_length=20, description="License plate number")
    plate_photo_url: Optional[str] = Field(None, description="URL to plate photo")
    assurance_paper_url: Optional[str] = Field(None, description="URL to assurance paper")
    license_url: Optional[str] = Field(None, description="URL to driver license")
    status: str = Field(default="active", description="Car status")
    
    # Vehicle information
    chassis_number: Optional[str] = Field(None, description="Vehicle chassis number")
    vehicle_type: Optional[str] = Field(None, description="Vehicle type")
    vehicle_brand: Optional[str] = Field(None, description="Vehicle brand")
    power_type: Optional[str] = Field(None, description="Power type (essence/diesel)")
    
    # Owner information (from PlaqueStandard form)
    cni_number: Optional[str] = Field(None, description="CNI/ID number")
    owner_address: Optional[str] = Field(None, description="Owner address")
    owner_name: Optional[str] = Field(None, description="Owner full name")
    owner_first_name: Optional[str] = Field(None, description="Owner first name")
    owner_phone: Optional[str] = Field(None, description="Owner phone")
    owner_email: Optional[str] = Field(None, description="Owner email")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ["active", "not_active"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @validator('plate_number')
    def validate_plate_number(cls, v):
        # Basic plate number validation - can be customized based on country requirements
        if v and len(v.strip()) < 5:
            raise ValueError("Plate number must be at least 5 characters")
        return v.strip().upper() if v else v


class CarCreate(BaseModel):
    """Schema for creating a new car from PlaqueStandard form."""
    # Required fields
    plate_number: str = Field(..., min_length=5, max_length=20, description="License plate number")
    
    # Vehicle information (from PlaqueStandard form)
    chassis_number: Optional[str] = Field(None, description="Vehicle chassis number")
    vehicle_type: Optional[str] = Field(None, description="Vehicle type")
    vehicle_brand: Optional[str] = Field(None, description="Vehicle brand")
    power_type: str = Field(default="essence", description="Power type (essence/diesel)")
    
    # Owner information (from PlaqueStandard form)
    cni_number: Optional[str] = Field(None, description="CNI/ID number")
    owner_address: Optional[str] = Field(None, description="Owner address")
    owner_name: Optional[str] = Field(None, description="Owner full name")
    owner_first_name: Optional[str] = Field(None, description="Owner first name")
    owner_phone: Optional[str] = Field(None, description="Owner phone")
    owner_email: Optional[str] = Field(None, description="Owner email")
    
    # Optional document URLs
    plate_photo_url: Optional[str] = Field(None, description="URL to plate photo")
    assurance_paper_url: Optional[str] = Field(None, description="URL to assurance paper")
    license_url: Optional[str] = Field(None, description="URL to driver license")
    cart_grise_url: Optional[str] = Field(None, description="URL to cart grise (gray card) document")
    
    # Status (default to active)
    status: str = Field(default="active", description="Car status")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ["active", "not_active"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @validator('plate_number')
    def validate_plate_number(cls, v):
        if len(v.strip()) < 5:
            raise ValueError("Plate number must be at least 5 characters")
        return v.strip().upper()
    
    class Config:
        from_attributes = True


class CarUpdate(BaseModel):
    """Schema for updating a car (all fields optional)."""
    plate_photo_url: Optional[str] = Field(None, description="URL to plate photo")
    assurance_paper_url: Optional[str] = Field(None, description="URL to assurance paper")
    license_url: Optional[str] = Field(None, description="URL to driver license")
    status: Optional[str] = Field(None, description="Car status")
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["active", "not_active"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class CarResponse(BaseModel):
    """Schema for car response."""
    id: str
    user_id: str
    qr_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Vehicle information
    plate_number: str
    chassis_number: Optional[str]
    vehicle_type: Optional[str]
    vehicle_brand: Optional[str]
    power_type: Optional[str]
    
    # Owner information
    cni_number: Optional[str]
    owner_address: Optional[str]
    owner_name: Optional[str]
    owner_first_name: Optional[str]
    owner_phone: Optional[str]
    owner_email: Optional[str]
    
    # Document URLs
    plate_photo_url: Optional[str]
    assurance_paper_url: Optional[str]
    license_url: Optional[str]
    cart_grise_url: Optional[str]
    vignette_url: Optional[str]
    controle_technique_url: Optional[str]
    status: str
    
    # Computed properties
    ownership_duration_days: int = Field(description="Ownership duration in days")
    
    class Config:
        from_attributes = True


class CarList(BaseModel):
    """Schema for paginated car list response."""
    cars: List[CarResponse]
    total: int = Field(description="Total number of cars")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")


class CarSearch(BaseModel):
    """Schema for car search parameters."""
    query: Optional[str] = Field(None, description="Search query")
    plate_number: Optional[str] = Field(None, description="Filter by plate number")
    status: Optional[str] = Field(None, description="Filter by status")
    has_complete_documents: Optional[bool] = Field(None, description="Filter by document completion")
    is_complete_profile: Optional[bool] = Field(None, description="Filter by profile completion")
    date_from: Optional[datetime] = Field(None, description="Filter cars from this date")
    date_to: Optional[datetime] = Field(None, description="Filter cars to this date")
    is_active: Optional[bool] = Field(None, description="Filter by active status")


class CarStats(BaseModel):
    """Schema for car statistics."""
    total_cars: int


class DashboardData(BaseModel):
    """Schema for car dashboard data."""
    stats: CarStats
    recent_cars: List[CarResponse]
    my_cars: List[CarResponse]  # Cars owned by current user


class QRCodeResponse(BaseModel):
    """Schema for QR code response."""
    qr_code: str = Field(description="QR code data/URL")
    plate_number: str = Field(description="Associated plate number")
    generated_at: datetime = Field(description="QR code generation timestamp")
    
    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    car_id: str
    document_type: str = Field(description="Type of document uploaded")
    document_url: str = Field(description="URL to uploaded document")
    upload_timestamp: datetime = Field(description="Document upload timestamp")
    message: str = Field(description="Upload confirmation message")
    
    class Config:
        from_attributes = True
