

-- Map stop coordinates to routes

WITH select_route AS (
	SELECT  route_id,
	        shape_id
    FROM "analytics"."main"."route_shapes_lookup"
),

select_trip AS (
    SELECT  r.route_id,
            r.shape_id,
            t.trip_id,
    FROM select_route r
    JOIN "analytics"."main"."stg_trips" t ON r.shape_id = t.shape_id
    WHERE t.trip_id IS NOT NULL
),

select_stops AS (
    SELECT  DISTINCT t.trip_id,
            st.stop_id
    FROM select_trip t
    JOIN "analytics"."main"."stg_stop_times" st ON t.trip_id = st.trip_id
)

SELECT  DISTINCT t.route_id,
        s2.stop_id,
        s2.stop_name,
        s2.stop_lat,
        s2.stop_lon

FROM select_trip t
JOIN select_stops s ON t.trip_id = s.trip_id
JOIN "analytics"."main"."stops" s2 ON s.stop_id = s2.stop_id