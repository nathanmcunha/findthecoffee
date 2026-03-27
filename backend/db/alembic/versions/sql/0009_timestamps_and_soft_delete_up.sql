-- Migration 0009: Add Timestamps and Data Quality

-- Add timestamp columns
ALTER TABLE cafes
    ADD COLUMN created_at TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();

ALTER TABLE roasters
    ADD COLUMN created_at TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();

ALTER TABLE coffee_beans
    ADD COLUMN created_at TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();

-- Auto-update updated_at trigger
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

-- Add soft delete support
ALTER TABLE cafes ADD COLUMN deleted_at TIMESTAMPTZ;
ALTER TABLE roasters ADD COLUMN deleted_at TIMESTAMPTZ;
ALTER TABLE coffee_beans ADD COLUMN deleted_at TIMESTAMPTZ;

-- Create indexes for soft delete filtering
CREATE INDEX idx_cafes_deleted_at ON cafes(deleted_at);
CREATE INDEX idx_roasters_deleted_at ON roasters(deleted_at);
CREATE INDEX idx_beans_deleted_at ON coffee_beans(deleted_at);
