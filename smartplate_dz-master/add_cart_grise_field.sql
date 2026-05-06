-- Add cart grise (gray card) upload field to orders table
-- This migration adds support for cart grise document uploads

-- Add cart grise URL field to orders table
ALTER TABLE orders ADD COLUMN IF NOT EXISTS cart_grise_url TEXT;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_orders_cart_grise ON orders(cart_grise_url);

-- Verify migration
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'orders' 
  AND column_name IN ('cart_grise_url')
ORDER BY column_name;
