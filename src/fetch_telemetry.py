import fastf1 
import sqlite3 
import pandas as pd 
import os

def fetch_driver_telemetry(year, gp, driver_code): 
    if not os.path.exists('cache'): 
        os.makedirs('cache') 
    fastf1.Cache.enable_cache('cache') 
    print(f"Loading {year} {gp} for {driver_code}...") 
    session = fastf1.get_session(year, gp, 'R') 
    session.load() 
    fastest_lap = session.laps.pick_drivers(driver_code).pick_fastest() 
    telemetry = fastest_lap.get_telemetry() 
    telemetry['Time'] = telemetry['Time'].dt.total_seconds() 
    telemetry = telemetry[['Time', 'Speed', 'RPM', 'Throttle', 'Brake', 'nGear']] 
    conn = sqlite3.connect('data/f1_data.db') 
    Apex_table = f"telemetry_{driver_code}_{gp}_{year}"
    telemetry.to_sql(Apex_table, conn, if_exists='replace', index=False) 
    conn.close() 
    print(f" Success! Table created: {Apex_table}")

if __name__ == "__main__": 
    fetch_driver_telemetry(2025, 'Monaco', 'HAM')