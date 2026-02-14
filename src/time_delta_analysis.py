import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

def get_processed_telemetry(table_name):
    conn = sqlite3.connect('data/f1_data.db')
    df = pd.read_sql(f"SELECT Time, Speed FROM {table_name}", conn)
    conn.close()

    # Convert Time to total seconds (float)
    df['Time_sec'] = pd.to_timedelta(df['Time']).dt.total_seconds()
    
    # Calculate Cumulative Distance
    df['Speed_ms'] = df['Speed'] / 3.6
    # Distance = Speed * Time_Delta
    df['Distance'] = (df['Speed_ms'] * df['Time_sec'].diff().fillna(0)).cumsum()
    
    return df

def run_delta_analysis(tab1, tab2, name1, name2):
    d1 = get_processed_telemetry(tab1)
    d2 = get_processed_telemetry(tab2)

    # 1. Create the Common Ruler (0 to Track Length)
    track_length = max(d1['Distance'].max(), d2['Distance'].max())
    common_dist = np.linspace(0, track_length, 2000)

    # 2. Interpolate: Find where each driver was at every millimeter of the ruler
    time1_interp = np.interp(common_dist, d1['Distance'], d1['Time_sec'])
    time2_interp = np.interp(common_dist, d2['Distance'], d2['Time_sec'])

    # 3. Calculate Delta (Positive = name2 is faster, Negative = name1 is faster)
    delta = time1_interp - time2_interp

    # --- Visualization ---
    fig, ax = plt.subplots(figsize=(15, 7))
    
    # The Delta Line
    ax.plot(common_dist, delta, color='white', linewidth=2, label=f'Delta Trace')
    
    # Fill the 'Who is ahead' zones
    ax.fill_between(common_dist, delta, 0, where=(delta > 0), color='#FF0000', alpha=0.4, label=f'{name2} Gaining')
    ax.fill_between(common_dist, delta, 0, where=(delta < 0), color='#00A19B', alpha=0.4, label=f'{name1} Gaining')

    ax.set_title(f'Time Delta Analysis: {name1} vs {name2}', fontsize=16)
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('<-- {name1} Ahead | {name2} Ahead --> (Seconds)')
    ax.grid(alpha=0.1)
    ax.legend()
    
    plt.savefig('visuals/time_delta.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    run_delta_analysis('telemetry_LEC_Monaco_2025', 'telemetry_HAM_Monaco_2025', "Leclerc", "Hamilton")