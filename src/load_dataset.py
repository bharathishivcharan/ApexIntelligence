import fastf1
import sqlite3
import pandas as pd

fastf1.Cache.enable_cache('cache') 
session = fastf1.get_session(2025, 'Spain', 'Q')
session.load()

conn = sqlite3.connect('data/f1_data.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"DROP TABLE {table[0]}")
    print(f"Deleted: {table[0]}")

drivers = session.results['Abbreviation'].head(10).tolist()

for drv in drivers:
    try:
        print(f"Downloading {drv}...")
        lap = session.laps.pick_driver(drv).pick_fastest()
        tel = lap.get_telemetry().add_distance()
        
        tel_df = pd.DataFrame(tel)
        tel_df.to_sql(f'telemetry_{drv.lower()}_spain', conn, index=False)
    except:
        print(f"Skipping {drv} - No data.")

conn.close()
print("Spanish GP Grid Loaded!")