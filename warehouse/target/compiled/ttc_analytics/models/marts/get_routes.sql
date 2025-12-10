-- Clean routes layer

SELECT  l.route_id,
        l.trip_name,
        l.direction_id,
        s.coordinates
FROM "analytics"."main"."route_shapes_lookup" l
JOIN "analytics"."main"."route_shapes" s ON l.shape_id = s.shape_id