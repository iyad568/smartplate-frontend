-- Add order-related fields to cars table for PlaqueStandard form integration
-- This migration adds owner information fields that were missing

-- Add owner information fields
ALTER TABLE cars ADD COLUMN IF NOT EXISTS owner_name VARCHAR(255);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS owner_first_name VARCHAR(255);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS owner_phone VARCHAR(20);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS owner_email VARCHAR(255);

-- Add cart grise field
ALTER TABLE cars ADD COLUMN IF NOT EXISTS cart_grise_url TEXT;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_cars_owner_name ON cars(owner_name);
CREATE INDEX IF NOT EXISTS idx_cars_owner_phone ON cars(owner_phone);
CREATE INDEX IF NOT EXISTS idx_cars_owner_email ON cars(owner_email);
CREATE INDEX IF NOT EXISTS idx_cars_cart_grise ON cars(cart_grise_url);

-- Verify the migration
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'cars' 
  AND column_name IN ('owner_name', 'owner_first_name', 'owner_phone', 'owner_email', 'cart_grise_url')
ORDER BY column_name;
