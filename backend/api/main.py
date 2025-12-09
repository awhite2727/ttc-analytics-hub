import duckdb
from fastapi import FastAPI, Query
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

# Allow the frontend to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development only
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to warehouse
CURRENT_DIR = Path(__file__).resolve().parent
DB_PATH = CURRENT_DIR.parent.parent / "warehouse" / "analytics.duckdb"
con = duckdb.connect(str(DB_PATH), read_only=True) 

@app.get("/")
def read_root():
    return {"status": "ok", "service": "TTC GTFS API"}

# 1. NEW ENDPOINT: Get available directions for a route
@app.get("/api/directions")
def get_directions(route_id: str):
    """
    Returns the available directions (0/1) and their headsigns 
    (e.g., 'East - To Kennedy Stn') for a specific route.
    """
    query = """
        SELECT direction_id, trip_name 
        FROM int_route_shapes_lookup 
        WHERE route_id = ?
        ORDER BY direction_id
    """
    cursor = con.cursor()
    df = cursor.execute(query, [route_id]).df()
    return df.to_dict(orient="records")

@app.get("/api/route_list")
def get_route_list():
    """Returns a simple list of Route IDs and Names"""
    query = """
        SELECT DISTINCT route_id, route_long_name 
        FROM stg_routes 
        ORDER BY route_id
    """
    df = con.execute(query).df()
    return df.to_dict(orient="records")

@app.get("/api/routes")
def get_routes(route_id: str = Query(None), direction_id: int = Query(None)):
    cursor = con.cursor()
    
    # Base query
    query = """
        SELECT lookup.route_id, lookup.trip_name, shapes.coordinates
        FROM int_route_shapes_lookup AS lookup
        JOIN dim_route_shapes AS shapes ON lookup.shape_id = shapes.shape_id
        WHERE lookup.route_id = ?
    """
    params = [route_id]

    # Add optional direction filter
    if direction_id is not None:
        query += " AND lookup.direction_id = ?"
        params.append(direction_id)

    results = cursor.execute(query, params).fetchall()
    
    features = []
    for row in results:
        features.append({
            "type": "Feature",
            "geometry": { "type": "LineString", "coordinates": row[2] },
            "properties": { "route_id": row[0], "trip_name": row[1] }
        })

    return {"type": "FeatureCollection", "features": features}

@app.get("/api/stops")
def get_stops(route_id: str = Query(None), direction_id: int = Query(None)):
    cursor = con.cursor()
    
    query = "SELECT stop_id, stop_name, stop_lat, stop_lon FROM dim_route_stops WHERE route_id = ?"
    params = [route_id]

    # Add optional direction filter
    if direction_id is not None:
        query += " AND direction_id = ?"
        params.append(direction_id)

    df = cursor.execute(query, params).df()
    
    features = []
    for _, row in df.iterrows():
        features.append({
            "type": "Feature",
            "geometry": { "type": "Point", "coordinates": [row['stop_lon'], row['stop_lat']] },
            "properties": { "stop_id": row['stop_id'], "stop_name": row['stop_name'] }
        })

    return {"type": "FeatureCollection", "features": features}