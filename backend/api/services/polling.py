import asyncio
import requests
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
from api.db import db

def cleanup_old_data():
    """
    Cleans up vehicle position data older than 3 days.
    """
    if db.con:
        db.con.execute(
            "DELETE FROM realtime_vehicles WHERE timestamp < current_date - INTERVAL 3 DAY"
        )

async def update_vehicle_positions():
    """
    Polls the TTC GTFS-RT feed every 10 seconds and updates DuckDB.
    """
    VEHICLE_POSITIONS_URL = "https://bustime.ttc.ca/gtfsrt/vehicles"
    
    while True:
        try:
            # Check if DB is connected
            if db.con:
                response = requests.get(VEHICLE_POSITIONS_URL, timeout=10)
                
                if response.status_code == 200:
                    # Parse the Protocol Buffer response
                    feed = gtfs_realtime_pb2.FeedMessage()
                    feed.ParseFromString(response.content)

                    vehicles = []
                    for entity in feed.entity:
                        if entity.HasField('vehicle'):
                            v = entity.vehicle
                            
                            # Extract data safely
                            row = (
                                v.vehicle.id,
                                v.trip.trip_id,
                                v.trip.route_id,
                                v.trip.direction_id if v.trip.HasField('direction_id') else None,
                                v.position.latitude,
                                v.position.longitude,
                                v.position.bearing,
                                v.position.speed,
                                v.vehicle.label,
                            )
                            vehicles.append(row)

                    if vehicles:
                        # Perform a Transactional Update
                        cursor = db.con.cursor()
                        cursor.execute("BEGIN TRANSACTION")
                        cursor.execute("DELETE FROM realtime_vehicles")
                        cursor.executemany("""
                            INSERT INTO realtime_vehicles 
                            (vehicle_id, trip_id, route_id, direction_id, latitude, longitude, bearing, speed, vehicle_label, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, current_timestamp)
                        """, vehicles)
                        cursor.execute("COMMIT")
                        # Optional: Print status
                        # print(f"Synced {len(vehicles)} vehicles.")
                else:
                    print(f"GTFS API Error: {response.status_code}")

        except Exception as e:
            print(f"Polling Error: {e}")
            # Attempt rollback if DB is locked/failed
            try: db.con.execute("ROLLBACK")
            except: pass

        # Wait 10 seconds before next poll
        await asyncio.sleep(10)