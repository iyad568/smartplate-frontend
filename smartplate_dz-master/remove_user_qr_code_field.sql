-- Remove qr_code field from users table
-- This migration removes the QR code field from users since QR codes are now handled at the Car level

-- First, let's see the current state
SELECT COUNT(*) as total_users FROM users;

-- Drop the unique constraint if it exists
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_qr_code_unique;

-- Drop the index if it exists
DROP INDEX IF EXISTS idx_users_qr_code;

-- Drop the qr_code column from users table
ALTER TABLE users DROP COLUMN IF EXISTS qr_code;

-- Verify the column has been removed
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- The users table should now have:
-- - id
-- - full_name
-- - email
-- - phone
-- - hashed_password
-- - role
-- - is_verified
-- - provider
-- - google_id
-- - profile_picture
-- - created_at
-- - updated_at

-- QR codes are now handled at the Car level in the cars table
