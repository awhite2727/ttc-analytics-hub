
  
    
    

    create  table
      "analytics"."main"."stops__dbt_tmp"
  
    as (
      

-- Clean stops layer

SELECT  stop_id,
        stop_name,
        stop_lat,
        stop_lon
        
from "analytics"."main"."stg_stops"
    );
  
  