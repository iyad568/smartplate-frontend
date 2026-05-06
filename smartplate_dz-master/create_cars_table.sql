-- Create cars table for SmartPlate vehicle management system
-- This table stores vehicle information including QR codes for license plates

CREATE TABLE IF NOT EXISTS cars (
    -- Primary key
    id VARCHAR(36) PRIMARY KEY,
    
    -- Foreign key to user
    user_id VARCHAR(36) NOT NULL,
    
    -- Plate information
    plate_number VARCHAR(20) NOT NULL UNIQUE,
    qr_code VARCHAR(255) NOT NULL UNIQUE,
    plate_photo_url TEXT,
    
    -- Document URLs
    assurance_paper_url TEXT,
    license_url TEXT,
    
    -- Status and metadata
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    
    -- General metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cars_user_id ON cars(user_id);
CREATE INDEX IF NOT EXISTS idx_cars_plate_number ON cars(plate_number);
CREATE INDEX IF NOT EXISTS idx_cars_qr_code ON cars(qr_code);
CREATE INDEX IF NOT EXISTS idx_cars_status ON cars(status);
CREATE INDEX IF NOT EXISTS idx_cars_created_at ON cars(created_at);
CREATE INDEX IF NOT EXISTS idx_cars_is_active ON cars(is_active);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_cars_user_status ON cars(user_id, status);
CREATE INDEX IF NOT EXISTS idx_cars_status_active ON cars(status, is_active);
CREATE INDEX IF NOT EXISTS idx_cars_status_created ON cars(status, created_at DESC);

-- Create indexes for document availability queries
CREATE INDEX IF NOT EXISTS idx_cars_plate_photo ON cars(plate_photo_url) WHERE plate_photo_url IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cars_assurance_paper ON cars(assurance_paper_url) WHERE assurance_paper_url IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cars_license ON cars(license_url) WHERE license_url IS NOT NULL;

-- Add table comments for documentation
COMMENT ON TABLE cars IS 'Vehicle information for SmartPlate users including QR-coded license plates';
COMMENT ON COLUMN cars.id IS 'Unique identifier for the car';
COMMENT ON COLUMN cars.user_id IS 'ID of the user who owns the car';
COMMENT ON COLUMN cars.plate_number IS 'License plate number (unique)';
COMMENT ON COLUMN cars.qr_code IS 'QR code data/URL for the license plate';
COMMENT ON COLUMN cars.plate_photo_url IS 'URL to the plate photo';
COMMENT ON COLUMN cars.assurance_paper_url IS 'URL to the assurance paper document';
COMMENT ON COLUMN cars.license_url IS 'URL to the driver license document';
COMMENT ON COLUMN cars.status IS 'Car status (active, not_active)';
COMMENT ON COLUMN cars.is_active IS 'Whether the car record is active';
COMMENT ON COLUMN cars.created_at IS 'Car record creation timestamp';
COMMENT ON COLUMN cars.updated_at IS 'Car record last update timestamp';

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_cars_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_cars_updated_at
    BEFORE UPDATE ON cars
    FOR EACH ROW
    EXECUTE FUNCTION update_cars_updated_at();

-- Create view for cars with complete documents
CREATE OR REPLACE VIEW cars_complete_profile AS
SELECT 
    id,
    user_id,
    plate_number,
    qr_code,
    status,
    created_at,
    updated_at
FROM cars
WHERE plate_photo_url IS NOT NULL
  AND assurance_paper_url IS NOT NULL
  AND license_url IS NOT NULL
  AND is_active = TRUE;

COMMENT ON VIEW cars_complete_profile IS 'Cars with complete profiles (all documents uploaded)';

-- Create view for cars statistics
CREATE OR REPLACE VIEW car_stats AS
SELECT 
    COUNT(*) as total_cars,
    COUNT(*) FILTER (WHERE status = 'active') as active_cars,
    COUNT(*) FILTER (WHERE status = 'not_active') as not_active_cars,
    COUNT(*) FILTER (
        WHERE plate_photo_url IS NOT NULL 
        AND assurance_paper_url IS NOT NULL 
        AND license_url IS NOT NULL
    ) as complete_profile_cars,
    COUNT(*) FILTER (
        WHERE plate_photo_url IS NOT NULL 
        AND assurance_paper_url IS NOT NULL 
        AND license_url IS NOT NULL
    ) as complete_documents_cars
FROM cars
WHERE is_active = TRUE;

COMMENT ON VIEW car_stats IS 'Aggregated statistics for all cars';
