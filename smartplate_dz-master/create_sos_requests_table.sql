-- Create SOS requests table for SmartPlate emergency assistance system
-- This table stores SOS emergency assistance requests from users

CREATE TABLE IF NOT EXISTS sos_requests (
    -- Primary key
    id VARCHAR(36) PRIMARY KEY,
    
    -- User information
    user_id VARCHAR(36) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    
    -- Request details
    license_plate VARCHAR(50) NOT NULL,
    emergency_description TEXT NOT NULL,
    current_location TEXT,
    gps_coordinates VARCHAR(100),
    
    -- Status and management
    status VARCHAR(20) NOT NULL DEFAULT 'en attente',
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sos_requests_user_id ON sos_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_sos_requests_email ON sos_requests(email);
CREATE INDEX IF NOT EXISTS idx_sos_requests_license_plate ON sos_requests(license_plate);
CREATE INDEX IF NOT EXISTS idx_sos_requests_status ON sos_requests(status);
CREATE INDEX IF NOT EXISTS idx_sos_requests_created_at ON sos_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_sos_requests_is_active ON sos_requests(is_active);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sos_requests_status_active ON sos_requests(status, is_active);
CREATE INDEX IF NOT EXISTS idx_sos_requests_status_created ON sos_requests(status, created_at DESC);

-- Add table comments for documentation
COMMENT ON TABLE sos_requests IS 'SOS emergency assistance requests from SmartPlate users';
COMMENT ON COLUMN sos_requests.id IS 'Unique identifier for the SOS request';
COMMENT ON COLUMN sos_requests.user_id IS 'ID of the user making the request';
COMMENT ON COLUMN sos_requests.full_name IS 'Full name of the person requesting help';
COMMENT ON COLUMN sos_requests.email IS 'Email address of the requester';
COMMENT ON COLUMN sos_requests.phone IS 'Phone number of the requester';
COMMENT ON COLUMN sos_requests.license_plate IS 'License plate number of the vehicle';
COMMENT ON COLUMN sos_requests.emergency_description IS 'Description of the emergency situation';
COMMENT ON COLUMN sos_requests.current_location IS 'Current location description';
COMMENT ON COLUMN sos_requests.gps_coordinates IS 'GPS coordinates of the requester';
COMMENT ON COLUMN sos_requests.status IS 'Current status of the request (en attente, en cours, résolu, annulé)';
COMMENT ON COLUMN sos_requests.claimed_by IS 'ID of the operator who claimed the request';
COMMENT ON COLUMN sos_requests.claimed_at IS 'Timestamp when the request was claimed';
COMMENT ON COLUMN sos_requests.resolved_at IS 'Timestamp when the request was resolved';
COMMENT ON COLUMN sos_requests.resolution_notes IS 'Notes about how the request was resolved';
COMMENT ON COLUMN sos_requests.priority IS 'Priority level (low, medium, high, critical)';
COMMENT ON COLUMN sos_requests.is_active IS 'Whether the request is active';
COMMENT ON COLUMN sos_requests.created_at IS 'Timestamp when the request was created';
COMMENT ON COLUMN sos_requests.updated_at IS 'Timestamp when the request was last updated';
