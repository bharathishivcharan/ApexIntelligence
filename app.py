import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# PAGE SETUP
st.set_page_config(page_title="Apex Intelligence 2026", layout="wide")
plt.style.use('dark_background') 

# LOGIC

def get_all_sessions():
    """Fetches list of tables, EXCLUDING the calendar."""
    if not os.path.exists('data/f1_data.db'):
        return []
    conn = sqlite3.connect('data/f1_data.db')
    # Filter out the calendar to keep the dropdown clean
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name != 'calendar';"
    tables = pd.read_sql(query, conn)
    conn.close()
    return tables['name'].tolist()

def load_telemetry(table_name):
    """Loads data and ensures column names are standardized."""
    conn = sqlite3.connect('data/f1_data.db')
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    # Ensure columns like 'speed' become 'Speed' for the code to work
    df.columns = [c.capitalize() for c in df.columns]
    return df

def plot_professional_telemetry(df, driver_name):
    """The 3-Pane Performance Signature."""
    fig, (ax_speed, ax_throttle, ax_brake) = plt.subplots(
        3, 1, figsize=(12, 10), sharex=True, 
        gridspec_kw={'height_ratios': [2, 1, 1]}
    )
    # Speed (Teal)
    ax_speed.plot(df.index, df['Speed'], color='#00A19B', linewidth=2)
    ax_speed.set_ylabel("Speed (km/h)")
    ax_speed.set_title(f"Performance Signature: {driver_name}", fontsize=16)
    ax_speed.grid(alpha=0.1)
    
    # Throttle (Green)
    if 'Throttle' in df.columns:
        ax_throttle.plot(df.index, df['Throttle'], color='#15FF00', linewidth=1.5)
        ax_throttle.fill_between(df.index, df['Throttle'], color='#15FF00', alpha=0.2)
    ax_throttle.set_ylabel("Throttle %")
    ax_throttle.grid(alpha=0.1)
    
    # Brake (Red)
    if 'Brake' in df.columns:
        ax_brake.plot(df.index, df['Brake'], color='#FF0000', linewidth=1.5)
        ax_brake.fill_between(df.index, df['Brake'], color='#FF0000', alpha=0.2)
    ax_brake.set_ylabel("Brake")
    ax_brake.set_xlabel("Time Samples")
    ax_brake.grid(alpha=0.1)

    plt.tight_layout()
    return fig

# --- THE UI ---
st.title("Apex Intelligence: Command Center")

# Sidebar
st.sidebar.header("Session Control")
available_data = get_all_sessions()

# PRE-DEFINE TABS so the variables always exist
tab1, tab2 = st.tabs([" Performance Overview", "2026 Rules"])

if available_data:
    display_names = []
    for name in available_data:
        clean_name = name.replace('telemetry', '').replace('_', ' ').strip()
        clean_name = clean_name.title()
        display_names.append(clean_name)
    
    name_map = dict(zip(display_names, available_data))
    
    selected_display = st.sidebar.selectbox("Select Telemetry Data:", display_names)
    selected_table = name_map[selected_display] 
    
    data = load_telemetry(selected_table)

    with tab1:
        if 'Speed' in data.columns:
            st.sidebar.success(f"Selected: {selected_display}")
            # Metric Cards
            max_speed = data['Speed'].max()
            avg_speed = data['Speed'].mean()
            c1, c2, c3 = st.columns(3)
            c1.metric("Max Speed", f"{max_speed:.1f} km/h")
            c2.metric("Avg Speed", f"{avg_speed:.1f} km/h")
            c3.metric("Samples", len(data))

            st.subheader(f"Session Analysis: {selected_display}")
            fig = plot_professional_telemetry(data, selected_display)
            st.pyplot(fig)

with tab2:
    st.info("The AI Rulebook Agent will be integrated here on Day 8.")