-- Fresh installation schema (v4: Complete schema with all migrations)
-- Note: For production, use Alembic migrations instead of this file.
-- Requires PostgreSQL 18+ for native uuidv7()

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS roasters (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    location TEXT,
    address TEXT,
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS cafes (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name VARCHAR(255) NOT NULL,
    location TEXT,
    website VARCHAR(255),
    address TEXT,
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    search_vector tsvector,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS coffee_beans (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name VARCHAR(255) NOT NULL,
    roast_level VARCHAR(50),
    origin VARCHAR(100),
    roaster_id UUID REFERENCES roasters(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS cafe_inventory (
    cafe_id UUID REFERENCES cafes(id) ON DELETE CASCADE,
    bean_id UUID REFERENCES coffee_beans(id) ON DELETE CASCADE,
    PRIMARY KEY (cafe_id, bean_id)
);

-- ============================================================
-- INDEXES
-- ============================================================

-- FK join indexes
CREATE INDEX IF NOT EXISTS idx_beans_roaster_id ON coffee_beans(roaster_id);
CREATE INDEX IF NOT EXISTS idx_inventory_bean_id ON cafe_inventory(bean_id);

-- Filter indexes
CREATE INDEX IF NOT EXISTS idx_beans_roast_level ON coffee_beans(roast_level);

-- Trigram indexes for ILIKE queries
CREATE INDEX IF NOT EXISTS idx_beans_origin_trgm ON coffee_beans USING gin(origin gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_cafes_name_trgm ON cafes USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_roasters_name_trgm ON roasters USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_beans_name_trgm ON coffee_beans USING gin(name gin_trgm_ops);

-- Geo indexes
CREATE INDEX IF NOT EXISTS idx_cafes_lat_lng ON cafes(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_roasters_lat_lng ON roasters(latitude, longitude);

-- FTS index
CREATE INDEX IF NOT EXISTS idx_cafes_search_vector ON cafes USING GIN(search_vector);

-- Soft delete indexes
CREATE INDEX IF NOT EXISTS idx_cafes_deleted_at ON cafes(deleted_at);
CREATE INDEX IF NOT EXISTS idx_roasters_deleted_at ON roasters(deleted_at);
CREATE INDEX IF NOT EXISTS idx_beans_deleted_at ON coffee_beans(deleted_at);

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cafes_updated
    BEFORE UPDATE ON cafes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_roasters_updated
    BEFORE UPDATE ON roasters
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_beans_updated
    BEFORE UPDATE ON coffee_beans
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- FTS search vector auto-update
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
