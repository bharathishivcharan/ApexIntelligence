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

if available_data:
    # This creates the dropdown "Remote Control"
    selected_session = st.sidebar.selectbox("Select Telemetry Data:", available_data)
    st.sidebar.success(f"Connected to: {selected_session}")
else:
    st.sidebar.error("Database is empty. Waiting for Robot update...")

# --- ANALYSIS TABS ---
tab1, tab2 = st.tabs(["📊 Performance Overview", "📜 2026 Rules (AI)"])

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