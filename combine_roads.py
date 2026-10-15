import json
from pathlib import Path

# Folder containing this script
project_folder = Path(__file__).resolve().parent
download_folder = project_folder / "downloads_with_private"

# The four completed downloads
filenames = [
    "cell_001.json",
    "cell_002a.json",
    "cell_002b.json",
    "cell_003.json",
]

unique_roads = {}
total_count = 0

# Read each download
for filename in filenames:
    path = download_folder / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing download: {path}")

    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    if "remark" in data or "elements" not in data:
        raise ValueError(f"Check this download: {filename}")

    for element in data["elements"]:
        if element["type"] == "way":
            total_count += 1

            # Keep only one copy of each OSM way ID
            unique_roads[element["id"]] = element

features = []

# Convert each road into a GeoJSON feature
for osm_id, road in unique_roads.items():
    geometry = road.get("geometry", [])

    if len(geometry) < 2:
        raise ValueError(f"Road {osm_id} is missing its geometry.")

    # GeoJSON coordinates use longitude, then latitude
    coordinates = [
        [point["lon"], point["lat"]]
        for point in geometry
    ]

    properties = dict(road.get("tags", {}))
    properties["osm_id"] = osm_id

    features.append({
        "type": "Feature",
        "id": f"way/{osm_id}",
        "properties": properties,
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        }
    })

# Combine all features into one GeoJSON
geojson = {
    "type": "FeatureCollection",
    "features": features
}

output_file = project_folder / "combined_roads_with_private.geojson"

with output_file.open("w", encoding="utf-8") as file:
    json.dump(geojson, file, indent=2)

print(f"Features before removing duplicates: {total_count}")
print(f"Unique road features: {len(features)}")
print(f"Duplicates removed: {total_count - len(features)}")
print(f"Saved to: {output_file}")
print("Done everything is saved in combined_car_roads.geojson.")