ALTER TABLE cafes DROP COLUMN IF EXISTS is_curator_pick;
ALTER TABLE cafes DROP COLUMN IF EXISTS source_attribution;
ALTER TABLE roasters DROP COLUMN IF EXISTS is_curator_pick;
ALTER TABLE roasters DROP COLUMN IF EXISTS source_attribution;