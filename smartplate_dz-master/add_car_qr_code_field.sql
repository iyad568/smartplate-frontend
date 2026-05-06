-- Add qr_code field to cars table
-- This migration adds the QR code field back to cars for the original car-level QR system

-- Add the qr_code column to cars table
ALTER TABLE cars ADD COLUMN qr_code VARCHAR(255) NOT NULL;

-- Add unique constraint on qr_code to ensure uniqueness
ALTER TABLE cars ADD CONSTRAINT cars_qr_code_unique UNIQUE (qr_code);

-- Add index on qr_code for faster lookups
CREATE INDEX IF NOT EXISTS idx_cars_qr_code ON cars(qr_code);

-- Generate QR codes for existing cars (this should be done in application code)
-- For now, we'll generate QR codes for existing cars
UPDATE cars SET qr_code = 'QR-' || UPPER(plate_number) || '-' || UPPER(SUBSTRING(REPLACE(id, '-', ''), 1, 8))
WHERE qr_code IS NULL OR qr_code = '';

-- Verify the migration
SELECT COUNT(*) as total_cars, COUNT(qr_code) as cars_with_qr_code FROM cars;

-- The cars table should now have:
-- - id
-- - user_id
-- - plate_number
-- - qr_code (newly added)
-- - plate_photo_url
-- - assurance_paper_url
-- - license_url
-- - status
-- - is_active
-- - created_at
-- - updated_at

-- QR codes are now handled at the Car level (one QR code per plate)
