-- Migration 0010: Add Coffee Bean Technical Details (Ficha Técnica)

-- Add technical detail columns to coffee_beans table
ALTER TABLE coffee_beans
    ADD COLUMN variety VARCHAR(100),           -- e.g., Bourbon, Catuaí, Mundo Novo
    ADD COLUMN processing VARCHAR(50),         -- e.g., Natural, Pulped Natural, Washed
    ADD COLUMN altitude INTEGER,               -- meters above sea level
    ADD COLUMN producer VARCHAR(200),          -- producer/farm name
    ADD COLUMN farm VARCHAR(200),              -- specific farm name
    ADD COLUMN region VARCHAR(200),            -- growing region (e.g., Sul de Minas)
    ADD COLUMN tasting_notes TEXT[],           -- array of sensory notes
    ADD COLUMN acidity INTEGER CHECK (acidity >= 1 AND acidity <= 5),
    ADD COLUMN sweetness INTEGER CHECK (sweetness >= 1 AND sweetness <= 5),
    ADD COLUMN body INTEGER CHECK (body >= 1 AND body <= 5);

-- Add indexes for common search filters
CREATE INDEX idx_coffee_beans_variety ON coffee_beans(variety);
CREATE INDEX idx_coffee_beans_processing ON coffee_beans(processing);
CREATE INDEX idx_coffee_beans_region ON coffee_beans(region);
CREATE INDEX idx_coffee_beans_altitude ON coffee_beans(altitude);

-- Add GIN index for tasting_notes array (supports contains queries)
CREATE INDEX idx_coffee_beans_tasting_notes ON coffee_beans USING GIN (tasting_notes);
