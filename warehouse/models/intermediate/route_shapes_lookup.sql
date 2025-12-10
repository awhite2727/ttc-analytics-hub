{{ config(materialized='table') }}

WITH shape_stats AS (
    -- Calculate the maximum distance (length) for every shape
    -- This assumes shape_dist_traveled is populated in stg_shapes
    SELECT  shape_id,
            MAX(shape_dist_traveled) AS total_length_meters
    FROM {{ ref('stg_shapes') }}
    GROUP BY shape_id
),

joined_trips AS (
    SELECT  t.route_id,
            t.trip_headsign,
            t.direction_id,
            t.shape_id,
            s.total_length_meters
    FROM {{ ref('stg_trips') }} t
    JOIN shape_stats s ON t.shape_id = s.shape_id
    WHERE t.shape_id IS NOT NULL
)

SELECT  route_id,
        trip_headsign AS trip_name,
        direction_id,
        shape_id
FROM joined_trips
-- Group by to deduplicate trips that share the exact same shape
GROUP BY  route_id,
          trip_headsign,
          direction_id,
          shape_id,
          total_length_meters

-- Select the route_id with the greatest length
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY route_id, direction_id 
    ORDER BY total_length_meters DESC
) = 1