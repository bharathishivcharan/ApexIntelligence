import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data(table_name):
    conn = sqlite3.connect('data/f1_data.db')
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    
    #  Distance calculation
    df['Speed_ms'] = df['Speed'] / 3.6
    df['Distance'] = (df['Speed_ms'] * df['Time'].diff().fillna(0)).cumsum()
    return df

def plot_mechanical(table_name, driver_name):
    df = load_data(table_name)
    
    # 1. Find V-max (Top Speed)
    v_max = df['Speed'].max()
    # Find the distance where V-max happened
    v_max_dist = df.loc[df['Speed'].idxmax(), 'Distance']
    
    fig, ax = plt.subplots(figsize=(15, 7))
    
    # 2. Plot the main speed line
    ax.plot(df['Distance'], df['Speed'], label=f'{driver_name} Speed', color='green', alpha=0.3)
    
    # 3. Highlight Gear Shifts
    # Plot every 20th data point for gears so the graph isn't crowded
    for i in range(0, len(df), 20):
        ax.annotate(int(df['nGear'].iloc[i]), 
                    (df['Distance'].iloc[i], df['Speed'].iloc[i]),
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center', 
                    fontsize=8, 
                    color='cyan')

    # 4. Mark the Speed Trap (V-max)
    ax.scatter(v_max_dist, v_max, color='red', s=100, zorder=5)
    ax.annotate(f'V-max: {v_max:.1f} km/h', 
                (v_max_dist, v_max), 
                xytext=(0, 15), 
                textcoords='offset points', 
                ha='center', 
                arrowprops=dict(arrowstyle='->', color='red'))

    ax.set_title(f'Mechanical Analysis: {driver_name} - Monaco 2025')
    ax.set_xlabel('Distance (meters)')
    ax.set_ylabel('Speed (km/h)')
    ax.grid(True, alpha=0.2)

def compare_mechanical(table1, table2, name1, name2):
    df1 = load_data(table1)
    df2 = load_data(table2)

    fig, ax = plt.subplots(2, 1, figsize=(15, 12), sharex=True)

    # --- TOP PLOT: GEARS ---
    # "Step" plot for gears because gears don't have "3.5", they jump from 3 to 4.
    ax[0].step(df1['Distance'], df1['nGear'], where='post', label=name1, color='red', linewidth=2)
    ax[0].step(df2['Distance'], df2['nGear'], where='post', label=name2, color='blue', linestyle='--', linewidth=2)
    
    ax[0].set_title(f'Gearing Strategy: {name1} vs {name2}')
    ax[0].set_ylabel('Gear Number')
    ax[0].set_ylim(0, 9)
    ax[0].legend()
    ax[0].grid(True, alpha=0.2)

    # --- BOTTOM PLOT: SPEED ---
    ax[1].plot(df1['Distance'], df1['Speed'], color='darkblue', label=name1)
    ax[1].plot(df2['Distance'], df2['Speed'], color='darkred', linestyle='--', label=name2)
    
    ax[1].set_ylabel('Speed (km/h)')
    ax[1].set_xlabel('Distance (meters)')
    ax[1].legend()
    ax[1].grid(True, alpha=0.2)

    plt.tight_layout()
    

def plot_rpm_profile(table_name, driver_name):
    df = load_data(table_name)
    
    plt.figure(figsize=(15, 6))
    
    # 1. Plot RPM
    scatter = plt.scatter(df['Distance'], df['RPM'], c=df['nGear'], cmap='viridis', s=1)
    
    # 2. Add a Colorbar to show which color is which gear
    cbar = plt.colorbar(scatter)
    cbar.set_label('Gear')
    
    plt.title(f'Engine Power Band: {driver_name} - Monaco 2025')
    plt.xlabel('Distance (meters)')
    plt.ylabel('RPM')
    plt.grid(True, alpha=0.3)
    

if __name__ == "__main__":
    TABLE_LEC = 'telemetry_LEC_Monaco_2025'
    TABLE_HAM = 'telemetry_HAM_Monaco_2025'
    
    plot_mechanical(TABLE_LEC, "Leclerc")
    compare_mechanical(TABLE_LEC, TABLE_HAM, "Leclerc", "Hamilton")
    plot_rpm_profile(TABLE_LEC, "Leclerc")   
    # show everything at once!
    print("Opening all analysis windows...")
    plt.show()