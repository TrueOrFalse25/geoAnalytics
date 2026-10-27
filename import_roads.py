# this script imports road data from a GeoJSON file into the SQLite database that we made earlier (roads.db), 
# including road tags and handling existing entries.

import json
import sqlite3
from pathlib import Path

# Locate project files
project_folder = Path(__file__).resolve().parent
database_file = project_folder / "roads.db"
geojson_file = project_folder / "combined_roads_with_private.geojson"

# Read the existing road data
with geojson_file.open("r", encoding="utf-8") as file:
    data = json.load(file)

# Connect to SQLite
connection = sqlite3.connect(database_file)
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

try:
    # Add Honduras to the countries table
    cursor.execute(
        "INSERT OR IGNORE INTO countries (country_name) VALUES (?)",
        ("Honduras",)
    )

    # Import each road
    for feature in data["features"]:
        properties = feature["properties"]
        osm_id = int(properties["osm_id"])

        highway_type = properties.get("highway")
        road_name = properties.get("name")
        geometry = json.dumps(feature["geometry"])

        # Insert road, skipping existing IDs
        cursor.execute(
            """
            INSERT OR IGNORE INTO roads
            (osm_id, highway_type, road_name, geometry)
            VALUES (?, ?, ?, ?)
            """,
            (osm_id, highway_type, road_name, geometry)
        )

        # Find the database ID for this road
        cursor.execute(
            "SELECT road_id FROM roads WHERE osm_id = ?",
            (osm_id,)
        )
        road_id = cursor.fetchone()[0]

        # Save all road tags
        for key, value in properties.items():
            if key == "osm_id":
                continue

            cursor.execute(
                """
                INSERT OR REPLACE INTO road_tags
                (road_id, tag_key, tag_value)
                VALUES (?, ?, ?)
                """,
                (road_id, key, str(value))
            )

    connection.commit()

    # Count imported roads
    cursor.execute("SELECT COUNT(*) FROM roads")
    total_roads = cursor.fetchone()[0]

    print("Import completed successfully!")
    print(f"Total roads in database: {total_roads}")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
