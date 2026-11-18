
import json
import sqlite3
import time
from pathlib import Path

import folium

# Locate the database
project_folder = Path(__file__).resolve().parent
database_file = project_folder / "roads.db"

# Connect to SQLite
connection = sqlite3.connect(database_file)

# Retrieve Honduras roads from SQL
query = """
SELECT r.osm_id, r.geometry
FROM roads AS r
JOIN country_roads AS cr
    ON r.road_id = cr.road_id
JOIN countries AS c
    ON cr.country_id = c.country_id
WHERE c.country_name = ?
"""

# Measure how long the SQL query takes
start = time.perf_counter()

roads = connection.execute(
    query, ("Honduras",)
).fetchall()

query_time = time.perf_counter() - start

connection.close()

# Create map centered near Tegucigalpa
road_map = folium.Map(
    location=[14.084, -87.208],
    zoom_start=13
)

# Convert SQL geometry into GeoJSON
features = []

for osm_id, geometry_text in roads:
    features.append({
        "type": "Feature",
        "properties": {"osm_id": osm_id},
        "geometry": json.loads(geometry_text)
    })

road_data = {
    "type": "FeatureCollection",
    "features": features
}

# Add roads to the map
roads_layer = folium.GeoJson(
    road_data,
    name="Honduras Roads",
    style_function=lambda feature: {
        "color": "red",
        "weight": 4,
        "opacity": 1
    }
)

roads_layer.add_to(road_map)

# Automatically zoom to the roads
road_map.fit_bounds(roads_layer.get_bounds())

folium.LayerControl().add_to(road_map)

# Save map as HTML
output_file = project_folder / "honduras_roads_map.html"
road_map.save(str(output_file))

print("Map created successfully!")
print(f"Total roads: {len(roads)}")
print(f"SQL query time: {query_time:.6f} seconds")
print(f"Map saved to: {output_file}")
