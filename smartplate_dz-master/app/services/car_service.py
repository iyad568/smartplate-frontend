"""
Service for Car business operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.car_repo import CarRepository
from app.schemas.car import (
    CarCreate,
    CarUpdate,
    CarResponse,
    CarList,
    CarSearch,
    CarStats,
    DashboardData,
    QRCodeResponse,
    DocumentUploadResponse
)
from app.models.car import Car


class CarService:
    """Service for Car business operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CarRepository(db)
    
    async def create_car(self, car_data: CarCreate, user_id: str) -> CarResponse:
        """Create a new car for a user."""
        # Check if plate number already exists
        existing_car = await self.repo.get_by_plate_number(car_data.plate_number)
        if existing_car:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plate number {car_data.plate_number} already exists"
            )
        
        # Create car with user_id (QR code generated in repository)
        car_dict = car_data.dict()
        car_dict['user_id'] = user_id
        
        car = await self.repo.create(car_dict)
        return CarResponse.model_validate(car)
    
    async def get_car(self, car_id: str, user_id: Optional[str] = None) -> CarResponse:
        """Get a car by ID."""
        car = await self.repo.get_by_id(car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car not found"
            )
        
        # Check if user has access (if user_id is provided)
        if user_id and car.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return CarResponse.model_validate(car)
    
    async def get_car_by_plate(self, plate_number: str, user_id: Optional[str] = None) -> CarResponse:
        """Get a car by plate number."""
        car = await self.repo.get_by_plate_number(plate_number)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car not found"
            )
        
        # Check if user has access (if user_id is provided)
        if user_id and car.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return CarResponse.model_validate(car)
    
    async def get_car_by_qr_code(self, qr_code: str) -> CarResponse:
        """Get a car by QR code."""
        car = await self.repo.get_by_qr_code(qr_code)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car not found"
            )
        
        return CarResponse.model_validate(car)
    
    async def get_cars(
        self,
        user_id: Optional[str] = None,
        page: int = 1,
        size: int = 50,
        search_params: Optional[CarSearch] = None
    ) -> CarList:
        """Get cars with pagination and search."""
        skip = (page - 1) * size
        
        # Prepare search parameters
        filters = {}
        if user_id:
            filters['user_id'] = user_id
        if search_params:
            filters.update(search_params.dict(exclude_none=True))
        
        # Get cars and total count
        cars = await self.repo.get_all(skip=skip, limit=size, **filters)
        total = await self.repo.count(**filters)
        
        pages = (total + size - 1) // size if total > 0 else 0
        
        return CarList(
            cars=[CarResponse.model_validate(car) for car in cars],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    async def update_car(self, car_id: str, update_data: CarUpdate, user_id: Optional[str] = None) -> CarResponse:
        """Update a car."""
        # Check if car exists
        existing_car = await self.repo.get_by_id(car_id)
        if not existing_car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car not found"
            )
        
        # Check if user has access (if user_id is provided)
        if user_id and existing_car.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update car
        updated_car = await self.repo.update(car_id, update_data.dict(exclude_none=True))
        if not updated_car:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update car"
            )
        
        return CarResponse.model_validate(updated_car)
    
    async def delete_car(self, car_id: str, user_id: Optional[str] = None) -> None:
        """Delete a car."""
        # Check if car exists
        existing_car = await self.repo.get_by_id(car_id)
        if not existing_car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car not found"
            )
        
        # Check if user has access (if user_id is provided)
        if user_id and existing_car.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete car
        success = await self.repo.delete(car_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete car"
            )
    
        
    async def update_document(self, car_id: str, document_type: str, document_url: str, user_id: str) -> DocumentUploadResponse:
        """Update a document for a car."""
        # Check if car exists and user has access
        car = await self.get_car(car_id, user_id)
        
        # Validate document type
        valid_documents = ['plate_photo_url', 'assurance_paper_url', 'license_url', 'vignette_url', 'controle_technique_url']
        if document_type not in valid_documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type. Must be one of: {', '.join(valid_documents)}"
            )
        
        # Update document
        update_data = {document_type: document_url}
        updated_car = await self.repo.update(car_id, update_data)
        
        if not updated_car:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update document"
            )
        
        return DocumentUploadResponse(
            car_id=updated_car.id,
            document_type=document_type.replace('_url', '').replace('_', ' ').title(),
            document_url=document_url,
            upload_timestamp=datetime.utcnow(),
            message=f"{document_type.replace('_url', '').replace('_', ' ').title()} uploaded successfully"
        )
    
    async def get_qr_code(self, car_id: str, user_id: Optional[str] = None) -> QRCodeResponse:
        """Get QR code for a car."""
        car = await self.get_car(car_id, user_id)
        
        return QRCodeResponse(
            qr_code=car.qr_code,
            plate_number=car.plate_number,
            generated_at=car.created_at
        )
    
    async def get_user_cars(self, user_id: str, limit: int = 100) -> List[CarResponse]:
        """Get all cars for a user (including all statuses)."""
        cars = await self.repo.get_all(user_id=user_id, limit=limit)
        return [CarResponse.model_validate(car) for car in cars]
    
    async def get_recent_cars(self, limit: int = 10) -> List[CarResponse]:
        """Get recent cars."""
        cars = await self.repo.get_recent_cars(limit)
        return [CarResponse.model_validate(car) for car in cars]
    
    async def get_stats(self, user_id: Optional[str] = None) -> CarStats:
        """Get car statistics."""
        stats = await self.repo.get_stats(user_id)
        return CarStats(**stats)
    
    async def get_dashboard_data(self, user_id: str) -> DashboardData:
        """Get comprehensive dashboard data for cars."""
        # Get statistics
        stats = await self.get_stats(user_id)
        
        # Get recent cars
        recent_cars = await self.get_recent_cars(limit=5)
        
        # Get user's cars
        my_cars = await self.get_user_cars(user_id, limit=10)
        
        return DashboardData(
            stats=stats,
            recent_cars=recent_cars,
            my_cars=my_cars
        )
    
    async def search_cars(self, search_params: CarSearch, page: int = 1, size: int = 50) -> CarList:
        """Search cars with advanced filters."""
        return await self.get_cars(search_params=search_params, page=page, size=size)
    
    async def update_car_status(self, car_id: str, new_status: str, user_id: Optional[str] = None) -> CarResponse:
        """Update car status."""
        # Validate status
        allowed_statuses = ["active", "not_active"]
        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"
            )
        
        # Update car
        update_data = {"status": new_status}
        return await self.update_car(car_id, CarUpdate(**update_data), user_id)
    
    async def verify_plate_number_availability(self, plate_number: str) -> dict:
        """Check if a plate number is available."""
        existing_car = await self.repo.get_by_plate_number(plate_number)
        
        return {
            "plate_number": plate_number,
            "is_available": existing_car is None,
            "message": "Plate number is available" if existing_car is None else "Plate number already exists"
        }
