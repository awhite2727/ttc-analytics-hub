
    
    

select
    trip_id as unique_field,
    count(*) as n_records

from '../backend/data/gtfs_raw/static_trips.csv'
where trip_id is not null
group by trip_id
having count(*) > 1


