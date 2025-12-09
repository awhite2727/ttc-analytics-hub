
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select stop_sequence
from '../backend/data/gtfs_raw/static_stop_times.csv'
where stop_sequence is null



  
  
      
    ) dbt_internal_test