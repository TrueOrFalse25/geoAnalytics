-- start of SQL script to create the database schema for the Overpass Project

-- creates a table to store information about countries
CREATE TABLE IF NOT EXISTS countries (
    country_id INTEGER PRIMARY KEY,
    country_name TEXT NOT NULL UNIQUE
);

-- creates a table to store information about grid cells, which are defined by their bounding box coordinates and associated with a country
CREATE TABLE IF NOT EXISTS grid_cells (
    cell_id TEXT PRIMARY KEY,
    country_id INTEGER NOT NULL,
    south REAL NOT NULL,
    west REAL NOT NULL,
    north REAL NOT NULL,
    east REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    downloaded_at TEXT,
    FOREIGN KEY (country_id)
        REFERENCES countries(country_id)
);

-- creates a table to store information about roads, including their OpenStreetMap ID, highway type, name, and geometry
CREATE TABLE IF NOT EXISTS roads (
    road_id INTEGER PRIMARY KEY,
    osm_id INTEGER NOT NULL UNIQUE,
    highway_type TEXT,
    road_name TEXT,
    geometry TEXT NOT NULL
);

-- creates a table to store tags associated with roads, allowing for multiple key-value pairs per road
CREATE TABLE IF NOT EXISTS road_tags (
    road_id INTEGER NOT NULL,
    tag_key TEXT NOT NULL,
    tag_value TEXT,
    PRIMARY KEY (road_id, tag_key),
    FOREIGN KEY (road_id)
        REFERENCES roads(road_id)
);

-- creates a table to establish a many-to-many relationship between grid cells and roads, indicating which roads are present in which grid cells
CREATE TABLE IF NOT EXISTS cell_roads (
    cell_id TEXT NOT NULL,
    road_id INTEGER NOT NULL,
    PRIMARY KEY (cell_id, road_id),
    FOREIGN KEY (cell_id)
        REFERENCES grid_cells(cell_id),
    FOREIGN KEY (road_id)
        REFERENCES roads(road_id)
);