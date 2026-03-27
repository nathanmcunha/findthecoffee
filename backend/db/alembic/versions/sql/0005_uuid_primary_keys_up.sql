-- Migration 0005: Convert SERIAL primary keys to UUIDv7
-- This migration is IRREVERSIBLE
-- Requires PostgreSQL 18+ for native uuidv7() function

-- ============================================================
-- STEP 1: Drop FTS triggers and materialized view
-- ============================================================
DROP TRIGGER IF EXISTS trg_refresh_fts_inventory ON cafe_inventory;
DROP TRIGGER IF EXISTS trg_refresh_fts_beans ON coffee_beans;
DROP TRIGGER IF EXISTS trg_refresh_fts_cafes ON cafes;
DROP FUNCTION IF EXISTS refresh_coffee_search_index();
DROP MATERIALIZED VIEW IF EXISTS coffee_search_index;

-- ============================================================
-- STEP 2: Drop foreign key constraints
-- ============================================================
ALTER TABLE coffee_beans DROP CONSTRAINT IF EXISTS coffee_beans_roaster_id_fkey;
ALTER TABLE cafe_inventory DROP CONSTRAINT IF EXISTS cafe_inventory_cafe_id_fkey;
ALTER TABLE cafe_inventory DROP CONSTRAINT IF EXISTS cafe_inventory_bean_id_fkey;

-- ============================================================
-- STEP 3: Add UUID columns to all tables (before converting any)
-- ============================================================
-- roasters
ALTER TABLE roasters ADD COLUMN uuid_id UUID DEFAULT uuidv7();

-- cafes
ALTER TABLE cafes ADD COLUMN uuid_id UUID DEFAULT uuidv7();

-- coffee_beans (pk and fk)
ALTER TABLE coffee_beans ADD COLUMN uuid_id UUID DEFAULT uuidv7();
ALTER TABLE coffee_beans ADD COLUMN uuid_roaster_id UUID;

-- cafe_inventory (both FKs)
ALTER TABLE cafe_inventory ADD COLUMN uuid_cafe_id UUID;
ALTER TABLE cafe_inventory ADD COLUMN uuid_bean_id UUID;

-- ============================================================
-- STEP 4: Populate UUID columns for primary keys
-- ============================================================
UPDATE roasters SET uuid_id = uuidv7();
UPDATE cafes SET uuid_id = uuidv7();
UPDATE coffee_beans SET uuid_id = uuidv7();

-- ============================================================
-- STEP 5: Map foreign keys using old integer columns
-- ============================================================
-- Map coffee_beans.roaster_id -> uuid_roaster_id
UPDATE coffee_beans cb
SET uuid_roaster_id = r.uuid_id
FROM roasters r
WHERE cb.roaster_id = r.id;

-- Map cafe_inventory.cafe_id -> uuid_cafe_id
UPDATE cafe_inventory ci
SET uuid_cafe_id = c.uuid_id
FROM cafes c
WHERE ci.cafe_id = c.id;

-- Map cafe_inventory.bean_id -> uuid_bean_id
UPDATE cafe_inventory ci
SET uuid_bean_id = b.uuid_id
FROM coffee_beans b
WHERE ci.bean_id = b.id;

-- ============================================================
-- STEP 6: Set NOT NULL constraints
-- ============================================================
ALTER TABLE roasters ALTER COLUMN uuid_id SET NOT NULL;
ALTER TABLE cafes ALTER COLUMN uuid_id SET NOT NULL;
ALTER TABLE coffee_beans ALTER COLUMN uuid_id SET NOT NULL;

-- ============================================================
-- STEP 7: Drop old columns
-- ============================================================
ALTER TABLE roasters DROP COLUMN id;
ALTER TABLE cafes DROP COLUMN id;
ALTER TABLE coffee_beans DROP COLUMN id;
ALTER TABLE coffee_beans DROP COLUMN roaster_id;
ALTER TABLE cafe_inventory DROP COLUMN cafe_id;
ALTER TABLE cafe_inventory DROP COLUMN bean_id;

-- ============================================================
-- STEP 8: Rename UUID columns
-- ============================================================
ALTER TABLE roasters RENAME COLUMN uuid_id TO id;
ALTER TABLE cafes RENAME COLUMN uuid_id TO id;
ALTER TABLE coffee_beans RENAME COLUMN uuid_id TO id;
ALTER TABLE coffee_beans RENAME COLUMN uuid_roaster_id TO roaster_id;
ALTER TABLE cafe_inventory RENAME COLUMN uuid_cafe_id TO cafe_id;
ALTER TABLE cafe_inventory RENAME COLUMN uuid_bean_id TO bean_id;

-- ============================================================
-- STEP 9: Add primary keys and foreign key constraints
-- ============================================================
ALTER TABLE roasters ADD PRIMARY KEY (id);
ALTER TABLE cafes ADD PRIMARY KEY (id);
ALTER TABLE coffee_beans ADD PRIMARY KEY (id);

ALTER TABLE coffee_beans ADD CONSTRAINT coffee_beans_roaster_id_fkey 
    FOREIGN KEY (roaster_id) REFERENCES roasters(id) ON DELETE SET NULL;

ALTER TABLE cafe_inventory ADD CONSTRAINT cafe_inventory_cafe_id_fkey 
    FOREIGN KEY (cafe_id) REFERENCES cafes(id) ON DELETE CASCADE;
ALTER TABLE cafe_inventory ADD CONSTRAINT cafe_inventory_bean_id_fkey 
    FOREIGN KEY (bean_id) REFERENCES coffee_beans(id) ON DELETE CASCADE;

-- Add composite PK for cafe_inventory
ALTER TABLE cafe_inventory ADD PRIMARY KEY (cafe_id, bean_id);
