-- Add PASSWORD value to otp_purpose enum for password change verification
-- This migration adds support for OTP codes used in password change flows

-- First, add the new value to the enum type
ALTER TYPE otp_purpose ADD VALUE 'PASSWORD';

-- Verify the enum now includes all expected values
-- (This is just for documentation, not executed)
-- SELECT unnest(enum_range(NULL::otp_purpose));
