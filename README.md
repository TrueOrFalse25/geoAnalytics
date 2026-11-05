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


## SQLite Database (as of 10/28/2026 with download + tracking updates)
Added a SQLite database to store road data downloaded from the Overpass API and track the progress of each grid cell.

### Changes
- `create_database.sql` creates tables for countries, roads, road tags, grid cells, and road-to-cell relationships.
- `database.py` handles database setup, road storage, and grid-cell status updates.
- `import_roads.py` imports existing GeoJSON road data into SQLite.
- `download_roads.py` now saves downloaded roads and records whether each grid cell is completed, failed, or pending.
- `combine_roads.py` combines successful downloads and removes duplicate roads.

### Current Progress
- Imported 795 existing Honduras road features into `roads.db`.
- Tested the downloader using a small 2×2 grid.
- Successfully downloaded 131 roads from one grid cell.
- Recorded another cell as failed after a `504 Gateway Time-out`, while two cells remain pending.
- Created `grid_test_roads.geojson` to view the successful download in QGIS.

### Next Steps
- Retry unfinished grid cells.
- Connect to the lab’s local Overpass server.
- Test larger grids and continue developing the grid-processing algorithm.