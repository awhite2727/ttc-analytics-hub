import asyncio
from api.db import db
import time

async def run_analytics_engine():
    """
    Runs periodically to:
    1. Aggregate raw logs into hourly stats.
    2. Prune raw logs older than 24 hours to save space.
    """
    while True:
        # Run this every 60 minutes
        await asyncio.sleep(3600) 
        
        print("Running Analytics Aggregation...")
        try:
            if db.con:
                cursor = db.con.cursor()
                
                # --- STEP 1: Aggregation ---
                # Speed conversion: m/s * 3.6 = km/h
                
                # INSERT OR REPLACE to handle re-runs safely
                cursor.execute("""
                    INSERT OR REPLACE INTO analytics_route_stats_hourly
                    SELECT 
                        CAST(timestamp AS DATE) as log_date,
                        EXTRACT(HOUR FROM timestamp) as hour_of_day,
                        route_id,
                        AVG(speed) * 3.6 as avg_speed_kph,
                        MAX(speed) * 3.6 as max_speed_kph,
                        COUNT(DISTINCT vehicle_id) as active_vehicle_count,
                        COUNT(*) as total_samples,
                        CURRENT_TIMESTAMP as updated_at
                    FROM raw_vehicle_position_log
                    WHERE timestamp < date_trunc('hour', current_timestamp) -- Only process fully completed hours
                    GROUP BY 1, 2, 3
                """)
                
                inserted_count = cursor.rowcount
                print(f"Analytics: Updated stats for {inserted_count} route-hours.")

                # --- STEP 2: Pruning ---
                # Keep raw data only for the last 24 hours
                cursor.execute("""
                    DELETE FROM raw_vehicle_position_log 
                    WHERE timestamp < current_timestamp - INTERVAL 24 HOUR
                """)
                
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    print(f"Analytics: Pruned {deleted_count} old raw rows.")

                cursor.close()

        except Exception as e:
            print(f"Analytics Error: {e}")