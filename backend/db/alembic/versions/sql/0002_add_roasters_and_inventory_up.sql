-- Migration: Add roasters and cafe_inventory, refactor coffee_beans
-- Up Migration

-- 1. Create Roasters table
CREATE TABLE IF NOT EXISTS roasters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    location TEXT
);

-- 2. Add roaster_id to coffee_beans (Nullable for now to allow migration)
ALTER TABLE coffee_beans ADD COLUMN roaster_id INTEGER REFERENCES roasters(id);

-- 3. Create Cafe Inventory (M:N) join table
CREATE TABLE IF NOT EXISTS cafe_inventory (
    cafe_id INTEGER REFERENCES cafes(id) ON DELETE CASCADE,
    bean_id INTEGER REFERENCES coffee_beans(id) ON DELETE CASCADE,
    PRIMARY KEY (cafe_id, bean_id)
);

-- 4. Data Migration (Optional/Best Effort)
-- If we had beans linked to cafes, we could create an inventory entry for them.
-- Since this is a schema shift, we'll link existing beans to their cafes in the inventory table.
INSERT INTO cafe_inventory (cafe_id, bean_id)
SELECT cafe_id, id FROM coffee_beans WHERE cafe_id IS NOT NULL;

-- 5. Finalize coffee_beans refactor
-- Remove the direct cafe_id from beans as they now live in the inventory table
ALTER TABLE coffee_beans DROP COLUMN cafe_id;
