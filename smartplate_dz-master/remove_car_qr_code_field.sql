-- Remove qr_code field from cars table
-- This migration removes the QR code field from cars since QR codes are now handled at the User level

-- First, let's see the current state
SELECT COUNT(*) as total_cars FROM cars;

-- Drop the qr_code column from cars table
ALTER TABLE cars DROP COLUMN IF EXISTS qr_code;

-- Verify the column has been removed
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'cars' 
ORDER BY ordinal_position;

-- The cars table should now have:
-- - id
-- - user_id  
-- - plate_number
-- - plate_photo_url
-- - assurance_paper_url
-- - license_url
-- - status
-- - is_active
-- - created_at
-- - updated_at

-- QR codes are now handled at the User level in the users table
