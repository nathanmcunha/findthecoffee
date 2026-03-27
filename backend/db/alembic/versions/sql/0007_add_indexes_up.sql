-- Migration 0007: Add Missing Indexes
-- Adds indexes for FK joins, filters, and trigram search

-- Enable pg_trgm extension for trigram indexes
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- FK join indexes
CREATE INDEX IF NOT EXISTS idx_beans_roaster_id ON coffee_beans(roaster_id);
CREATE INDEX IF NOT EXISTS idx_inventory_bean_id ON cafe_inventory(bean_id);

-- Filter indexes
CREATE INDEX IF NOT EXISTS idx_beans_roast_level ON coffee_beans(roast_level);

-- Trigram indexes for ILIKE queries
CREATE INDEX IF NOT EXISTS idx_beans_origin_trgm ON coffee_beans USING gin(origin gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_cafes_name_trgm ON cafes USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_roasters_name_trgm ON roasters USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_beans_name_trgm ON coffee_beans USING gin(name gin_trgm_ops);
