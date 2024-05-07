CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);
CREATE TABLE plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    latin_name TEXT NOT NULL,
    api_id TEXT NOT NULL UNIQUE
);
CREATE TABLE intake_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    plant_id TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    alias TEXT,
    date_acquired TEXT NOT NULL,
    acquire_method TEXT,
    acquire_from TEXT,
    notes TEXT,
    UNIQUE(owner_id, alias),
    FOREIGN KEY(owner_id) REFERENCES users(id),
    FOREIGN KEY(plant_id) REFERENCES plants(id)
);
CREATE TABLE event_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE
);
INSERT INTO event_type ("name") VALUES
    ('Acquired'),
    ('Watering'),
    ('Fertilizing'),
    ('Treatment'),
    ('Repotting'),
    ('Death')
;
CREATE TABLE event_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    owner_id INTEGER NOT NULL,
    plant_alias TEXT NOT NULL,
    event_type INTEGER NOT NULL,
    event_date TEXT NOT NULL,
    entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    additional_details TEXT,
    FOREIGN KEY(owner_id, plant_alias) REFERENCES intake_details(owner_id, alias),
    FOREIGN KEY(event_type) REFERENCES event_type(id)
);
