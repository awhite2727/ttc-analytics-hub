
  
    
    

    create  table
      "analytics"."main"."dim_stops__dbt_tmp"
  
    as (
      

-- Clean, ready-to-query stops layer

SELECT  stop_id,
        stop_name,
        stop_lat,
        stop_lon
        
from "analytics"."main"."stg_stops"
    );
  
  