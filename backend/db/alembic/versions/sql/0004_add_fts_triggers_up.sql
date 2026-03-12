-- 1. Create the Refresh Function
CREATE OR REPLACE FUNCTION refresh_coffee_search_index()
RETURNS TRIGGER AS $$
BEGIN
    -- Refresh the materialized view in the background
    -- CONCURRENTLY requires a unique index on the view (which we have on cafe_id)
    REFRESH MATERIALIZED VIEW CONCURRENTLY coffee_search_index;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 2. Create Triggers for each relevant table
-- We refresh when cafes change
CREATE TRIGGER trg_refresh_fts_cafes
AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON cafes
FOR EACH STATEMENT EXECUTE FUNCTION refresh_coffee_search_index();

-- We refresh when beans change (names, roasters etc)
CREATE TRIGGER trg_refresh_fts_beans
AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON coffee_beans
FOR EACH STATEMENT EXECUTE FUNCTION refresh_coffee_search_index();

-- We refresh when the link between them changes (inventory)
CREATE TRIGGER trg_refresh_fts_inventory
AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON cafe_inventory
FOR EACH STATEMENT EXECUTE FUNCTION refresh_coffee_search_index();
