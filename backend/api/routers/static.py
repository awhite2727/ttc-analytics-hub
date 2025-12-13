from fastapi import APIRouter, Query
from api.db import db

router = APIRouter()
"""
@router.get("/directions")
def get_directions(route_id: str):
    cursor = db.get_cursor()
    query = 
        SELECT direction_id, trip_name 
        FROM route_shapes_lookup 
        WHERE route_id = ?
        ORDER BY direction_id
    
    df = cursor.execute(query, [route_id]).df()
    return df.to_dict(orient="records")
"""

@router.get("/route_list")
def get_route_list():
    cursor = db.get_cursor()
    query = """
        SELECT DISTINCT cast(route_id AS integer) AS route_id, route_long_name 
        FROM stg_routes 
        ORDER BY route_id ASC
    """
    df = cursor.execute(query).df()
    return df.to_dict(orient="records")

@router.get("/routes")
def get_routes(route_id: str = Query(None), direction_id: int = Query(None)):
    cursor = db.get_cursor()
    
    query = """
        SELECT route_id, trip_name, coordinates, route_color
        FROM get_routes
        WHERE route_id = ?
    """
    params = [route_id]

    if direction_id is not None:
        query += " AND direction_id = ?"
        params.append(direction_id)

    results = cursor.execute(query, params).fetchall()
    
    features = []
    for row in results:
        raw_color = row[3]
        final_color = f"#{raw_color}" if raw_color else "#d63031"
        
        features.append({
            "type": "Feature",
            "geometry": { "type": "LineString", "coordinates": row[2] },
            "properties": { 
                "route_id": row[0], 
                "trip_name": row[1], 
                "route_color": final_color 
            }
        })

    return {"type": "FeatureCollection", "features": features}

@router.get("/stops")
def get_stops(route_id: str = Query(None), direction_id: int = Query(None)):
    cursor = db.get_cursor()
    
    query = """
        SELECT stop_id, stop_name, stop_lat, stop_lon 
        FROM get_route_stops 
        WHERE route_id = ?
    """
    params = [route_id]

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