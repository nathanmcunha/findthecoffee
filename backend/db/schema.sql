-- Fresh installation schema (v3: UUID Primary Keys)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS roasters (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    location TEXT
);

CREATE TABLE IF NOT EXISTS cafes (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name VARCHAR(255) NOT NULL,
    location TEXT,
    website VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS coffee_beans (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name VARCHAR(255) NOT NULL,
    roast_level VARCHAR(50),
    origin VARCHAR(100),
    roaster_id UUID REFERENCES roasters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS cafe_inventory (
    cafe_id UUID REFERENCES cafes(id) ON DELETE CASCADE,
    bean_id UUID REFERENCES coffee_beans(id) ON DELETE CASCADE,
    PRIMARY KEY (cafe_id, bean_id)
);
