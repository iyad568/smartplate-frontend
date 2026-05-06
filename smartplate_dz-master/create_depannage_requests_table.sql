-- Create Depannage requests table for SmartPlate roadside assistance system
-- This table stores roadside assistance requests from users

CREATE TABLE IF NOT EXISTS depannage_requests (
    -- Primary key
    id VARCHAR(36) PRIMARY KEY,
    
    -- User information
    user_id VARCHAR(36) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    
    -- Request details
    license_plate VARCHAR(50) NOT NULL,
    breakdown_type VARCHAR(50) NOT NULL,
    location_address TEXT,
    gps_coordinates VARCHAR(100),
    additional_notes TEXT,
    
    -- Status and management
    status VARCHAR(20) NOT NULL DEFAULT 'en attente',
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_depannage_requests_user_id ON depannage_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_depannage_requests_phone ON depannage_requests(phone);
CREATE INDEX IF NOT EXISTS idx_depannage_requests_license_plate ON depannage_requests(license_plate);
CREATE INDEX IF NOT EXISTS idx_depannage_requests_breakdown_type ON depannage_requests(breakdown_type);
CREATE INDEX IF NOT EXISTS idx_depannage_requests_status ON depannage_requests(status);
CREATE INDEX IF NOT EXISTS idx_depannage_requests_created_at ON depannage_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_depannage_requests_is_active ON depannage_requests(is_active);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_depannage_requests_status_active ON depannage_requests(status, is_active);
CREATE INDEX IF NOT EXISTS idx_depannage_requests_status_created ON depannage_requests(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_depannage_requests_breakdown_status ON depannage_requests(breakdown_type, status);

-- Add table comments for documentation
COMMENT ON TABLE depannage_requests IS 'Roadside assistance requests from SmartPlate users';
COMMENT ON COLUMN depannage_requests.id IS 'Unique identifier for the Depannage request';
COMMENT ON COLUMN depannage_requests.user_id IS 'ID of the user making the request';
COMMENT ON COLUMN depannage_requests.full_name IS 'Full name of the person requesting assistance';
COMMENT ON COLUMN depannage_requests.phone IS 'Phone number of the requester';
COMMENT ON COLUMN depannage_requests.license_plate IS 'License plate number of the vehicle';
COMMENT ON COLUMN depannage_requests.breakdown_type IS 'Type of breakdown (Batterie, Pneu crevé, Moteur, Autre)';
COMMENT ON COLUMN depannage_requests.location_address IS 'Location address description';
COMMENT ON COLUMN depannage_requests.gps_coordinates IS 'GPS coordinates of the requester';
COMMENT ON COLUMN depannage_requests.additional_notes IS 'Additional notes about the breakdown';
COMMENT ON COLUMN depannage_requests.status IS 'Current status of the request (en attente, en cours, résolu, annulé)';
COMMENT ON COLUMN depannage_requests.is_active IS 'Whether the request is active';
COMMENT ON COLUMN depannage_requests.created_at IS 'Timestamp when the request was created';
COMMENT ON COLUMN depannage_requests.updated_at IS 'Timestamp when the request was last updated';
