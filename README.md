# geoAnalytics Roads Project 

## SQLite Database

Added SQLite to store and organize road data downloaded from the Overpass API.

## New Files

* create_database.sql – Creates five tables for countries, roads, road tags, grid cells, and road-to-cell relationships.

* database.py – Initializes the SQLite database (roads.db).

* import_roads.py – Imports existing GeoJSON road data into SQLite.

## Current Progress

* Successfully imported 795 unique road features from Honduras.

* Stored road IDs, highway types, names, coordinates, and additional OpenStreetMap tags.

* Verified the database using SQL queries.

* Database is currently stored locally.

## Next Steps

* Connect SQLite to download_roads.py to automatically store downloaded roads.

* Track completed and failed grid cells using SQLite.

* Integrate the local Overpass server once the URL becomes available.