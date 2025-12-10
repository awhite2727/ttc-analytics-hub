{{ config(materialized='table') }}

-- Clean stops layer

SELECT  stop_id,
        stop_name,
        stop_lat,
        stop_lon
        
from {{ ref('stg_stops') }}
