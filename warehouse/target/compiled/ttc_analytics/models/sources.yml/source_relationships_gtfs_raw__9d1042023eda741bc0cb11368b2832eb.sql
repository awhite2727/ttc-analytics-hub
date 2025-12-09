
    
    

with child as (
    select shape_id as from_field
    from '../backend/data/gtfs_raw/static_shapes.csv'
    where shape_id is not null
),

parent as (
    select shape_id as to_field
    from '../backend/data/gtfs_raw/static_trips.csv'
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


