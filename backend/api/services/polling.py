import asyncio
import requests
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
from api.db import db

# TTC Feed URLs
VEHICLE_POSITIONS_URL = "https://bustime.ttc.ca/gtfsrt/vehicles"
TRIP_UPDATES_URL = "https://bustime.ttc.ca/gtfsrt/trips"

async def update_vehicle_positions():
    """
    Polls TTC GTFS-RT every 10s.
    Updates 'realtime_vehicles' (Snapshot) AND inserts into 'raw_vehicle_position_log' (History).
    """
    
    while True:
        try:
            if db.con:
                response = requests.get(VEHICLE_POSITIONS_URL, timeout=10)
                
                if response.status_code == 200:
                    feed = gtfs_realtime_pb2.FeedMessage()
                    feed.ParseFromString(response.content)

                    snapshot_rows = []
                    history_rows = []

                    for entity in feed.entity:
                        if entity.HasField('vehicle'):
                            v = entity.vehicle
                            
                            # Snapshot Row
                            snapshot_rows.append((
                                v.vehicle.id,
                                v.trip.trip_id,
                                v.trip.route_id,
                                v.trip.direction_id if v.trip.HasField('direction_id') else None,
                                v.position.latitude,
                                v.position.longitude,
                                v.position.bearing,
                                v.position.speed, # m/s
                                v.vehicle.label,
                            ))

                            # History Row (Only what we need for analytics)
                            history_rows.append((
                                v.vehicle.id,
                                v.trip.route_id,
                                v.trip.direction_id if v.trip.HasField('direction_id') else None,
                                v.position.latitude,
                                v.position.longitude,
                                v.position.speed,
                            ))

                    # --- 2. Fetch Trip Updates (Predictions) ---
                    # This provides the "Next 5 stops" logic
                    resp_trip = requests.get(TRIP_UPDATES_URL, timeout=10)
                    prediction_rows = []

                    if resp_trip.status_code == 200:
                        feed_trip = gtfs_realtime_pb2.FeedMessage()
                        feed_trip.ParseFromString(resp_trip.content)

                        for entity in feed_trip.entity:
                            if entity.HasField('trip_update'):
                                tu = entity.trip_update
                                trip_id = tu.trip.trip_id
                                
                                for stu in tu.stop_time_update:
                                    arr_time = datetime.fromtimestamp(stu.arrival.time) if stu.HasField('arrival') else None
                                    dep_time = datetime.fromtimestamp(stu.departure.time) if stu.HasField('departure') else None
                                    
                                    if arr_time or dep_time:
                                        prediction_rows.append((
                                            trip_id,
                                            stu.stop_id,
                                            stu.stop_sequence,
                                            arr_time,
                                            dep_time,
                                            stu.arrival.delay if stu.HasField('arrival') else 0
                                        ))

                    if snapshot_rows or prediction_rows:
                        cursor = db.con.cursor()
                        cursor.execute("BEGIN TRANSACTION")
                        
                        # 1. Update live snapshot
                        cursor.execute("DELETE FROM realtime_vehicles")
                        cursor.executemany("""
                            INSERT INTO realtime_vehicles 
                            (vehicle_id, trip_id, route_id, direction_id, latitude, longitude, bearing, speed, vehicle_label, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, current_timestamp)
                        """, snapshot_rows)

                        # 2. Append to history log
                        cursor.executemany("""
                            INSERT INTO raw_vehicle_position_log
                            (vehicle_id, route_id, direction_id, latitude, longitude, speed, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, current_timestamp)
                        """, history_rows)
                    
                     # Update Predictions (Wipe and replace)
                    if prediction_rows:
                        cursor.execute("DELETE FROM realtime_predictions")
                        cursor.executemany("""
                            INSERT INTO realtime_predictions
                            (trip_id, stop_id, stop_sequence, arrival_time, departure_time, delay, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, current_timestamp)
                        """, prediction_rows)

                        cursor.execute("COMMIT")
                        cursor.close()
                else:
                    print(f"GTFS API Error: {response.status_code}")

        except Exception as e:
            print(f"Polling Error: {e}")
            try: db.con.execute("ROLLBACK")
            except: pass

        await asyncio.sleep(10)