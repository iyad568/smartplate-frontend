"""
API routes for User Dashboard functionality.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin
from app.core.file_storage import save_upload
from app.db.session import get_db
from app.models.user import User
from app.schemas.car import CarResponse, DashboardData
from app.schemas.auth import OtpSentResponse
from app.services.car_service import CarService
from app.services.qr_service import QRCodeService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ─── Dashboard Overview ─────────────────────────────────────────────────────

@router.get(
    "/overview",
    response_model=DashboardData,
    summary="Get user dashboard overview",
    responses={
        200: {"description": "Dashboard data retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> DashboardData:
    """Get comprehensive dashboard data for the current user."""
    car_service = CarService(db)
    return await car_service.get_dashboard_data(user.id)


# ─── QR Code Management ─────────────────────────────────────────────────────

@router.get(
    "/qr-codes",
    response_model=List[dict],
    summary="Get all QR codes for user's cars",
    responses={
        200: {"description": "QR codes retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
async def get_user_qr_codes(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[dict]:
    """Get QR codes for all user's cars."""
    car_service = CarService(db)
    cars = await car_service.get_user_cars(user.id)
    
    qr_service = QRCodeService()
    qr_codes = []
    
    for car in cars:
        qr_info = qr_service.get_qr_code_info(car.qr_code)
        qr_codes.append({
            "car_id": car.id,
            "plate_number": car.plate_number,
            "qr_code": car.qr_code,
            "qr_info": qr_info,
            "status": car.status,
            "generated_at": car.created_at
        })
    
    return qr_codes


@router.get(
    "/qr-code/{car_id}",
    summary="Get QR code image for a specific car",
    responses={
        200: {"description": "QR code image generated successfully"},
        404: {"description": "Car not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def get_qr_code_image(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Generate QR code image for a specific car."""
    car_service = CarService(db)
    car = await car_service.get_car(car_id, user.id)
    
    qr_service = QRCodeService()
    try:
        qr_package = qr_service.generate_plate_qr_code(car.plate_number, car.id)
        return {
            "qr_image_base64": qr_package["qr_image_bytes"].hex(),
            "qr_data": qr_package["qr_data"],
            "plate_number": car.plate_number,
            "format": qr_package["image_format"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {str(e)}"
        )


# ─── Plate Management ─────────────────────────────────────────────────────

@router.get(
    "/plates",
    response_model=List[CarResponse],
    summary="Get all user's license plates",
    responses={
        200: {"description": "Plates retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
async def get_user_plates(
    limit: int = Query(100, ge=1, le=100, description="Maximum number of plates"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[CarResponse]:
    """Get all license plates for the current user."""
    car_service = CarService(db)
    return await car_service.get_user_cars(user.id, limit)


@router.get(
    "/plates/{car_id}",
    response_model=CarResponse,
    summary="Get specific license plate details",
    responses={
        200: {"description": "Plate details retrieved successfully"},
        404: {"description": "Plate not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def get_plate_details(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> CarResponse:
    """Get detailed information about a specific license plate."""
    car_service = CarService(db)
    return await car_service.get_car(car_id, user.id)


@router.put(
    "/plates/{car_id}/status",
    response_model=CarResponse,
    summary="Update plate status (admin only)",
    responses={
        200: {"description": "Plate status updated successfully"},
        404: {"description": "Plate not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
        400: {"description": "Invalid status"},
    },
)
async def update_plate_status(
    car_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> CarResponse:
    """Update the status of a license plate (admin only)."""
    car_service = CarService(db)
    return await car_service.update_car_status(car_id, new_status, user_id=None)


# ─── Document Management ─────────────────────────────────────────────────────

@router.post(
    "/plates/{car_id}/documents/plate-photo",
    summary="Upload plate photo",
    responses={
        200: {"description": "Plate photo uploaded successfully"},
        404: {"description": "Plate not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def upload_plate_photo(
    car_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload plate photo for a specific car."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG images are allowed."
        )
    
    car_service = CarService(db)
    document_url = await save_upload(file, "plate-photos")
    return await car_service.update_document(
        car_id, "plate_photo_url", document_url, user.id
    )


@router.post(
    "/plates/{car_id}/documents/license",
    summary="Upload driver license",
    responses={
        200: {"description": "License uploaded successfully"},
        404: {"description": "Plate not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def upload_driver_license(
    car_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload driver license for a specific car."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images and PDF files are allowed."
        )
    
    car_service = CarService(db)
    document_url = await save_upload(file, "licenses")
    return await car_service.update_document(
        car_id, "license_url", document_url, user.id
    )


@router.post(
    "/plates/{car_id}/documents/insurance",
    summary="Upload insurance document",
    responses={
        200: {"description": "Insurance uploaded successfully"},
        404: {"description": "Plate not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def upload_insurance_document(
    car_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload insurance document for a specific car."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images and PDF files are allowed."
        )
    
    car_service = CarService(db)
    document_url = await save_upload(file, "assurance")
    return await car_service.update_document(
        car_id, "assurance_paper_url", document_url, user.id
    )


# ─── Plate Transfer/Selling ──────────────────────────────────────────────────

@router.post(
    "/plates/{car_id}/sell",
    summary="Initiate plate selling process",
    responses={
        200: {"description": "Selling process initiated successfully"},
        404: {"description": "Plate not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
        400: {"description": "Plate cannot be sold"},
    },
)
async def initiate_plate_sale(
    car_id: str,
    sale_price: float = Query(..., gt=0, description="Sale price"),
    buyer_email: str = Query(..., description="Buyer email address"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Initiate the process of selling a license plate."""
    car_service = CarService(db)
    car = await car_service.get_car(car_id, user.id)
    
    # Check if plate can be sold (must have complete documents)
    if not car.has_complete_documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plate cannot be sold. All required documents must be uploaded first."
        )
    
    # For now, this is a mock implementation
    # In production, you'd create a sale record, send notifications, etc.
    return {
        "plate_id": car_id,
        "plate_number": car.plate_number,
        "sale_price": sale_price,
        "buyer_email": buyer_email,
        "seller_id": user.id,
        "seller_name": user.full_name,
        "status": "pending",
        "message": "Plate selling process initiated. Waiting for buyer confirmation.",
        "initiated_at": datetime.utcnow()
    }


@router.get(
    "/plates/{car_id}/sale-status",
    summary="Get plate sale status",
    responses={
        200: {"description": "Sale status retrieved successfully"},
        404: {"description": "Plate not found"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
    },
)
async def get_plate_sale_status(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get the current status of a plate sale."""
    car_service = CarService(db)
    car = await car_service.get_car(car_id, user.id)
    
    # Mock implementation - in production, you'd query a sales table
    return {
        "plate_id": car_id,
        "plate_number": car.plate_number,
        "sale_status": "not_listed",  # not_listed, pending, completed, cancelled
        "listing_date": None,
        "sale_price": None,
        "buyer_info": None,
        "transaction_date": None
    }


# ─── User Profile Management ─────────────────────────────────────────────────

@router.get(
    "/profile",
    summary="Get user profile information",
    responses={
        200: {"description": "Profile retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
async def get_user_profile(
    user: User = Depends(get_current_user)
):
    """Get current user's profile information."""
    return {
        "full_name": user.full_name,
        "role": user.role,
        "profile_picture": user.profile_picture
    }


@router.put(
    "/profile",
    summary="Update user profile",
    responses={
        200: {"description": "Profile updated successfully"},
        401: {"description": "Authentication required"},
        400: {"description": "Invalid data provided"},
    },
)
async def update_user_profile(
    full_name: Optional[str] = None,
    profile_picture: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile information."""
    auth_service = AuthService(db)
    
    update_data = {}
    if full_name:
        update_data["full_name"] = full_name
    if profile_picture:
        update_data["profile_picture"] = profile_picture
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    updated_user = await auth_service.update_user_profile(user.id, update_data)
    
    return {
        "full_name": updated_user.full_name,
        "role": updated_user.role,
        "profile_picture": updated_user.profile_picture,
        "message": "Profile updated successfully"
    }


@router.post(
    "/send-password-otp",
    response_model=OtpSentResponse,
    summary="Send OTP code for password change",
    responses={
        200: {"description": "OTP sent successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "User not found"},
    },
)
async def send_password_otp(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> OtpSentResponse:
    """Send OTP code to user's email for password change verification."""
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    return await auth_service.send_password_otp(user.id)


@router.post(
    "/change-password",
    summary="Change user password",
    responses={
        200: {"description": "Password changed successfully"},
        401: {"description": "Authentication required"},
        400: {"description": "Invalid current password, new password, or OTP"},
    },
)
async def change_password(
    current_password: str,
    new_password: str,
    otp_code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change the current user's password with OTP verification."""
    from app.core.security import verify_password
    from app.db.repositories.user_repo import UserRepository
    from app.db.repositories.otp_repo import OtpRepository
    from app.models.otp_code import OtpCode, OtpPurpose
    
    # Get user repository
    user_repo = UserRepository(db)
    current_user = await user_repo.get_by_id(user.id)
    
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is same as current password
    if verify_password(new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as current password"
        )
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    # Verify OTP code using the same method as login
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    await auth_service.otp.verify_and_consume(
        user=user, purpose=OtpPurpose.PASSWORD, plain_code=otp_code
    )
    
    # Change password
    auth_service = AuthService(db)
    success = await auth_service.change_password(user.id, current_password, new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
    
    return {"message": "Password changed successfully"}




