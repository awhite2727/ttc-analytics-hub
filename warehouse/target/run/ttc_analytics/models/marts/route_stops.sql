
  
    
    

    create  table
      "analytics"."main"."route_stops__dbt_tmp"
  
    as (
      

-- Map stop coordinates to routes

SELECT  DISTINCT t.route_id,
        t.direction_id,
        s.stop_id,
        s.stop_name,
        s.stop_lat,
        s.stop_lon

FROM "analytics"."main"."stops" s
JOIN "analytics"."main"."stg_stop_times" st ON s.stop_id = st.stop_id
JOIN "analytics"."main"."stg_trips" t ON st.trip_id = t.trip_id
ORDER BY t.route_id, t.direction_id, s.stop_id ASC
    );
  
  