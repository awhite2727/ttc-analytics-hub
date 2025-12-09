
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select route_id
from '../backend/data/gtfs_raw/static_routes.csv'
where route_id is null



  
  
      
    ) dbt_internal_test