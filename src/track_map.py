import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import os

plt.style.use('dark_background')

def generate_track_map(table_name, driver_name):
    # 1. Load Data
    conn = sqlite3.connect('data/f1_data.db')
    df = pd.read_sql(f"SELECT X, Y, Speed FROM {table_name}", conn)
    conn.close()

    # 2. Prepare Segments
    #(X, Y) points into [ (x1, y1), (x2, y2) ] segments
    points = np.array([df['X'], df['Y']]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # 3. Create the Plot
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Red = Slow (Hairpins), Green = Fast (Tunnel/Straights)
    cmap = plt.get_cmap('RdYlGn')
    norm = plt.Normalize(df['Speed'].min(), df['Speed'].max())
    
    # LineCollection
    lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=8, capstyle='round')
    lc.set_array(df['Speed'])
    
    # Add the track to the plot
    line = ax.add_collection(lc)

    # 4. Aesthetics
    ax.set_xlim(df['X'].min() - 300, df['X'].max() + 300)
    ax.set_ylim(df['Y'].min() - 300, df['Y'].max() + 300)
    ax.axis('off') 
    ax.set_aspect('equal')
    
    # Add a Colorbar to show what the colors mean
    cbar = fig.colorbar(line, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Speed (km/h)', fontsize=12, fontweight='bold')

    plt.title(f'Circuit de Monaco: {driver_name} Speed Heatmap (2025)', 
              fontsize=15, fontweight='bold', color='white', pad=20)

    # Save the visual for your README
    plt.savefig(f'visuals/{driver_name}_map.png', bbox_inches='tight', dpi=300)
    print(f"Track map saved to visuals/{driver_name}_map.png")
    

    if not os.path.exists('visuals'):
        os.makedirs('visuals')

    plt.savefig(f'visuals/{driver_name}_map.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    generate_track_map('telemetry_LEC_Monaco_2025', 'Leclerc')