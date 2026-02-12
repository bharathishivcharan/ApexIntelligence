import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

def load_and_calculate(table_name):
    conn = sqlite3.connect('data/f1_data.db')
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    # Convert Speed to m/s
    df['Speed_ms'] = df['Speed'] / 3.6
    
    # Logic for Distance (X-Axis)
    df['Distance_calc'] = (df['Speed_ms'] * df['Time'].diff().fillna(0)).cumsum()

    # Longitudinal G (Braking/Accel)
    accel_long = df['Speed_ms'].diff() / df['Time'].diff().fillna(0.1)
    df['G_Long'] = accel_long / 9.81
    
    return df

def plot_pro_dashboard(table1, table2, name1, name2):
    d1 = load_and_calculate(table1)
    d2 = load_and_calculate(table2)

    # 4-pane layout
    fig, ax = plt.subplots(4, 1, figsize=(16, 20), sharex=True)
    plt.subplots_adjust(hspace=0.08)

    c1, c2 = '#FF0000', '#00A19B'

    # --- Plot 1: Speed & DRS ---
    ax[0].plot(d1['Distance_calc'], d1['Speed'], color=c1, label=name1, linewidth=2)
    ax[0].plot(d2['Distance_calc'], d2['Speed'], color=c2, label=name2, linewidth=2, linestyle='--')
    # Highlight DRS zones
    ax[0].fill_between(d1['Distance_calc'], 0, 300, where=d1['DRS']>10, color='white', alpha=0.1, label='DRS Open')
    ax[0].set_ylabel('Speed (km/h)')
    ax[0].legend(loc='upper right')

    # --- Plot 2: Throttle & Brake (The "Feet") 
    ax[1].plot(d1['Distance_calc'], d1['Throttle'], color=c1, alpha=0.8)
    ax[1].plot(d2['Distance_calc'], d2['Throttle'], color=c2, alpha=0.4, linestyle='--')
    # Shading the brake area
    ax[1].fill_between(d1['Distance_calc'], d1['Brake'], color='white', alpha=0.3, label='Brake')
    ax[1].set_ylabel('Pedal %')

    # --- Plot 3: G-Force Longitudinal (The "Bite") ---
    ax[2].plot(d1['Distance_calc'], d1['G_Long'], color=c1)
    ax[2].plot(d2['Distance_calc'], d2['G_Long'], color=c2, alpha=0.5)
    ax[2].axhline(0, color='white', linewidth=0.5)
    ax[2].set_ylabel('G-Long (Braking)')

    # --- Plot 4: GPS Track Layout (The "Location") ---
    ax[3].scatter(d1['Distance_calc'], d1['Y'], c=d1['Speed'], cmap='magma', s=2)
    ax[3].set_ylabel('Track Curvature')
    ax[3].set_xlabel('Distance (meters)')

    plt.suptitle(f'Apex Intelligence: {name1} vs {name2} Engineering Analysis', fontsize=18)
    plt.show()

if __name__ == "__main__":
    plot_pro_dashboard('telemetry_LEC_Monaco_2025', 'telemetry_HAM_Monaco_2025', "Leclerc", "Hamilton")