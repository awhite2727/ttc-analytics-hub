import duckdb
from pathlib import Path

# Calculate absolute path to warehouse/analytics.duckdb
CURRENT_DIR = Path(__file__).resolve().parent
DB_PATH = CURRENT_DIR.parent.parent / "warehouse" / "analytics.duckdb"

class Database:
    def __init__(self):
        self.con = None

    def connect(self):
        print(f"Connecting to DuckDB at: {DB_PATH}")
        # read_only=False is REQUIRED for real-time updates
        self.con = duckdb.connect(str(DB_PATH), read_only=False)
        self.init_tables()

    def init_tables(self):
        # Create the table to store live vehicle positions
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS realtime_vehicles (
                vehicle_id VARCHAR,
                trip_id VARCHAR,
                route_id VARCHAR,
                direction_id INTEGER,
                latitude DOUBLE,
                longitude DOUBLE,
                bearing DOUBLE,
                speed DOUBLE,
                vehicle_label VARCHAR,
                timestamp TIMESTAMP,
                PRIMARY KEY (vehicle_id)
            )
        """)

    def close(self):
        if self.con:
            self.con.close()
            print("Database connection closed.")

    def get_cursor(self):
        if not self.con:
            self.connect()
        return self.con.cursor()

# Create a global instance
db = Database()