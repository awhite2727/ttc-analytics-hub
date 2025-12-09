
    
    

select
    stop_id as unique_field,
    count(*) as n_records

from '../backend/data/gtfs_raw/static_stops.csv'
where stop_id is not null
group by stop_id
having count(*) > 1


