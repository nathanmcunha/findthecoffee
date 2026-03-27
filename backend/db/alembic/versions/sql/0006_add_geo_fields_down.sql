-- Migration 0006: Add Address and Geolocation Fields (DOWN)

-- Drop indexes
DROP INDEX IF EXISTS idx_roasters_lat_lng;
DROP INDEX IF EXISTS idx_cafes_lat_lng;

-- Drop columns
ALTER TABLE roasters DROP COLUMN IF EXISTS longitude, DROP COLUMN IF EXISTS latitude, DROP COLUMN IF EXISTS address;
ALTER TABLE cafes DROP COLUMN IF EXISTS longitude, DROP COLUMN IF EXISTS latitude, DROP COLUMN IF EXISTS address;
