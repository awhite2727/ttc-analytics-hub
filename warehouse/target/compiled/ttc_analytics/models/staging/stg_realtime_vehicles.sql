CREATE TABLE IF NOT EXISTS realtime_vehicles (
    vehicle_id VARCHAR,
    trip_id VARCHAR,
    route_id VARCHAR,
    direction_id INTEGER,
    latitude DOUBLE,
    longitude DOUBLE,
    bearing DOUBLE,
    speed DOUBLE,
    timestamp TIMESTAMP,
    vehicle_label VARCHAR, -- The bus number painted on the side
    PRIMARY KEY (vehicle_id)
)