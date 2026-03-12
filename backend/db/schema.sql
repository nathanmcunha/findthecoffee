-- Fresh installation schema (v2: Roaster-Centric)

CREATE TABLE IF NOT EXISTS roasters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    location TEXT
);

CREATE TABLE IF NOT EXISTS cafes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location TEXT,
    website VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS coffee_beans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    roast_level VARCHAR(50),
    origin VARCHAR(100),
    roaster_id INTEGER REFERENCES roasters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS cafe_inventory (
    cafe_id INTEGER REFERENCES cafes(id) ON DELETE CASCADE,
    bean_id INTEGER REFERENCES coffee_beans(id) ON DELETE CASCADE,
    PRIMARY KEY (cafe_id, bean_id)
);
