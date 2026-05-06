-- Add qr_code field to users table
-- This migration adds a nullable QR code field to each user (generated on first plate purchase)

-- Add the qr_code column to users table (nullable initially)
ALTER TABLE users ADD COLUMN qr_code VARCHAR(255);

-- Add unique constraint on qr_code to ensure uniqueness (only for non-null values)
ALTER TABLE users ADD CONSTRAINT users_qr_code_unique UNIQUE (qr_code);

-- Add index on qr_code for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_qr_code ON users(qr_code);

-- Note: QR codes will be generated when users purchase their first plate
-- Existing users will get QR codes when they create their first car

-- Verify the migration
SELECT COUNT(*) as total_users, COUNT(qr_code) as users_with_qr_code FROM users;
