import json
import requests
import zipfile
import pandas as pd
import io
from datetime import date
from urllib import parse

GTFS_STATIC_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/7795b45e-e65a-4465-81fc-c36b9dfff169/resource/cfb6b2b8-6191-41e3-bda1-b175c51148cb/download/TTC Routes and Schedules Data.zip"

FILES_TO_LOAD = {
    "routes.txt": "static_routes",
    "shapes.txt": "static_shapes",
    "stops.txt": "static_stops",
    "stop_times.txt": "static_stop_times",
    "trips.txt": "static_trips"
}

def load_static():
    try:
        r = requests.get(GTFS_STATIC_URL)
        
        z = zipfile.ZipFile(io.BytesIO(r.content))
        print(z.namelist)

        for filename, table_name in FILES_TO_LOAD.items():
            if filename in z.namelist():
                print(f"Processing {filename} -> {table_name}...")

                with z.open(filename) as f:
                    dest_path = ".\data\gtfs_raw"
                    output_file = f"{dest_path}/{table_name}.csv"
                    try:
                        df = pd.read_csv(f)
                        df.to_csv(output_file, index=False)
                        print(f"   ✅ Successfully loaded {table_name}")
                    except Exception as e:
                        print(f"   ❌ Error loading {table_name}: {e}")
            
            else:
                print(f"   ⚠️ File {filename} not found in Zip.")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the download: {e}")

if __name__ == "__main__":
    load_static()