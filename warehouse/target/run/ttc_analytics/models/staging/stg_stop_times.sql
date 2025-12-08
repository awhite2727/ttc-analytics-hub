
  
    
    

    create  table
      "analytics"."main"."stg_stop_times__dbt_tmp"
  
    as (
      -- stg_stop_times.sql

SELECT  cast(trip_id AS integer)       AS trip_id,
        cast(stop_id AS integer)       AS stop_id,
        cast(stop_sequence AS integer) AS stop_sequence,
        cast(shape_dist_traveled as float) as shape_dist_traveled

FROM '../backend/data/gtfs_raw/static_stop_times.csv'
    );
  
  