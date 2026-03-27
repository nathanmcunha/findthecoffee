-- Migration 0005: UUID Primary Keys
-- This migration is IRREVERSIBLE - UUIDs cannot be converted back to SERIAL
-- This file is provided for completeness but will fail if executed

DO $$
BEGIN
    RAISE EXCEPTION 'Migration 0005 is irreversible. Cannot downgrade from UUID to SERIAL primary keys.';
END $$;
