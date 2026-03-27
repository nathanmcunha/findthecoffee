-- Migration 0008: Refactor FTS to use inline tsvector column (DOWN)

-- Drop trigger and function
DROP TRIGGER IF EXISTS trg_cafe_search_vector ON cafes;
DROP FUNCTION IF EXISTS update_cafe_search_vector();

-- Drop index and column
DROP INDEX IF EXISTS idx_cafes_search_vector;
ALTER TABLE cafes DROP COLUMN IF EXISTS search_vector;

-- Recreate original materialized view system
CREATE MATERIALIZED VIEW coffee_search_index AS
SELECT
    c.id AS cafe_id,
    c.name AS cafe_name,
    setweight(to_tsvector('portuguese', COALESCE(c.name, '')), 'A') ||
    setweight(to_tsvector('portuguese', COALESCE(c.location, '')), 'B') ||
    setweight(to_tsvector('portuguese', COALESCE(string_agg(DISTINCT r.name, ' '), '')), 'C') ||
    setweight(to_tsvector('portuguese', COALESCE(string_agg(DISTINCT b.name, ' '), '')), 'D') AS search_document
FROM cafes c
LEFT JOIN cafe_inventory i ON i.cafe_id = c.id
LEFT JOIN coffee_beans b ON i.bean_id = b.id
LEFT JOIN roasters r ON b.roaster_id = r.id
GROUP BY c.id, c.name, c.location;

CREATE INDEX idx_coffee_search ON coffee_search_index USING GIN(search_document);
CREATE UNIQUE INDEX idx_coffee_search_cafe_id ON coffee_search_index(cafe_id);

CREATE OR REPLACE FUNCTION refresh_coffee_search_index()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY coffee_search_index;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_refresh_fts_cafes
AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON cafes
FOR EACH STATEMENT EXECUTE FUNCTION refresh_coffee_search_index();

CREATE TRIGGER trg_refresh_fts_beans
AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON coffee_beans
FOR EACH STATEMENT EXECUTE FUNCTION refresh_coffee_search_index();

CREATE TRIGGER trg_refresh_fts_inventory
AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON cafe_inventory
FOR EACH STATEMENT EXECUTE FUNCTION refresh_coffee_search_index();
