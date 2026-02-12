import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set the dark style globally
plt.style.use('dark_background')

def load_and_calculate(table_name):
    conn = sqlite3.connect('data/f1_data.db')
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    # Math: Convert Speed to m/s for physics calculations
    df['Speed_ms'] = df['Speed'] / 3.6
    
    # Math: Distance (Cumulative sum of Speed * Time Delta)
    df['Distance'] = (df['Speed_ms'] * df['Time'].diff().fillna(0)).cumsum()

    # Metric 1: Longitudinal G-Force (Acceleration/Braking)
    acceleration = df['Speed_ms'].diff() / df['Time'].diff().fillna(0.1)
    df['G_Long'] = acceleration / 9.81
    
    # Metric 2: Brake Aggressiveness (Rate of change of Brake pedal)
    # This shows how "violent" the driver is with the initial brake hit
    df['Brake_Rate'] = df['Brake'].diff() / df['Time'].diff().fillna(0.1)
    
    return df

def plot_pro_dashboard(table1, table2, name1, name2):
    d1 = load_and_calculate(table1)
    d2 = load_and_calculate(table2)

    # Creating the 4-apartment building (ax[0] to ax[3])
    fig, ax = plt.subplots(4, 1, figsize=(16, 22), sharex=True)
    plt.subplots_adjust(hspace=0.1)

    # Pro Colors: Deep Red for Ferrari, Dark Teal/Emerald for Mercedes
    c1, c2 = '#FF0000', '#00A19B'

    # --- Plot 1: Speed (The Result) ---
    ax[0].plot(d1['Distance'], d1['Speed'], color=c1, label=name1, linewidth=2)
    ax[0].plot(d2['Distance'], d2['Speed'], color=c2, label=name2, linewidth=2, linestyle='--')
    ax[0].set_ylabel('Speed (km/h)', fontsize=12, fontweight='bold')
    ax[0].legend(loc='upper right')
    ax[0].grid(visible=True, alpha=0.1)

    # --- Plot 2: Throttle & Brake Overlap (Driving Style) ---
    # Shading the area shows 'presence' better than just a line
    ax[1].fill_between(d1['Distance'], d1['Throttle'], color=c1, alpha=0.3, label=f'{name1} Throttle')
    ax[1].fill_between(d2['Distance'], d2['Throttle'], color=c2, alpha=0.1)
    ax[1].plot(d1['Distance'], d1['Brake']*100, color='white', linewidth=1, label='Brake Application')
    ax[1].set_ylabel('Pedal %', fontsize=12, fontweight='bold')
    ax[1].set_ylim(0, 105)

    # --- Plot 3: Steering Angle (Cornering) ---
    ax[2].plot(d1['Distance'], d1['SteeringWheelAngle'], color=c1, linewidth=1.5)
    ax[2].plot(d2['Distance'], d2['SteeringWheelAngle'], color=c2, linewidth=1.5, linestyle=':')
    ax[2].set_ylabel('Steering Angle', fontsize=12, fontweight='bold')
    ax[2].axhline(0, color='gray', linewidth=0.5)

    # --- Plot 4: G-Force (The Physics Stress) ---
    ax[3].plot(d1['Distance'], d1['G_Long'], color=c1, alpha=0.8)
    ax[3].plot(d2['Distance'], d2['G_Long'], color=c2, alpha=0.6, linestyle='--')
    ax[3].set_ylabel('G-Force (Long)', fontsize=12, fontweight='bold')
    ax[3].set_xlabel('Distance (meters)', fontsize=12)
    ax[3].axhline(0, color='white', linewidth=1)

    plt.suptitle(f'Apex Intelligence: {name1} vs {name2} Performance Analysis', fontsize=16)
    plt.show()

if __name__ == "__main__":
    plot_pro_dashboard('telemetry_LEC_Monaco_2025', 'telemetry_HAM_Monaco_2025', "Leclerc", "Hamilton")