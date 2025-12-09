{{ config(materialized='table') }}

-- Clean, ready-to-query stops layer

SELECT  stop_id,
        stop_name,
        stop_lat,
        stop_lon
        
from {{ ref('stg_stops') }}
