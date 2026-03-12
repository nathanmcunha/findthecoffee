DROP TRIGGER IF EXISTS trg_refresh_fts_inventory ON cafe_inventory;
DROP TRIGGER IF EXISTS trg_refresh_fts_beans ON coffee_beans;
DROP TRIGGER IF EXISTS trg_refresh_fts_cafes ON cafes;
DROP FUNCTION IF EXISTS refresh_coffee_search_index();
