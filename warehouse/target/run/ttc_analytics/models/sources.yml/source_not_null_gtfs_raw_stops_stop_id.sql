
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select stop_id
from '../backend/data/gtfs_raw/static_stops.csv'
where stop_id is null



  
  
      
    ) dbt_internal_test