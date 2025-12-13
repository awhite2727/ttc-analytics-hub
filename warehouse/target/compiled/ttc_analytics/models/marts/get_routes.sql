-- Clean routes layer

with route_colour as (
    select route_id, route_color,
    from "analytics"."main"."stg_routes"
)

SELECT  r.route_id,
        l.trip_name,
        s.coordinates,
        r.route_color
FROM route_colour r
JOIN "analytics"."main"."route_shapes_lookup" l ON r.route_id = l.route_id
JOIN "analytics"."main"."route_shapes" s ON l.shape_id = s.shape_id