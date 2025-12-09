
    
    

select
    route_id as unique_field,
    count(*) as n_records

from '../backend/data/gtfs_raw/static_routes.csv'
where route_id is not null
group by route_id
having count(*) > 1


