# this code creates and sets up SQLite database (roads.db) so there is a place to store and organize 
# road information from Overpass
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import json

# Locate the project folder
project_folder = Path(__file__).resolve().parent

# Database and SQL file paths
database_file = project_folder / "roads.db"
sql_file = project_folder / "create_database.sql"

# # Connect to SQLite
# connection = sqlite3.connect(database_file)

# # Enable foreign key constraints
# connection.execute("PRAGMA foreign_keys = ON")

# # Read and execute the SQL commands
# with sql_file.open("r", encoding="utf-8") as file:
#     sql_script = file.read()

# connection.executescript(sql_script)

# # Save and close the database
# connection.commit()
# connection.close()

# print("Database created successfully!")
# print(f"Database location: {database_file}")

def utc_now():
    '''Return the current time in UTC for database records.'''
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def connect_database():
    '''Open roads.db with foreign-key enforcement enabled.'''
    connection = sqlite3.connect(database_file)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')

    return connection


def add_missing_columns(connection):
    '''Upgrade an older roads.db without deleting its data.'''
    grid_columns = {
        row['name']
        for row in connection.execute(
            'PRAGMA table_info(grid_cells)'
        )
    }

    grid_additions = {
        'attempt_count': 'INTEGER NOT NULL DEFAULT 0',
        'feature_count': 'INTEGER',
        'raw_file': 'TEXT',
        'last_error': 'TEXT',
        'last_attempted_at': 'TEXT',
        'updated_at': 'TEXT',
        'parent_cell_id': (
            'TEXT REFERENCES grid_cells(cell_id)'
        ),
    }

    for column_name, definition in grid_additions.items():
        if column_name not in grid_columns:
            connection.execute(
                f'''
                ALTER TABLE grid_cells
                ADD COLUMN {column_name} {definition}
                '''
            )

    road_columns = {
        row['name']
        for row in connection.execute(
            'PRAGMA table_info(roads)'
        )
    }

    if 'updated_at' not in road_columns:
        connection.execute(
            'ALTER TABLE roads ADD COLUMN updated_at TEXT'
        )

    timestamp = utc_now()

    connection.execute(
        '''
        UPDATE grid_cells
        SET updated_at = ?
        WHERE updated_at IS NULL
        ''',
        (timestamp,)
    )

    connection.execute(
        '''
        UPDATE roads
        SET updated_at = ?
        WHERE updated_at IS NULL
        ''',
        (timestamp,)
    )

def initialize_database():
    '''Create a new database or safely update an older one.'''
    with connect_database() as connection:
        sql_script = sql_file.read_text(encoding='utf-8')
        connection.executescript(sql_script)
        add_missing_columns(connection)

def get_or_create_country(connection, country_name):
    '''Return a country ID, creating the country if necessary.'''
    connection.execute(
        '''
        INSERT OR IGNORE INTO countries (country_name)
        VALUES (?)
        ''',
        (country_name,)
    )

    row = connection.execute(
        '''
        SELECT country_id
        FROM countries
        WHERE country_name = ?
        ''',
        (country_name,)
    ).fetchone()

    return row['country_id']


def register_cell(
    cell_id,
    country_name,
    south,
    west,
    north,
    east,
    parent_cell_id=None
):
    '''Add a geographic cell without erasing existing progress.'''
    if south >= north:
        raise ValueError(
            f'South must be below north for {cell_id}.'
        )

    if west >= east:
        raise ValueError(
            f'West must be left of east for {cell_id}.'
        )

    timestamp = utc_now()

    with connect_database() as connection:
        country_id = get_or_create_country(
            connection,
            country_name
        )

        connection.execute(
            '''
            INSERT INTO grid_cells (
                cell_id,
                country_id,
                south,
                west,
                north,
                east,
                parent_cell_id,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(cell_id) DO UPDATE SET
                country_id = excluded.country_id,
                south = excluded.south,
                west = excluded.west,
                north = excluded.north,
                east = excluded.east,
                parent_cell_id = excluded.parent_cell_id,
                updated_at = excluded.updated_at
            ''',
            (
                cell_id,
                country_id,
                south,
                west,
                north,
                east,
                parent_cell_id,
                timestamp
            )
        )


def get_cell_status(cell_id):
    '''Return a cell status or None if it is not registered.'''
    with connect_database() as connection:
        row = connection.execute(
            '''
            SELECT status
            FROM grid_cells
            WHERE cell_id = ?
            ''',
            (cell_id,)
        ).fetchone()

    if row is None:
        return None

    return row['status']

def mark_cell_downloading(cell_id):
    '''Record the beginning of a cell download attempt.'''
    timestamp = utc_now()

    with connect_database() as connection:
        cursor = connection.execute(
            '''
            UPDATE grid_cells
            SET status = 'downloading',
                attempt_count = attempt_count + 1,
                last_attempted_at = ?,
                last_error = NULL,
                updated_at = ?
            WHERE cell_id = ?
            ''',
            (timestamp, timestamp, cell_id)
        )

        if cursor.rowcount == 0:
            raise KeyError(
                f'Cell is not registered: {cell_id}'
            )


def mark_cell_completed(
    cell_id,
    feature_count,
    raw_file
):
    '''Record a successfully downloaded and stored cell.'''
    timestamp = utc_now()

    with connect_database() as connection:
        cursor = connection.execute(
            '''
            UPDATE grid_cells
            SET status = 'completed',
                feature_count = ?,
                raw_file = ?,
                downloaded_at = ?,
                last_error = NULL,
                updated_at = ?
            WHERE cell_id = ?
            ''',
            (
                feature_count,
                str(raw_file),
                timestamp,
                timestamp,
                cell_id
            )
        )

        if cursor.rowcount == 0:
            raise KeyError(
                f'Cell is not registered: {cell_id}'
            )


def mark_cell_failed(cell_id, error_message):
    '''Record why a cell download failed.'''
    timestamp = utc_now()

    with connect_database() as connection:
        cursor = connection.execute(
            '''
            UPDATE grid_cells
            SET status = 'failed',
                last_error = ?,
                updated_at = ?
            WHERE cell_id = ?
            ''',
            (
                str(error_message),
                timestamp,
                cell_id
            )
        )

        if cursor.rowcount == 0:
            raise KeyError(
                f'Cell is not registered: {cell_id}'
            )

def store_roads_for_cell(cell_id, elements):
    '''
    Store OSM roads, their tags, and their relationship
    to a downloaded grid cell.
    '''
    stored_count = 0
    timestamp = utc_now()

    with connect_database() as connection:
        cell = connection.execute(
            '''
            SELECT cell_id
            FROM grid_cells
            WHERE cell_id = ?
            ''',
            (cell_id,)
        ).fetchone()

        if cell is None:
            raise KeyError(
                f'Cell is not registered: {cell_id}'
            )

        for element in elements:
            if element.get('type') != 'way':
                continue

            osm_id = int(element['id'])
            geometry = element.get('geometry', [])
            tags = element.get('tags', {})

            if len(geometry) < 2:
                raise ValueError(
                    f'OSM way {osm_id} has incomplete geometry.'
                )

            connection.execute(
                '''
                INSERT INTO roads (
                    osm_id,
                    highway_type,
                    road_name,
                    geometry,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(osm_id) DO UPDATE SET
                    highway_type = excluded.highway_type,
                    road_name = excluded.road_name,
                    geometry = excluded.geometry,
                    updated_at = excluded.updated_at
                ''',
                (
                    osm_id,
                    tags.get('highway'),
                    tags.get('name'),
                    json.dumps(geometry),
                    timestamp
                )
            )

            road = connection.execute(
                '''
                SELECT road_id
                FROM roads
                WHERE osm_id = ?
                ''',
                (osm_id,)
            ).fetchone()

            road_id = road['road_id']

            # Replace the saved tag set so outdated tags do not remain
            connection.execute(
                '''
                DELETE FROM road_tags
                WHERE road_id = ?
                ''',
                (road_id,)
            )

            tag_rows = [
                (
                    road_id,
                    key,
                    str(value)
                )
                for key, value in tags.items()
            ]

            if tag_rows:
                connection.executemany(
                    '''
                    INSERT INTO road_tags (
                        road_id,
                        tag_key,
                        tag_value
                    )
                    VALUES (?, ?, ?)
                    ''',
                    tag_rows
                )

            connection.execute(
                '''
                INSERT OR IGNORE INTO cell_roads (
                    cell_id,
                    road_id
                )
                VALUES (?, ?)
                ''',
                (cell_id, road_id)
            )

            stored_count += 1

    return stored_count

if __name__ == '__main__':
    initialize_database()

    print('Database created or updated successfully!')
    print(f'Database location: {database_file}')