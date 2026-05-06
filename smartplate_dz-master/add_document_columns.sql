-- SQL script to add document upload columns to cars table
-- Run this script manually in your database

-- Add vignette_url column if it doesn't exist
ALTER TABLE cars ADD COLUMN IF NOT EXISTS vignette_url TEXT;

-- Add controle_technique_url column if it doesn't exist  
ALTER TABLE cars ADD COLUMN IF NOT EXISTS controle_technique_url TEXT;

-- Check if assurance_paper_url exists (it should already exist)
-- If not, add it:
-- ALTER TABLE cars ADD COLUMN IF NOT EXISTS assurance_paper_url TEXT;

-- Verify the columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'cars' 
  AND column_name IN ('vignette_url', 'controle_technique_url', 'assurance_paper_url')
ORDER BY column_name;
