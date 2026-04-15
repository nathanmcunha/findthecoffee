-- Add curation fields to cafes and roasters
-- is_curator_pick: mark venues as personal recommendations
-- source_attribution: track provenance of curation

ALTER TABLE cafes ADD COLUMN IF NOT EXISTS is_curator_pick BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE cafes ADD COLUMN IF NOT EXISTS source_attribution TEXT;
ALTER TABLE roasters ADD COLUMN IF NOT EXISTS is_curator_pick BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE roasters ADD COLUMN IF NOT EXISTS source_attribution TEXT;