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
    cursor = db.get_cursor()
    # FIX: JOIN trips table for route_id fallback
    # FIX: Use date_diff for accurate minutes calculation
    query = """
        SELECT 
            p.trip_id,
            COALESCE(v.route_id, t.route_id, 'Unknown') as route_id,
            COALESCE(v.vehicle_label, v.vehicle_id, 'Scheduled') as vehicle_label,
            p.arrival_time,
            CAST(date_diff('second', current_timestamp, p.arrival_time) / 60 AS INTEGER) as minutes_away,
            p.delay
        FROM realtime_predictions p
        LEFT JOIN realtime_vehicles v ON p.trip_id = v.trip_id
        LEFT JOIN stg_trips t ON p.trip_id = t.trip_id
        WHERE p.stop_id = ? 
          AND p.arrival_time > current_timestamp
        ORDER BY p.arrival_time ASC
        LIMIT 5
    """
    rows = cursor.execute(query, (stop_id,)).fetchall()
    return {"stop_id": stop_id, "predictions": [
        {"trip_id": r[0], "route_id": r[1], "vehicle_label": r[2], "minutes_away": r[4] if r[4]>=0 else 0, "delay_seconds": r[5]}
        for r in rows
    ]}

@router.get("/vehicle/{vehicle_id}/next-stops")
def get_vehicle_next_stops(vehicle_id: str):
    cursor = db.get_cursor()
    trip_res = cursor.execute("SELECT trip_id FROM realtime_vehicles WHERE vehicle_id = ?", (vehicle_id,)).fetchone()
    if not trip_res: raise HTTPException(status_code=404, detail="Vehicle inactive")
    
    query = """
        SELECT 
            p.stop_id, 
            s.stop_name, 
            CAST(date_diff('second', current_timestamp, p.arrival_time) / 60 AS INTEGER)
        FROM realtime_predictions p
        LEFT JOIN stops s ON p.stop_id = s.stop_id
        WHERE p.trip_id = ? AND p.arrival_time > current_timestamp
        ORDER BY p.stop_sequence ASC LIMIT 5
    """
    rows = cursor.execute(query, (trip_res[0],)).fetchall()
    return {"vehicle_id": vehicle_id, "next_stops": [
        {"stop_id": r[0], "stop_name": r[1] or r[0], "minutes_away": r[2] if r[2]>=0 else 0} for r in rows
    ]}