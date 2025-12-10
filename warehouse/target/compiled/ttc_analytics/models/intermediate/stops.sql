

-- Clean stops layer

SELECT  stop_id,
        stop_name,
        stop_lat,
        stop_lon
        
from "analytics"."main"."stg_stops"