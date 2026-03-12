-- Migration: Add roasters and cafe_inventory, refactor coffee_beans
-- Down Migration

-- 1. Restore cafe_id to coffee_beans
ALTER TABLE coffee_beans ADD COLUMN cafe_id INTEGER REFERENCES cafes(id);

-- 2. Restore data from inventory back to coffee_beans (Best effort)
-- This might be ambiguous if a bean is in multiple cafes, but we pick the first one.
UPDATE coffee_beans 
SET cafe_id = (SELECT cafe_id FROM cafe_inventory WHERE bean_id = coffee_beans.id LIMIT 1);

-- 3. Drop new tables and columns
DROP TABLE IF EXISTS cafe_inventory;
ALTER TABLE coffee_beans DROP COLUMN roaster_id;
DROP TABLE IF EXISTS roasters;
