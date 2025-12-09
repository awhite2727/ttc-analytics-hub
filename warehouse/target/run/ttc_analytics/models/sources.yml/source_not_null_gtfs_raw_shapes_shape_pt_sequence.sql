
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select shape_pt_sequence
from '../backend/data/gtfs_raw/static_shapes.csv'
where shape_pt_sequence is null



  
  
      
    ) dbt_internal_test