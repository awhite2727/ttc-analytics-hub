
  
    
    

    create  table
      "analytics"."main"."dim_route_shapes__dbt_tmp"
  
    as (
      

-- Creates {lon:lat} coordinates for every route point 

SELECT  shape_id,
        ARRAY_AGG(list_value(shape_pt_lon, shape_pt_lat) ORDER BY  shape_pt_sequence ASC ) AS coordinates
FROM "analytics"."main"."stg_shapes"
GROUP BY  shape_id
    );
  
  