-- stg_routes.sql

SELECT  cast(route_id AS integer)         AS route_id,
        cast(route_long_name AS varchar)  AS route_long_name,
        cast(route_type AS integer)       AS route_type,
        cast(route_color AS varchar)      AS route_color

FROM {{source('gtfs_raw', 'routes')}}
