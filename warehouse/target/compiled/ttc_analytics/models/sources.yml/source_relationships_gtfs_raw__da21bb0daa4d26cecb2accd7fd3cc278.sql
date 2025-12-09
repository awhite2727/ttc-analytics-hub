
    
    

with child as (
    select route_id as from_field
    from '../backend/data/gtfs_raw/static_trips.csv'
    where route_id is not null
),

parent as (
    select route_id as to_field
    from '../backend/data/gtfs_raw/static_routes.csv'
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


