
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select shape_id
from '../backend/data/gtfs_raw/static_shapes.csv'
where shape_id is null



  
  
      
    ) dbt_internal_test