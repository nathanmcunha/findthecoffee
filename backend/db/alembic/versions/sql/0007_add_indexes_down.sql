-- Migration 0007: Add Missing Indexes (DOWN)

DROP INDEX IF EXISTS idx_beans_name_trgm;
DROP INDEX IF EXISTS idx_roasters_name_trgm;
DROP INDEX IF EXISTS idx_cafes_name_trgm;
DROP INDEX IF EXISTS idx_beans_origin_trgm;
DROP INDEX IF EXISTS idx_beans_roast_level;
DROP INDEX IF EXISTS idx_inventory_bean_id;
DROP INDEX IF EXISTS idx_beans_roaster_id;

-- Note: Not dropping pg_trgm extension as it may be used elsewhere
