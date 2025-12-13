from fastapi import APIRouter, Query
from api.db import db

router = APIRouter()

@router.get("/vehicles")
def get_vehicles(route_id: str = Query(None), direction_id: int = Query(None)):
    cursor = db.get_cursor()
    
    query = """
        SELECT vehicle_id, latitude, longitude, bearing, vehicle_label 
        FROM realtime_vehicles
        WHERE route_id = ?
    """
    params = [route_id]
        
    df = cursor.execute(query, params).df()
    
    features = []
    for _, row in df.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']]
            },
            "properties": {
                "vehicle_id": row['vehicle_id'],
                "label": row['vehicle_label'],
                "bearing": row['bearing'],
                "arrow_bearing": (row['bearing']+90) % 360
            }
        })

    return {"type": "FeatureCollection", "features": features}