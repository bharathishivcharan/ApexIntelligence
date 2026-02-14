import streamlit as st
import os

# 1. Page Configuration
st.set_page_config(page_title="Apex Intelligence F1", layout="wide")

st.title("Apex Intelligence: 2026 Strategy Command Center")
st.markdown("---")

# 2. Sidebar for Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to:", ["Lap Analysis", "Telemetry Comparison", "2026 Regulations"])

# 3. Main Display Logic
if page == "Lap Analysis":
    st.subheader("Circuit Speed Heatmap")
    
    if os.path.exists('visuals/Leclerc_map.png'):
        st.image('visuals/Leclerc_map.png', caption="Monaco GP Speed Profile")
    else:
        st.warning("Heatmap not found. Run src/track_map.py first!")

elif page == "Telemetry Comparison":
    st.subheader("Head-to-Head: Leclerc vs Hamilton")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if os.path.exists('visuals/Leclerc_speed_profile.png'):
            st.image('visuals/Leclerc_speed_profile.png', caption="Speed & Pedal Inputs")
            
    with col2:
        if os.path.exists('visuals/time_delta.png'):
            st.image('visuals/time_delta.png', caption="Live Time Delta (The 'Ghost Car')")

elif page == "2026 Regulations":
    st.info("AI Rulebook Agent coming on Day 8...")