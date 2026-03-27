-- Migration 0008: Refactor FTS to use inline tsvector column
-- Replaces materialized view with lightweight per-row tsvector

-- Drop old FTS system
DROP TRIGGER IF EXISTS trg_refresh_fts_inventory ON cafe_inventory;
DROP TRIGGER IF EXISTS trg_refresh_fts_beans ON coffee_beans;
DROP TRIGGER IF EXISTS trg_refresh_fts_cafes ON cafes;
DROP FUNCTION IF EXISTS refresh_coffee_search_index();
DROP MATERIALIZED VIEW IF EXISTS coffee_search_index;

-- Add tsvector column directly to cafes
ALTER TABLE cafes ADD COLUMN search_vector tsvector;

-- Populate initial values
UPDATE cafes c SET search_vector = (
    setweight(to_tsvector('portuguese', COALESCE(c.name, '')), 'A') ||
    setweight(to_tsvector('portuguese', COALESCE(c.location, '')), 'B') ||
    setweight(to_tsvector('portuguese', COALESCE(c.address, '')), 'B')
);

-- GIN index on the column
CREATE INDEX idx_cafes_search_vector ON cafes USING GIN(search_vector);

-- Lightweight trigger: only updates the row being changed
CREATE OR REPLACE FUNCTION update_cafe_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('portuguese', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('portuguese', COALESCE(NEW.location, '')), 'B') ||
        setweight(to_tsvector('portuguese', COALESCE(NEW.address, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cafe_search_vector
    BEFORE INSERT OR UPDATE ON cafes
    FOR EACH ROW EXECUTE FUNCTION update_cafe_search_vector();
