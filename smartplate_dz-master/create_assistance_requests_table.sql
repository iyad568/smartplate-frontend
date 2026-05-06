-- Create unified assistance requests table for SmartPlate emergency and roadside assistance system
-- This table combines SOS emergency requests and Depannage roadside assistance requests

CREATE TABLE IF NOT EXISTS assistance_requests (
    -- Primary key
    id VARCHAR(36) PRIMARY KEY,
    
    -- Request type
    request_type VARCHAR(20) NOT NULL,  -- 'sos' or 'depannage'
    
    -- User information
    user_id VARCHAR(36) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),  -- Required for SOS, optional for Depannage
    phone VARCHAR(20),  -- Optional for SOS, required for Depannage
    
    -- Request details
    license_plate VARCHAR(50) NOT NULL,
    
    -- SOS specific fields
    emergency_description TEXT,  -- SOS specific
    current_location TEXT,  -- SOS specific
    
    -- Depannage specific fields
    breakdown_type VARCHAR(50),  -- Depannage specific
    location_address TEXT,  -- Depannage specific
    
    -- Common fields
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
CREATE INDEX IF NOT EXISTS idx_assistance_requests_id ON assistance_requests(id);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_user_id ON assistance_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_email ON assistance_requests(email);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_phone ON assistance_requests(phone);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_license_plate ON assistance_requests(license_plate);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_request_type ON assistance_requests(request_type);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_breakdown_type ON assistance_requests(breakdown_type);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_status ON assistance_requests(status);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_created_at ON assistance_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_is_active ON assistance_requests(is_active);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_assistance_requests_type_status ON assistance_requests(request_type, status);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_status_active ON assistance_requests(status, is_active);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_status_created ON assistance_requests(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_type_created ON assistance_requests(request_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assistance_requests_breakdown_status ON assistance_requests(breakdown_type, status);

-- Add table comments for documentation
COMMENT ON TABLE assistance_requests IS 'Unified emergency and roadside assistance requests from SmartPlate users';
COMMENT ON COLUMN assistance_requests.id IS 'Unique identifier for the assistance request';
COMMENT ON COLUMN assistance_requests.request_type IS 'Type of request: "sos" for emergency, "depannage" for roadside assistance';
COMMENT ON COLUMN assistance_requests.user_id IS 'ID of the user making the request';
COMMENT ON COLUMN assistance_requests.full_name IS 'Full name of the person requesting assistance';
COMMENT ON COLUMN assistance_requests.email IS 'Email address of the requester (required for SOS)';
COMMENT ON COLUMN assistance_requests.phone IS 'Phone number of the requester (required for Depannage)';
COMMENT ON COLUMN assistance_requests.license_plate IS 'License plate number of the vehicle';
COMMENT ON COLUMN assistance_requests.emergency_description IS 'Description of the emergency situation (SOS specific)';
COMMENT ON COLUMN assistance_requests.current_location IS 'Current location description (SOS specific)';
COMMENT ON COLUMN assistance_requests.breakdown_type IS 'Type of breakdown (Depannage specific: Batterie, Pneu crevé, Moteur, Autre)';
COMMENT ON COLUMN assistance_requests.location_address IS 'Location address (Depannage specific)';
COMMENT ON COLUMN assistance_requests.gps_coordinates IS 'GPS coordinates of the requester';
COMMENT ON COLUMN assistance_requests.additional_notes IS 'Additional notes about the request';
COMMENT ON COLUMN assistance_requests.status IS 'Current status of the request (en attente, en cours, résolu, annulé)';
COMMENT ON COLUMN assistance_requests.is_active IS 'Whether the request is active';
COMMENT ON COLUMN assistance_requests.created_at IS 'Timestamp when the request was created';
COMMENT ON COLUMN assistance_requests.updated_at IS 'Timestamp when the request was last updated';
