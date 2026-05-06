-- Add vehicle and owner information fields to cars table
ALTER TABLE cars ADD COLUMN IF NOT EXISTS chassis_number VARCHAR(50);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS vehicle_type VARCHAR(50);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS vehicle_brand VARCHAR(50);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS power_type VARCHAR(20);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS cni_number VARCHAR(50);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS owner_address TEXT;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS ix_cars_vehicle_type ON cars(vehicle_type);
CREATE INDEX IF NOT EXISTS ix_cars_vehicle_brand ON cars(vehicle_brand);
CREATE INDEX IF NOT EXISTS ix_cars_power_type ON cars(power_type);

-- Add comments
COMMENT ON COLUMN cars.chassis_number IS 'Vehicle chassis number';
COMMENT ON COLUMN cars.vehicle_type IS 'Vehicle type';
COMMENT ON COLUMN cars.vehicle_brand IS 'Vehicle brand';
COMMENT ON COLUMN cars.power_type IS 'Power type (essence/diesel)';
COMMENT ON COLUMN cars.cni_number IS 'CNI/ID number';
COMMENT ON COLUMN cars.owner_address IS 'Owner address';
