
  
    
    

    create  table
      "analytics"."main"."stg_shapes__dbt_tmp"
  
    as (
      -- stg_shapes.sql

SELECT  cast(shape_id AS varchar)          AS shape_id,
        cast(shape_pt_lat AS float)        AS shape_pt_lat,
        cast(shape_pt_lon AS float)        AS shape_pt_lon,
        cast(shape_pt_sequence AS integer) AS shape_pt_sequence,
        cast(shape_dist_traveled AS float) AS shape_dist_traveled

FROM '../backend/data/gtfs_raw/static_shapes.csv'
    );
  
  