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
    cafe_id INTEGER REFERENCES cafes(id)
);
