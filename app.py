import streamlit as st
import sqlite3
import pandas as pd
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Apex Intelligence 2026", layout="wide")

def get_all_sessions():
    """Ask the database for a list of all telemetry tables it has saved."""
    if not os.path.exists('data/f1_data.db'):
        return []
    
    conn = sqlite3.connect('data/f1_data.db')
    
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(query, conn)
    conn.close()
    return tables['name'].tolist()

# --- THE UI ---
st.title("Apex Intelligence: Command Center")

# Sidebar for picking the driver/session
st.sidebar.header("Session Control")
available_data = get_all_sessions()
selected_session = "No Data Available"

if available_data:
    # Using this function to make table names nicer
    display_names = [name.replace('_', ' ') for name in available_data]
    
    #Using Zip to make a better name for the table
    name_map = dict(zip(display_names, available_data))
    
    selected_display = st.sidebar.selectbox("Select Telemetry Data:", display_names)
    selected_session = name_map[selected_display] # This is the real name we use for code
    
    st.sidebar.success(f"Connected to: {selected_display}")
else:
    st.sidebar.error("Database is empty. Waiting for Robot update...")

# --- ANALYSIS TABS ---
tab1, tab2 = st.tabs(["Performance Overview", " 2026 Rules"])

with tab1:
    st.subheader(f"Session Analysis: {selected_session if available_data else 'No Data'}")
    
    # Placeholder for the graphs we made earlier
    col1, col2 = st.columns(2)
    with col1:
        st.info("Speed/Throttle Heatmap")
        
    with col2:
        st.info("Time Delta (Ghost Car)")

with tab2:
    st.warning("RAG Agent Offline: Rulebook integration scheduled for Day 8.")
    
