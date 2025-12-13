from fastapi import APIRouter, HTTPException
from api.db import db

router = APIRouter()

@router.get("/route/{route_id}/stats")
def get_route_stats(route_id: str):
    """
    Returns aggregated stats for a route (AVG Speed, Active Buses)
    plus the most recent hourly log.
    """
    cursor = db.get_cursor()
    
    # 1. Get Live Stats (Right Now)
    live_res = cursor.execute("""
        SELECT COUNT(*), AVG(speed) * 3.6 
        FROM realtime_vehicles 
        WHERE route_id = ?
    """, (route_id,)).fetchone()
    
    active_buses = live_res[0] if live_res else 0
    current_avg_speed = live_res[1] if live_res and live_res[1] else 0

    # 2. Get Historical Stats (Last 24h Average)
    hist_res = cursor.execute("""
        SELECT AVG(avg_speed_kph), MAX(max_speed_kph)
        FROM analytics_route_stats_hourly
        WHERE route_id = ? AND log_date >= current_date - 1
    """, (route_id,)).fetchone()

    return {
        "route_id": route_id,
        "live": {
            "active_buses": active_buses,
            "current_avg_speed_kph": round(current_avg_speed, 1)
        },
        "history_24h": {
            "avg_speed_kph": round(hist_res[0], 1) if hist_res[0] else None,
            "max_speed_kph": round(hist_res[1], 1) if hist_res[1] else None
        }
    }

@router.get("/stop/{stop_id}/predictions")
def get_stop_predictions(stop_id: str):
    """
    Popup: Click a Stop -> See next buses.
    Joins 'realtime_predictions' with 'realtime_vehicles' (to get bus label).
    """
    cursor = db.get_cursor()
    
    # Get next 5 predictions for this stop
    query = """
        SELECT 
            p.trip_id,
            v.route_id,
            v.vehicle_label,
            p.arrival_time,
            (epoch(p.arrival_time) - epoch(current_timestamp)) / 60 as minutes_away,
            p.delay
        FROM realtime_predictions p
        LEFT JOIN realtime_vehicles v ON p.trip_id = v.trip_id
        WHERE p.stop_id = ? 
          AND p.arrival_time > current_timestamp
        ORDER BY p.arrival_time ASC
        LIMIT 5
    """
    
    rows = cursor.execute(query, (stop_id,)).fetchall()
    
    results = []
    for r in rows:
        results.append({
            "trip_id": r[0],
            "route_id": r[1] or "Unknown",
            "vehicle_label": r[2] or "Unknown",
            "arrival_time": r[3],
            "minutes_away": int(r[4]),
            "delay_seconds": r[5]
        })
        
    return {"stop_id": stop_id, "predictions": results}

@router.get("/vehicle/{vehicle_id}/next-stops")
def get_vehicle_next_stops(vehicle_id: str):
    """
    Popup: Click a Bus -> See where it's going.
    """
    cursor = db.get_cursor()
    
    # 1. Find the trip_id for this vehicle
    trip_res = cursor.execute("SELECT trip_id FROM realtime_vehicles WHERE vehicle_id = ?", (vehicle_id,)).fetchone()
    
    if not trip_res:
        raise HTTPException(status_code=404, detail="Vehicle not found or not active")
        
    trip_id = trip_res[0]

    # 2. Get predictions for this trip
    query = """
        SELECT 
            p.stop_id,
            s.stop_name, 
            p.arrival_time,
            (epoch(p.arrival_time) - epoch(current_timestamp)) / 60 as minutes_away
        FROM realtime_predictions p
        LEFT JOIN stg_stops s ON p.stop_id = s.stop_id
        WHERE p.trip_id = ? 
          AND p.arrival_time > current_timestamp
        ORDER BY p.stop_sequence ASC
        LIMIT 5
    """
    
    rows = cursor.execute(query, (trip_id,)).fetchall()
    
    next_stops = []
    for r in rows:
        next_stops.append({
            "stop_id": r[0],
            "stop_name": r[1] or f"Stop {r[0]}", # Fallback if stops table missing
            "arrival_time": r[2],
            "minutes_away": int(r[3])
        })

    return {"vehicle_id": vehicle_id, "trip_id": trip_id, "next_stops": next_stops}