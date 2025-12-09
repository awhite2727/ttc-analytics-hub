-- stg_stops.sql

SELECT  cast(stop_id AS varchar)             AS stop_id,
        cast(stop_name AS varchar)           AS stop_name,
        cast(stop_lat AS float)              AS stop_lat,
        cast(stop_lon AS float)              AS stop_lon,
        cast(wheelchair_boarding AS integer) AS wheelchair_boarding,

        CASE WHEN wheelchair_boarding = 1 THEN true else false end AS has_wheelchair_boarding


FROM {{source('gtfs_raw', 'stops')}}
