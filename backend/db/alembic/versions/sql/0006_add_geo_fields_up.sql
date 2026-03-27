-- Migration 0006: Add Address and Geolocation Fields
-- Adds structured address, latitude, longitude columns
-- Note: PostGIS geometry columns skipped - PostGIS not available for PG 18 yet

-- Add address and geo columns to cafes
ALTER TABLE cafes
    ADD COLUMN address TEXT,
    ADD COLUMN latitude NUMERIC(9,6),
    ADD COLUMN longitude NUMERIC(9,6);

-- Add address and geo columns to roasters
ALTER TABLE roasters
    ADD COLUMN address TEXT,
    ADD COLUMN latitude NUMERIC(9,6),
    ADD COLUMN longitude NUMERIC(9,6);

-- Create indexes for proximity queries (without PostGIS)
CREATE INDEX idx_cafes_lat_lng ON cafes(latitude, longitude);
CREATE INDEX idx_roasters_lat_lng ON roasters(latitude, longitude);
