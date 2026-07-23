import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from services.telemetry_service import TelemetryService

telemetry_service = TelemetryService()

# PAGE SETUP 
st.set_page_config(page_title="Apex Intelligence 2026", layout="wide")
plt.style.use('dark_background') 

# DATA LOGIC 
def get_all_sessions():
    if not os.path.exists('data/f1_data.db'): return []
    conn = sqlite3.connect('data/f1_data.db')
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name != 'calendar';"
    tables = pd.read_sql(query, conn)
    conn.close()
    return tables['name'].tolist()

def load_telemetry(table_name):
    conn = sqlite3.connect('data/f1_data.db')
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    df.columns = [c.capitalize() for c in df.columns]

    # Convert Time to float if it's not already
    df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    
    # 1. Distance Math
    df['Speed_ms'] = df['Speed'] / 3.6
    dt = df['Time'].diff().fillna(0.1) # Time between points
    df['Distance'] = (df['Speed_ms'] * dt).cumsum()

    # 2. G-Force Math (Acceleration / 9.81)
    # We use a small 'limit' to avoid infinity errors
    acceleration = df['Speed_ms'].diff() / dt.replace(0, 0.1)
    df['G_Long'] = acceleration / 9.81
    
    return df

def plot_professional_telemetry(df, driver_name):
    """Detailed single-driver telemetry stack with clear labels."""
    fig, (ax_speed, ax_throttle, ax_brake) = plt.subplots(3, 1, figsize=(10, 8), 
                                                        sharex=True, 
                                                        gridspec_kw={'height_ratios': [2, 1, 1]})
    
    # Plot 1: Speed
    ax_speed.plot(df['Distance'], df['Speed'], color='#00A19B', linewidth=2)
    ax_speed.set_ylabel("Speed (km/h)", fontsize=10, fontweight='bold')
    ax_speed.set_title(f"Performance Signature: {driver_name}", fontsize=14, pad=15)
    ax_speed.grid(visible=True, alpha=0.1)

    # Plot 2: Throttle
    if 'Throttle' in df.columns:
        ax_throttle.plot(df['Distance'], df['Throttle'], color='#15FF00', alpha=0.8)
        ax_throttle.fill_between(df['Distance'], df['Throttle'], color='#15FF00', alpha=0.1)
        ax_throttle.set_ylabel("Throttle %", fontsize=10)
        ax_throttle.set_ylim(-5, 105)

    # Plot 3: Brake
    if 'Brake' in df.columns:
        ax_brake.plot(df['Distance'], df['Brake'], color='#FF0000', alpha=0.8)
        ax_brake.fill_between(df['Distance'], df['Brake'], color='#FF0000', alpha=0.1)
        ax_brake.set_ylabel("Brake %", fontsize=10)
        ax_brake.set_xlabel("Distance along lap (meters)", fontsize=10, fontweight='bold')
        ax_brake.set_ylim(-5, 105)

    plt.tight_layout()
    return fig

def plot_time_delta(d1, d2, name1, name2):
    """Calculates the Gap. If line is UP, Driver 2 is leading. If DOWN, Driver 1 is leading."""
    track_length = max(d1['Distance'].max(), d2['Distance'].max())
    common_dist = np.linspace(0, track_length, 2000)
    
    # We use Time_sec (ensure this exists in your load_telemetry)
    time1_interp = np.interp(common_dist, d1['Distance'], d1['Time'])
    time2_interp = np.interp(common_dist, d2['Distance'], d2['Time'])
    delta = time1_interp - time2_interp # Negative = D1 faster, Positive = D2 faster
    
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(common_dist, delta, color='yellow', linewidth=2)
    
    # Visual cues for who is faster
    ax.fill_between(common_dist, delta, 0, where=(delta < 0), color='#00A19B', alpha=0.3, label=f"{name1} Gaining")
    ax.fill_between(common_dist, delta, 0, where=(delta > 0), color='#FF0000', alpha=0.3, label=f"{name2} Gaining")
    
    ax.axhline(0, color='white', linestyle='--', alpha=0.5)
    ax.set_ylabel("Time Gap (s)", fontweight='bold')
    ax.set_xlabel("Track Distance (meters)", fontweight='bold')
    ax.legend(loc='upper right', fontsize='small')
    return fig

# SIMULATION & ANALYTICS 
def calculate_2026_energy(df):
    """Simulates 2026 MGU-K harvesting/deployment logic."""
    soc = 100.0
    soc_history = []
    for _, row in df.iterrows():
        if row.get('Brake', 0) > 0: soc += 0.05
        elif row.get('Throttle', 0) > 80: soc -= 0.08
        soc = max(0, min(100, soc))
        soc_history.append(soc)
    df['SoC'] = soc_history
    return df

def get_sector_stats(df):
    """Splits lap into technical sectors."""
    n = len(df)
    return {
        "S1": df.iloc[:n//3]['Speed'].mean(),
        "S2": df.iloc[n//3 : 2*n//3]['Speed'].mean(),
        "S3": df.iloc[2*n//3:]['Speed'].mean()
    }

# PLOTTING FUNCTIONS 
def plot_professional_telemetry(df, driver_name):
    """Detailed single-driver telemetry stack."""
    fig, (ax_speed, ax_throttle, ax_brake) = plt.subplots(3, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})
    ax_speed.plot(df['Distance'], df['Speed'], color='#00A19B', linewidth=2)
    ax_speed.set_ylabel("Speed (km/h)")
    ax_speed.set_title(f"Performance Signature: {driver_name}", fontsize=14)
    if 'Throttle' in df.columns:
        ax_throttle.plot(df['Distance'], df['Throttle'], color='#15FF00', alpha=0.7)
        ax_throttle.fill_between(df['Distance'], df['Throttle'], color='#15FF00', alpha=0.1)
    if 'Brake' in df.columns:
        ax_brake.plot(df['Distance'], df['Brake'], color='#FF0000', alpha=0.7)
        ax_brake.fill_between(df['Distance'], df['Brake'], color='#FF0000', alpha=0.1)
    ax_brake.set_xlabel("Distance (m)")
    plt.tight_layout()
    return fig

def plot_track_dominance(data1, data2, name1, name2):
    """Visualizes which driver is faster at every coordinate of the circuit."""
    min_l = min(len(data1), len(data2))
    x = data1['X'].values[:min_l]
    y = data1['Y'].values[:min_l]
    delta = data1['Speed'].values[:min_l] - data2['Speed'].values[:min_l]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    # Using a faster method for plotting the dominance line
    for i in range(0, len(x)-1, 5): # Step by 5 for performance
        color = '#00A19B' if delta[i] > 0 else '#FF0000'
        ax.plot(x[i:i+6], y[i:i+6], color=color, linewidth=4)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"Track Dominance: {name1.split()[0]} vs {name2.split()[0]}", color='white')
    return fig

def plot_time_delta(d1, d2, name1, name2):
    """Calculates and plots the Gap (Tug of War) from your compare_drivers.py"""
    track_length = max(d1['Distance'].max(), d2['Distance'].max())
    common_dist = np.linspace(0, track_length, 2000)
    # Interpolate time onto the common distance ruler
    time1_interp = np.interp(common_dist, d1['Distance'], d1['Time'])
    time2_interp = np.interp(common_dist, d2['Distance'], d2['Time'])
    delta = time1_interp - time2_interp
    
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(common_dist, delta, color='yellow', linewidth=2)
    ax.fill_between(common_dist, delta, 0, where=(delta > 0), color='#FF0000', alpha=0.3)
    ax.fill_between(common_dist, delta, 0, where=(delta < 0), color='#00A19B', alpha=0.3)
    ax.axhline(0, color='white', linestyle='--', alpha=0.5)
    ax.set_ylabel("Gap (sec)")
    ax.set_title(f"Time Delta: {name1} vs {name2}")
    return fig

# MAIN UI
st.title("Apex Intelligence: Command Center")

available_data = telemetry_service.get_available_sessions()

if available_data:
    display_names = [name.replace('telemetry_', '').replace('_', ' ').title() for name in available_data]
    name_map = dict(zip(display_names, available_data))
    drivers_list = display_names

    st.sidebar.header("Configuration")
    selected_drivers = st.sidebar.multiselect("Select Drivers:", options=drivers_list, key="main_driver_selector")
    all_selected_data = {
        name: telemetry_service.get_processed_telemetry(name_map[name])
        for name in selected_drivers
    } 
else:
    st.sidebar.error("Database not found!")
    selected_drivers = []

tab1, tab2 = st.tabs([" Performance Overview", " 2026 Rules Librarian"])

with st.expander("Data Source & Methodology", expanded=False):
    st.write("- **Dataset:** 2025 Spanish Grand Prix Qualifying via FastF1.")
    st.write("- **Simulation:** 2026 MGU-K Model (0.05% harvest, 0.08% drain).")

# --- TAB 1: PERFORMANCE ---
with tab1:
    if not selected_drivers:
        st.warning("Please select at least one driver in the sidebar.")
    else:
        for driver in selected_drivers:
            if driver in all_selected_data:
                with st.expander(f"Data Profile: {driver}", expanded=(len(selected_drivers)==1)):
                    df = all_selected_data[driver]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Top Speed", f"{df['Speed'].max():.1f} km/h")
                    c2.metric("Max G-Force", f"{df['G_Long'].min():.2f} G") # Braking force
                    c3.metric("Data Points", len(df))
                    st.pyplot(plot_professional_telemetry(df, driver))

        if len(selected_drivers) == 2:
            st.divider()
            st.header("Head-to-Head Battle Analysis")
            d1_name, d2_name = selected_drivers[0], selected_drivers[1]
            data1 = calculate_2026_energy(all_selected_data[d1_name])
            data2 = calculate_2026_energy(all_selected_data[d2_name])

            # Track and Sector Comparison
            col_left, col_right = st.columns([1.5, 1])
            with col_left:
                st.pyplot(plot_track_dominance(data1, data2, d1_name, d2_name))
            with col_right:
                st.subheader("Sector Pace (km/h)")
                s1, s2 = get_sector_stats(data1), get_sector_stats(data2)
                st.table(pd.DataFrame({
                    "Sector": ["S1", "S2", "S3"],
                    d1_name.split()[0]: [f"{s1['S1']:.1f}", f"{s1['S2']:.1f}", f"{s1['S3']:.1f}"],
                    d2_name.split()[0]: [f"{s2['S1']:.1f}", f"{s2['S2']:.1f}", f"{s2['S3']:.1f}"]
                }))

            # Time Delta Plot 
            st.subheader("Distance-Based Time Gap")
            st.pyplot(plot_time_delta(data1, data2, d1_name, d2_name))

            # Energy Simulation Plot
            st.subheader("2026 Energy Deployment (MGU-K)")
            fig_ers, ax_ers = plt.subplots(figsize=(12, 3))
            ax_ers.plot(data1['Distance'], data1['SoC'], color='#00A19B', label=d1_name)
            ax_ers.plot(data2['Distance'], data2['SoC'], color='#FF0000', label=d2_name)
            ax_ers.set_ylabel("Battery %")
            ax_ers.set_xlabel("Distance (m)")
            ax_ers.legend()
            st.pyplot(fig_ers)

#  TAB 2: LIBRARIAN 
with tab2:
    st.header("2026 Technical Assistant")
    
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Missing 'GROQ_API_KEY' in Streamlit Secrets!")
    else:
        if "vector_db" not in st.session_state:
            st.info("The Librarian needs to process the 2026 Regulations.")
            if st.button(" Initialize Librarian"):
                try:
                    with st.spinner("Analyzing Knowledge Base..."):
                        from src.rule_processor import load_rules, create_chunks, get_vector_db
                        raw_text = load_rules("knowledge_base") 
                        chunks = create_chunks(raw_text)
                        st.session_state.vector_db = get_vector_db(chunks)
                        st.rerun()
                except Exception as e:
                    st.error(f"Init Error: {e}")
        else:
            st.success("Engineer is Online ")
            user_q = st.chat_input("Ask about the 2026 Technical Regs...")
            if user_q:
                with st.chat_message("user"): st.write(user_q)
                with st.chat_message("assistant"):
                    from src.rule_processor import ask_ai
                    st.write(ask_ai(user_q, st.session_state.vector_db))