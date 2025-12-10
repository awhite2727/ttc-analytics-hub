-- Clean routes layer

SELECT  l.route_id,
        l.trip_name,
        l.direction_id,
        s.coordinates
FROM {{ref('route_shapes_lookup')}} l
JOIN {{ref('route_shapes')}} s ON l.shape_id = s.shape_id
