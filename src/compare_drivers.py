import sqlite3 
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import os

def load_and_process(table_name): 
    conn = sqlite3.connect('data/f1_data.db') 
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn) 
    conn.close() 
    df['Speed_ms'] = df['Speed'] / 3.6 
    df['Distance'] = (df['Speed_ms'] * df['Time'].diff().fillna(0)).cumsum() 
    return df

def calculate_delta(driver1, driver2): 
    # 1. Create a "Standard Track" from 0m to the end of the lap, every 1 meter 
    ref_distance = np.linspace(0, driver1['Distance'].iloc[-1], num=2000) 
    # 2. Interpolate Time for both drivers onto this 1-meter map 
    time1_interp = np.interp(ref_distance, driver1['Distance'], driver1['Time']) 
    time2_interp = np.interp(ref_distance, driver2['Distance'], driver2['Time']) 
    # 3. Subtract one from the other to get the Delta (the gap) 
    delta = time1_interp - time2_interp 
    return ref_distance, delta

def plot_battle(table1, table2, name1, name2):
    d1 = load_and_process(table1)
    d2 = load_and_process(table2)

    # 1. Calculate the Gap (The "Tug of War" line)
    ref_dist, delta = calculate_delta(d1, d2)

    # 2. CREATE THE FIGURES
    fig, ax = plt.subplots(2, 1, figsize=(15, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    # 3. Plot the Speed (Top Plot)
    ax[0].plot(d1['Distance'], d1['Speed'], label=name1, color='red')
    ax[0].plot(d2['Distance'], d2['Speed'], label=name2, color='cyan', linestyle='--')
    ax[0].set_ylabel('Speed (km/h)')
    ax[0].legend()
    ax[0].grid(True, alpha=0.3)
    ax[0].set_title(f'F1 Telemetry Battle: {name1} vs {name2}')

    # 4. Plot the Gap (Bottom Plot)
    ax[1].plot(ref_dist, delta, color='yellow', linewidth=2)
    ax[1].axhline(0, color='white', linestyle='-')
    ax[1].set_ylabel('Gap (seconds)')
    ax[1].set_xlabel('Distance (meters)')
    ax[1].grid(True, alpha=0.3)

    # 5. NOW ADD THE SECTOR LINES 
    sectors = [1100, 2300]
    for s in sectors:
        ax[0].axvline(s, color='purple', linestyle='--', alpha=0.5)
        ax[1].axvline(s, color='purple', linestyle='--', alpha=0.5)

    # Add text labels
    ax[0].text(500, 310, 'Sector 1', color='purple', alpha=0.7)
    ax[0].text(1600, 310, 'Sector 2', color='purple', alpha=0.7)
    ax[0].text(2800, 310, 'Sector 3', color='purple', alpha=0.7)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__": 
    TABLE_1 = 'telemetry_LEC_Monaco_2025' 
    TABLE_2 = 'telemetry_HAM_Monaco_2025' 
    plot_battle(TABLE_1, TABLE_2, "Leclerc", "Hamilton")