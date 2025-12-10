
  
    
    

    create  table
      "analytics"."main"."stg_routes__dbt_tmp"
  
    as (
      -- stg_routes.sql

SELECT  cast(route_id AS varchar)           AS route_id,
        cast(route_long_name AS varchar)    AS route_long_name,
        cast(route_type AS integer)         AS route_type,
        cast(LOWER(route_color) AS varchar) AS route_color


FROM '../backend/data/gtfs_raw/static_routes.csv'
    );
  
  