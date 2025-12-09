{{ config(materialized='table') }}

-- Map stop coordinates to routes

SELECT  DISTINCT t.route_id,
        t.direction_id,
        s.stop_id,
        s.stop_name,
        s.stop_lat,
        s.stop_lon

FROM {{ ref('dim_stops') }} s
JOIN {{ ref('stg_stop_times') }} st ON s.stop_id = st.stop_id
JOIN {{ ref('stg_trips') }} t ON st.trip_id = t.trip_id