import duckdb
import pandas as pd
import json
from pathlib import Path
from backend.api.services.polling import update_vehicle_positions_json

con = duckdb.connect("warehouse/analytics.duckdb")

OUT = Path("frontend/data/")
(OUT / "directions").mkdir(parents=True, exist_ok=True)
(OUT / "map").mkdir(parents=True, exist_ok=True)
(OUT / "vehicles").mkdir(parents=True, exist_ok=True)

# --------------------------
# STAGING TABLES
# --------------------------
df_stg_routes = con.execute("SELECT * FROM stg_routes").fetchdf()
df_stg_shapes = con.execute("SELECT * FROM stg_shapes").fetchdf()
df_stg_stop_times = con.execute("SELECT * FROM stg_stop_times").fetchdf()
df_stg_stops = con.execute("SELECT * FROM stg_stops").fetchdf()
df_stg_trips = con.execute("SELECT * FROM stg_trips").fetchdf()

# --------------------------
# ROUTE LIST
# --------------------------
df_route_list = con.execute("""
    SELECT DISTINCT CAST(route_id AS INTEGER) AS route_id, route_long_name
    FROM stg_routes
    ORDER BY route_id
""").fetchdf()

df_route_list.to_json(OUT / "route_list.json", orient="records")

# --------------------------
# DIRECTIONS per route_id
# --------------------------
df_all_directions = con.execute("""
    SELECT route_id, direction_id, trip_name
    FROM route_shapes_lookup
    ORDER BY route_id, direction_id
""").fetchdf()

for route_id, group in df_all_directions.groupby("route_id"):
    group[["direction_id", "trip_name"]].to_json(
        OUT / "directions" / f"{route_id}.json",
        orient="records"
    )

# --------------------------
# MAP DATA (routes + stops)
# --------------------------
routes = con.execute("""
    SELECT route_id, direction_id, trip_name, coordinates, route_color
    FROM get_routes
""").fetchdf()

stops = con.execute("""
    SELECT route_id, direction_id, stop_id, stop_name, stop_lat, stop_lon
    FROM get_route_stops
""").fetchdf()

def feature_collection(features):
    return {
        "type": "FeatureCollection",
        "features": features
    }

for (route_id, direction_id), group in routes.groupby(["route_id", "direction_id"]):
    route_features = []
    for _, row in group.iterrows():
        # Convert ndarray → list of lists with native Python floats
        coords = [[float(lon), float(lat)] for lon, lat in row.coordinates]
        color = f"#{row.route_color}" if row.route_color else "#d63031"
        route_features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "route_id": route_id,
                "trip_name": row.trip_name,
                "route_color": color
            }
        })

    with open(OUT / "map" / f"{route_id}-{direction_id}-routes.json", "w") as f:
        json.dump(feature_collection(route_features), f)

    stop_group = stops[(stops.route_id == route_id) & (stops.direction_id == direction_id)]
    stop_features = []
    for _, row in stop_group.iterrows():
        stop_features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [row.stop_lon, row.stop_lat]},
            "properties": {"stop_id": row.stop_id, "stop_name": row.stop_name}
        })

    with open(OUT / "map" / f"{route_id}-{direction_id}-stops.json", "w") as f:
        json.dump(feature_collection(stop_features), f)

# --------------------------
# VEHICLES
# --------------------------
vehicles = update_vehicle_positions_json() 

