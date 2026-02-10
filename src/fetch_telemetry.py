import fastf1 
import sqlite3 
import pandas as pd 
import os

print("1. Script started...")
def fetch_driver_telemetry(year, gp, driver_code): 
    if not os.path.exists('cache'): 
        os.makedirs('cache') 
    fastf1.Cache.enable_cache('cache') 
    print(f"Loading {year} {gp} for {driver_code}...") 
    session = fastf1.get_session(year, gp, 'R') 
    session.load() 
    fastest_lap = session.laps.pick_driver(driver_code).pick_fastest() 
    telemetry = fastest_lap.get_telemetry() 
    telemetry['Time'] = telemetry['Time'].dt.total_seconds() 
    telemetry = telemetry[['Time', 'Speed', 'RPM', 'Throttle', 'Brake', 'nGear']] 
    conn = sqlite3.connect('data/f1_data.db') 
    table_name = f"telemetry_{driver_code}{gp}{year}".replace(" ", "_") 
    telemetry.to_sql(table_name, conn, if_exists='replace', index=False) 
    conn.close() 
    print(f"✅ Success! Table created: {table_name}")

if __name__ == "__main__": 
    fetch_driver_telemetry(2025, 'Monaco', 'LEC')