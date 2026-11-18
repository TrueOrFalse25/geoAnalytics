# geoAnalytics Roads Project

## Project Overview

This project investigates how to extract, filter, store, and manage OpenStreetMap (OSM) road data using Python, the Overpass API, Osmium, and SQLite.

The main goals are to:
- Extract candidate car-passable roads from OSM.
- Store road geometries and attributes in SQLite.
- Track geographic grid-cell downloads and failures.
- Measure download times, processing performance, and storage requirements.
- Estimate the feasibility of collecting worldwide road data.
- Investigate daily incremental updates.

## Tools and Technologies

- Python
- SQLite
- OpenStreetMap
- Overpass API
- Osmium
- Geofabrik
- GeoJSON
- QGIS

## Road Extraction Methods

### Method 1: Overpass API

The original approach downloads roads using geographic bounding boxes divided into grid cells.

The Python downloader:
- Queries OSM road data through the Overpass API.
- Filters selected highway types and access restrictions.
- Stores road geometries and attributes.
- Tracks completed, failed, and pending grid cells.
- Retries failed requests and supports smaller grid subdivisions.

Public Overpass testing encountered repeated HTTP 504 timeout errors, making large-scale downloading difficult.

### Method 2: Geofabrik and Osmium

A second approach downloads complete country-level OSM extracts from Geofabrik.

Osmium is used to extract selected highway types and export road geometries to GeoJSON sequences. Python then applies additional filtering and imports the results into SQLite.

This approach was benchmarked using Honduras and Jamaica.

## Candidate Car-Passable Road Filtering

Included road categories:
- Motorway, trunk, primary, secondary, and tertiary roads, including their link types.
- Residential, service, unclassified, and living-street roads.
- Tracks tagged with `tracktype=grade1`.

Excluded:
- Features tagged `area=yes`.
- Roads explicitly tagged `access=no`, `vehicle=no`, `motor_vehicle=no`, or `motorcar=no`.

These rules identify candidate car-passable roads. They do not guarantee that every selected road is physically passable or legally accessible by car.

OSM coverage may also be incomplete.

## Country Benchmarks

Complete country-level OSM extracts were downloaded and processed for Honduras and Jamaica.

| Metric | Honduras | Jamaica |
|---|---:|---:|
| Original OSM download | 74.38 MB | 38.66 MB |
| Candidate road ways | 180,791 | 59,563 |
| Filtered road ways | 160,891 | 54,820 |
| Geometry storage | 72.33 MB | 23.44 MB |
| SQLite database size | 93.12 MB | 30.18 MB |
| Download time | 42.65 sec | 34.00 sec |
| Extraction time | 1.005 sec | 0.916 sec |
| GeoJSON export time | 1.303 sec | 0.716 sec |
| Filter and SQLite import time | 3.122 sec | 1.836 sec |
| Total measured time | 48.08 sec | 37.47 sec |

Combined results:
- 215,711 filtered road ways.
- 95.78 MB of geometry data.
- 123.30 MB of SQLite database storage.
- 85.55 seconds of combined measured processing time.
- Approximately 571.61 bytes of SQLite storage per road way.

The benchmark databases were created separately from the original `roads.db`.

## Worldwide Storage Estimate

An initial project estimate suggested approximately 60 GB for worldwide road storage.

Using the Honduras and Jamaica benchmarks:

- Average SQLite storage: 571.61 bytes per road way.
- Hypothetical capacity of 60 GB: approximately 105 million road ways.

This is a storage-capacity estimate, not a verified worldwide road count or final database size.

Worldwide storage requirements depend on the number of mapped road ways, geometry complexity, database structure, and indexing.

## Worldwide Overpass Download Estimates

A theoretical global grid contains:

| Grid resolution | Worldwide cells |
|---|---:|
| 1 degree | 64,800 |
| 0.5 degree | 259,200 |
| 0.1 degree | 6,480,000 |

For a 1-degree grid with sequential requests:

| Average time per cell | Estimated duration |
|---|---:|
| 2 seconds | 1.5 days |
| 10 seconds | 7.5 days |
| 30 seconds | 22.5 days |
| 78 seconds | 58.5 days |

These are hypothetical scenarios, not validated worldwide download durations.

Actual performance depends on server limits, geographic coverage, request failures, retries, and grid subdivision.

Earlier Overpass testing recorded repeated HTTP 504 errors and significant retry delays.

## Local Download Performance

Measured download speeds:
- Honduras: approximately 1.74 MB/s.
- Jamaica: approximately 1.14 MB/s.
- Average: approximately 1.44 MB/s.

At this average speed, transferring a hypothetical 60 GB would take approximately 11.57 hours.

This calculation does not represent the actual time needed to download and process the complete worldwide OSM dataset.

Country-level benchmarks suggest that bulk OSM extracts are more practical for large-scale collection than relying exclusively on public Overpass grid requests.

A locally hosted Overpass server has not yet been benchmarked.

## SQLite Database

The original project database stores road data and tracks geographic download progress.

Its tables include:
- `countries`
- `roads`
- `road_tags`
- `grid_cells`
- `country_roads`
- `cell_roads`

The country benchmarks use separate SQLite databases with road IDs, OSM IDs, highway types, names, and GeoJSON geometries.

## Incremental Updates

Investigated OSM replication updates as an alternative to downloading entire datasets repeatedly.

Verified:
- Geofabrik provides replication metadata.
- Jamaica's downloaded extract reported sequence number 3210.
- The corresponding numbered change file was accessible.
- Osmium supports applying OSM change files using `apply-changes`.

Proposed workflow:
1. Download the initial OSM dataset.
2. Record the replication sequence number.
3. Check periodically for newer change files.
4. Download and apply missing updates in sequence.
5. Rebuild affected road geometries and update SQLite records.
6. Save the latest successfully processed checkpoint.

The complete automated update workflow has not yet been implemented or tested.

## Limitations

- OSM may not contain every real-world road.
- Road tags cannot guarantee physical or legal car accessibility.
- Worldwide storage estimates are based on only two countries.
- Public Overpass performance varies by server, region, and request size.
- The full worldwide dataset has not been downloaded.
- Local Overpass infrastructure and automated incremental updates have not been benchmarked.

## Future Work

- Improve the accuracy of car-passability filtering.
- Develop automated incremental updates for SQLite.
- Benchmark the lab's local Overpass server when available.
- Improve global storage estimates using independent worldwide road counts.
- Add automated performance logging and reporting.

## Project Status

Completed:
- Country-level extraction benchmarks for Honduras and Jamaica.
- SQLite storage measurements.
- Preliminary worldwide storage and download-time estimates.
- Investigation of public Overpass failures and replication update availability.

Remaining:
- Validate worldwide road counts and storage requirements.
- Test local Overpass infrastructure.
- Implement and validate automated incremental updates.
