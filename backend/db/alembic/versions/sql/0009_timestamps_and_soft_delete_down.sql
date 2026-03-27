-- Migration 0009: Add Timestamps and Soft Delete (DOWN)

-- Drop indexes
DROP INDEX IF EXISTS idx_beans_deleted_at;
DROP INDEX IF EXISTS idx_roasters_deleted_at;
DROP INDEX IF EXISTS idx_cafes_deleted_at;

-- Drop triggers
DROP TRIGGER IF EXISTS trg_beans_updated ON coffee_beans;
DROP TRIGGER IF EXISTS trg_roasters_updated ON roasters;
DROP TRIGGER IF EXISTS trg_cafes_updated ON cafes;

-- Drop function
DROP FUNCTION IF EXISTS set_updated_at();

-- Drop columns
ALTER TABLE coffee_beans DROP COLUMN IF EXISTS deleted_at, DROP COLUMN IF EXISTS updated_at, DROP COLUMN IF EXISTS created_at;
ALTER TABLE roasters DROP COLUMN IF EXISTS deleted_at, DROP COLUMN IF EXISTS updated_at, DROP COLUMN IF EXISTS created_at;
ALTER TABLE cafes DROP COLUMN IF EXISTS deleted_at, DROP COLUMN IF EXISTS updated_at, DROP COLUMN IF EXISTS created_at;
