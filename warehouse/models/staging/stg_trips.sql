-- stg_trips.sql

SELECT  cast(trip_id AS integer)               AS trip_id,
        cast(route_id AS integer)              AS route_id,
        cast(trip_headsign AS varchar)         AS trip_headsign,
        cast(trip_short_name AS varchar)       AS trip_short_name,
        cast(direction_id AS integer)          AS direction_id,
        cast(block_id AS integer)              AS block_id,
        cast(shape_id AS integer)              AS shape_id,
        cast(wheelchair_accessible AS integer) AS wheelchair_accessible,
        cast(bikes_allowed AS integer)         AS bikes_allowed,
         
        --Create clean booleans (original fields are tristate)
        CASE WHEN wheelchair_accessible = 1 THEN true else false end AS is_accessible, 
        CASE WHEN bikes_allowed = 1 THEN true else false end AS is_bike_allowed

FROM {{source('gtfs_raw', 'trips')}}

