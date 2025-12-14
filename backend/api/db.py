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
        self.con = duckdb.connect(str(DB_PATH), read_only=False)
        self.init_tables()

    def init_tables(self):
        cursor = self.con.cursor()
        
        # LIVE VEHICLES - Current Snapshot
        cursor.execute("""
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

        # LIVE PREDICTIONS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS realtime_predictions (
                trip_id VARCHAR,
                stop_id VARCHAR,
                stop_sequence INTEGER,
                arrival_time TIMESTAMP,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # RAW LOG - For 24h History
        # No Primary Key, optimized for fast inserts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_vehicle_position_log (
                vehicle_id VARCHAR,
                route_id VARCHAR,
                direction_id INTEGER,
                latitude DOUBLE,
                longitude DOUBLE,
                speed DOUBLE,
                timestamp TIMESTAMP
            )
        """)

        # AGGREGATED METRICS - Permanent Storage
        # Aggregates speed and volume per route, per hour
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_route_stats_hourly (
                log_date DATE,
                hour_of_day INTEGER,
                route_id VARCHAR,
                avg_speed_kph DOUBLE,
                max_speed_kph DOUBLE,
                active_vehicle_count INTEGER,
                total_samples INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (log_date, hour_of_day, route_id)
            )
        """)
        
        cursor.close()

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