-- Create orders table for SmartPlate - matching PlaqueStandard.jsx form data
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    order_type VARCHAR(20) NOT NULL DEFAULT 'plate_order', -- plate_order, product_order, service_order
    plate_type VARCHAR(20) NOT NULL, -- standard, commercial, special
    
    -- Order details
    total_price NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'DZD',
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, processing, completed, cancelled
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, paid, failed
    
    -- Exact fields from PlaqueStandard.jsx form
    name VARCHAR(255), -- owner full name
    first VARCHAR(255), -- owner first name
    phone VARCHAR(20), -- owner phone
    email VARCHAR(255), -- owner email
    cni VARCHAR(50), -- CNI/ID number
    address TEXT, -- owner address
    chassis VARCHAR(50), -- vehicle chassis number
    type VARCHAR(50), -- vehicle type
    brand VARCHAR(50), -- vehicle brand
    plate VARCHAR(20), -- license plate number
    power VARCHAR(20) DEFAULT 'essence', -- power type (essence/diesel)
    
    -- Metadata
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    processed_at TIMESTAMP WITHOUT TIME ZONE,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    
    -- Foreign key to users
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS ix_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS ix_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS ix_orders_payment_status ON orders(payment_status);
CREATE INDEX IF NOT EXISTS ix_orders_plate_type ON orders(plate_type);
CREATE INDEX IF NOT EXISTS ix_orders_plate ON orders(plate);
CREATE INDEX IF NOT EXISTS ix_orders_created_at ON orders(created_at);

-- Add comments
COMMENT ON TABLE orders IS 'Orders for plates, products, and services - matching PlaqueStandard.jsx form data';
COMMENT ON COLUMN orders.id IS 'Unique identifier for the order';
COMMENT ON COLUMN orders.user_id IS 'ID of the user who placed the order';
COMMENT ON COLUMN orders.order_type IS 'Type of order: plate_order, product_order, service_order';
COMMENT ON COLUMN orders.plate_type IS 'Type of plate: standard, commercial, special';
COMMENT ON COLUMN orders.total_price IS 'Total price of the order';
COMMENT ON COLUMN orders.status IS 'Order status: pending, processing, completed, cancelled';
COMMENT ON COLUMN orders.payment_status IS 'Payment status: pending, paid, failed';
COMMENT ON COLUMN orders.name IS 'Owner full name (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.first IS 'Owner first name (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.phone IS 'Owner phone number (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.email IS 'Owner email address (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.cni IS 'CNI/ID number (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.address IS 'Owner address (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.chassis IS 'Vehicle chassis number (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.type IS 'Vehicle type (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.brand IS 'Vehicle brand (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.plate IS 'License plate number (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.power IS 'Power type (essence/diesel) (from PlaqueStandard.jsx form)';
COMMENT ON COLUMN orders.created_at IS 'Order creation timestamp';
COMMENT ON COLUMN orders.updated_at IS 'Order last update timestamp';
COMMENT ON COLUMN orders.processed_at IS 'Order processing timestamp';
COMMENT ON COLUMN orders.completed_at IS 'Order completion timestamp';
