# this code creates and sets up SQLite database (roads.db) so there is a place to store and organize 
# road information from Overpass
import sqlite3
from pathlib import Path

# Locate the project folder
project_folder = Path(__file__).resolve().parent

# Database and SQL file paths
database_file = project_folder / "roads.db"
sql_file = project_folder / "create_database.sql"

# Connect to SQLite
connection = sqlite3.connect(database_file)

# Enable foreign key constraints
connection.execute("PRAGMA foreign_keys = ON")

# Read and execute the SQL commands
with sql_file.open("r", encoding="utf-8") as file:
    sql_script = file.read()

connection.executescript(sql_script)

# Save and close the database
connection.commit()
connection.close()

print("Database created successfully!")
print(f"Database location: {database_file}")