-- 1. Create the Materialized View
CREATE MATERIALIZED VIEW coffee_search_index AS
SELECT 
    c.id AS cafe_id,
    c.name AS cafe_name,
    -- Weights: A (Cafe Name) > B (Location) > C (Roaster) > D (Bean Name)
    -- We aggregate roasters and beans to have one row per cafe
    setweight(to_tsvector('portuguese', COALESCE(c.name, '')), 'A') || 
    setweight(to_tsvector('portuguese', COALESCE(c.location, '')), 'B') ||
    setweight(to_tsvector('portuguese', COALESCE(string_agg(DISTINCT r.name, ' '), '')), 'C') ||
    setweight(to_tsvector('portuguese', COALESCE(string_agg(DISTINCT b.name, ' '), '')), 'D') AS search_document
FROM cafes c
LEFT JOIN cafe_inventory i ON i.cafe_id = c.id
LEFT JOIN coffee_beans b ON i.bean_id = b.id
LEFT JOIN roasters r ON b.roaster_id = r.id
GROUP BY c.id, c.name, c.location;

-- 2. Create the GIN Index for fast searching
CREATE INDEX idx_coffee_search ON coffee_search_index USING GIN(search_document);

-- 3. Unique Index (Required for CONCURRENT refreshes)
CREATE UNIQUE INDEX idx_coffee_search_cafe_id ON coffee_search_index(cafe_id);
