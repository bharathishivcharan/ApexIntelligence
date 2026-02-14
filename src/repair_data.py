import fastf1
import sqlite3
import os

try:
    fastf1.Cache.enable_cache('cache') 
except AttributeError:
    print("Skipping cache setup...")

def repair_database(year, circuit, driver_code):
    print(f"🚀 Fetching FULL engineering data for {driver_code}...")
    
    # Using 'Qualifying' (Q) ensures we get the most detailed sensor data
    session = fastf1.get_session(year, circuit, 'Q')
    session.load()
    
    # Get the fastest lap
    lap = session.laps.pick_driver(driver_code).pick_fastest()
    
    # This is the critical part: get_telemetry() picks up all 
    # channels (Steering, Brake, Throttle, X, Y, Z)
    telemetry = lap.get_telemetry()
    
    # Clean the column names to remove any weird formatting
    telemetry.columns = telemetry.columns.astype(str)

    # Save to SQL
    conn = sqlite3.connect('data/f1_data.db')
    table_name = f"telemetry_{driver_code}_{circuit}_{year}"
    
    # We use if_exists='replace' to wipe the old, broken table
    telemetry.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"📊 Columns now in {table_name}:")
    print(telemetry.columns.tolist())
    print(f"Successfully updated {driver_code}\n")

if __name__ == "__main__":
    # Create cache folder if it doesn't exist
    if not os.path.exists('cache'):
        os.makedirs('cache')
        
    repair_database(2025, 'Monaco', 'LEC')
    repair_database(2025, 'Monaco', 'HAM')