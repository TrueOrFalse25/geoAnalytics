import json
import time
from pathlib import Path

import requests

# Overpass server
url = "https://overpass-api.de/api/interpreter"

# Identify our script to the server
headers = {
    "User-Agent": "Isaac-Honduras-Roads-Research/0.1"
}

# Small areas in Honduras
# Outer boundaries of the new test area
# Start of Grid Test 
south_edge = 14.09
north_edge = 14.10
west_edge = -87.22
east_edge = -87.20

rows = 2
columns = 2

cell_height = (north_edge - south_edge) / rows
cell_width = (east_edge - west_edge) / columns

sections = {}

for row in range(rows):
    for column in range(columns):
        south = round(south_edge + row * cell_height, 6)
        north = round(south_edge + (row + 1) * cell_height, 6)
        west = round(west_edge + column * cell_width, 6)
        east = round(west_edge + (column + 1) * cell_width, 6)

        section_id = f"grid_r{row + 1}_c{column + 1}"
        sections[section_id] = (south, west, north, east)

# Show the sections before downloading
for section_id, bounds in sections.items():
    print(f"{section_id}: {bounds}")

# End of Grid Test 

# Create a downloads folder next to this script
folder = Path(__file__).resolve().parent / "downloads_grid_test"
folder.mkdir(exist_ok=True)

progress_file = folder / "progress.json"

# Read previously saved progress
if progress_file.exists():
    with progress_file.open(encoding="utf-8") as file:
        progress = json.load(file)
else:
    progress = {}


# Save safely using a temporary file
def save_json(path, data):
    temporary = path.with_suffix(".tmp")

    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    temporary.replace(path)


# Download each section
for section_id, bounds in sections.items():
    output_file = folder / f"{section_id}.json"

    if (
        progress.get(section_id) == "completed"
        and output_file.exists()
    ):
        print(f"Skipping {section_id}: already downloaded.")
        continue

    south, west, north, east = bounds

    # Include private roads, preserving their access tags
    query = f"""
    [out:json][timeout:60];
    (
      way
        ["highway"~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|unclassified|residential|service|living_street)$"]
        ["area"!="yes"]
        ["access"!="no"]
        ["vehicle"!="no"]
        ["motor_vehicle"!="no"]
        ["motorcar"!="no"]
        ({south},{west},{north},{east});

      way
        ["highway"="track"]
        ["tracktype"="grade1"]
        ["area"!="yes"]
        ["access"!="no"]
        ["vehicle"!="no"]
        ["motor_vehicle"!="no"]
        ["motorcar"!="no"]
        ({south},{west},{north},{east});
    );
    out geom;
    """

    progress[section_id] = "pending"
    save_json(progress_file, progress)

    completed = False
    max_attempts = 4

    for attempt in range(1, max_attempts + 1):
        print(
            f"Downloading {section_id} "
            f"(attempt {attempt}/{max_attempts})..."
        )

        retryable = False
        retry_after = 0

        try:
            response = requests.post(
                url,
                data={"data": query},
                headers=headers,
                timeout=90
            )

            # Retry temporary server errors and rate limits
            retryable = response.status_code in {
                429, 500, 502, 503, 504
            }

            # Respect a server-requested delay given in seconds
            delay_header = response.headers.get("Retry-After", "")
            if delay_header.isdigit():
                retry_after = int(delay_header)

            response.raise_for_status()
            data = response.json()

            if "remark" in data:
                raise ValueError(data["remark"])

            if "elements" not in data:
                raise ValueError("The response is missing its data.")

            save_json(output_file, data)

            progress[section_id] = "completed"
            save_json(progress_file, progress)

            print(
                f"Saved {section_id}: "
                f"{len(data['elements'])} features."
            )

            completed = True
            break

        except (requests.Timeout, requests.ConnectionError) as error:
            retryable = True
            print(f"Connection problem: {error}")

        except (requests.RequestException, ValueError) as error:
            print(f"Download failed: {error}")

        # Stop immediately for other errors, or after the last attempt
        if not retryable or attempt == max_attempts:
            break

        wait_seconds = max(60 * (2 ** (attempt - 1)), retry_after)
        print(f"Waiting {wait_seconds} seconds before retrying...")
        time.sleep(wait_seconds)

    if not completed:
        progress[section_id] = "failed"
        save_json(progress_file, progress)
        print(f"Stopping at {section_id}. Progress is saved.")
        break

    # Pause before requesting another section
    time.sleep(30)

print(f"Run finished. Check {progress_file}")