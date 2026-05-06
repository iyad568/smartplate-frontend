"""
QR Code generation service for SmartPlate.
"""
import uuid
from datetime import datetime
from typing import Optional

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_L
    QR_CODE_AVAILABLE = True
except ImportError:
    QR_CODE_AVAILABLE = False

from fastapi import HTTPException, status


class QRCodeService:
    """Service for generating QR codes for license plates."""
    
    def __init__(self):
        self.qr_available = QR_CODE_AVAILABLE
    
    def generate_qr_data(self, plate_number: str, car_id: str) -> str:
        """Generate QR code data for a car plate."""
        return f"QR-{plate_number.upper()}-{car_id[:8]}"
    
    def generate_user_qr_data(self, user_id: str) -> str:
        """Generate QR code data for a user."""
        return f"USER-{user_id[:8]}-{uuid.uuid4().hex[:8].upper()}"
    
    def generate_qr_code_image(self, data: str, save_path: Optional[str] = None) -> bytes:
        """Generate QR code image as bytes."""
        if not self.qr_available:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="QR code generation not available. Install qrcode package."
            )
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add data and optimize
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to file if path provided
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(buffer.getvalue())
        
        return buffer.getvalue()
    
    def generate_plate_qr_code(self, plate_number: str, car_id: str, save_path: Optional[str] = None) -> dict:
        """Generate complete QR code package for a license plate."""
        # Generate QR data
        qr_data = self.generate_qr_data(plate_number, car_id)
        
        # Generate QR image
        qr_image_bytes = self.generate_qr_code_image(qr_data, save_path)
        
        return {
            "qr_data": qr_data,
            "qr_image_bytes": qr_image_bytes,
            "plate_number": plate_number,
            "car_id": car_id,
            "generated_at": datetime.utcnow(),
            "image_format": "PNG"
        }
    
    def generate_user_qr_code(self, user_id: str, existing_qr_code: Optional[str] = None, save_path: Optional[str] = None) -> dict:
        """Generate complete QR code package for a user."""
        # Use existing QR code if provided, otherwise generate new one
        qr_data = existing_qr_code if existing_qr_code else self.generate_user_qr_data(user_id)
        
        # Generate QR image
        qr_image_bytes = self.generate_qr_code_image(qr_data, save_path)
        
        return {
            "qr_data": qr_data,
            "qr_image_bytes": qr_image_bytes,
            "user_id": user_id,
            "generated_at": datetime.utcnow(),
            "image_format": "PNG"
        }
    
    def validate_qr_format(self, qr_code: str) -> bool:
        """Validate QR code format."""
        if not qr_code.startswith("QR-"):
            return False
        
        parts = qr_code.split("-")
        if len(parts) != 3:
            return False
        
        # Check if plate number part is reasonable (5-20 chars)
        plate_part = parts[1]
        if len(plate_part) < 5 or len(plate_part) > 20:
            return False
        
        # Check if ID part is reasonable (8 chars)
        id_part = parts[2]
        if len(id_part) != 8:
            return False
        
        return True
    
    def extract_plate_from_qr(self, qr_code: str) -> Optional[str]:
        """Extract plate number from QR code."""
        if not self.validate_qr_format(qr_code):
            return None
        
        return qr_code.split("-")[1]
    
    def get_qr_code_info(self, qr_code: str) -> dict:
        """Get information about a QR code."""
        return {
            "qr_code": qr_code,
            "is_valid": self.validate_qr_format(qr_code),
            "plate_number": self.extract_plate_from_qr(qr_code),
            "format": "QR-{PLATE}-{ID_PREFIX}"
        }
