{{ config(materialized='table') }}

WITH shape_stats AS (
    -- Calculate the maximum distance (length) for every shape
    SELECT  shape_id,
            MAX(shape_dist_traveled) AS total_length_meters
    FROM {{ ref('stg_shapes') }}
    GROUP BY shape_id
),

joined_trips AS (
    SELECT  t.route_id,
            t.direction_id,
            t.trip_headsign,
            t.shape_id,
            s.total_length_meters
    FROM {{ ref('stg_trips') }} t
    JOIN shape_stats s ON t.shape_id = s.shape_id
    WHERE t.shape_id IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY t.route_id, t.direction_id
        ORDER BY s.total_length_meters DESC
    ) = 1
)

SELECT  route_id,
        trip_headsign AS trip_name,
        jt.shape_id,
        ARRAY_AGG(rs.coordinates) AS multilinestring,
FROM joined_trips jt
JOIN {{ ref('route_shapes') }} rs ON jt.shape_id = rs.shape_id
-- Group by to deduplicate trips that share the exact same shape
GROUP BY  route_id,
          trip_headsign,
          jt.shape_id