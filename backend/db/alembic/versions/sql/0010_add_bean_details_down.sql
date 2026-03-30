-- Migration 0010 Downgrade: Remove Coffee Bean Technical Details

-- Drop indexes
DROP INDEX IF EXISTS idx_coffee_beans_tasting_notes;
DROP INDEX IF EXISTS idx_coffee_beans_altitude;
DROP INDEX IF EXISTS idx_coffee_beans_region;
DROP INDEX IF EXISTS idx_coffee_beans_processing;
DROP INDEX IF EXISTS idx_coffee_beans_variety;

-- Remove technical detail columns
ALTER TABLE coffee_beans
    DROP COLUMN IF EXISTS body,
    DROP COLUMN IF EXISTS sweetness,
    DROP COLUMN IF EXISTS acidity,
    DROP COLUMN IF EXISTS tasting_notes,
    DROP COLUMN IF EXISTS region,
    DROP COLUMN IF EXISTS farm,
    DROP COLUMN IF EXISTS producer,
    DROP COLUMN IF EXISTS altitude,
    DROP COLUMN IF EXISTS processing,
    DROP COLUMN IF EXISTS variety;
