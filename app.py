import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

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
    return df

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
    ax_speed.plot(df.index, df['Speed'], color='#00A19B', linewidth=2)
    ax_speed.set_ylabel("Speed (km/h)")
    ax_speed.set_title(f"Performance Signature: {driver_name}", fontsize=14)
    if 'Throttle' in df.columns:
        ax_throttle.plot(df.index, df['Throttle'], color='#15FF00', alpha=0.7)
        ax_throttle.fill_between(df.index, df['Throttle'], color='#15FF00', alpha=0.1)
    if 'Brake' in df.columns:
        ax_brake.plot(df.index, df['Brake'], color='#FF0000', alpha=0.7)
        ax_brake.fill_between(df.index, df['Brake'], color='#FF0000', alpha=0.1)
    plt.tight_layout()
    return fig

def plot_track_dominance(data1, data2, name1, name2):
    """Visualizes which driver is faster at every coordinate of the circuit."""
    min_l = min(len(data1), len(data2))
    x = data1['X'].values[:min_l]
    y = data1['Y'].values[:min_l]
    delta = data1['Speed'].values[:min_l] - data2['Speed'].values[:min_l]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    for i in range(len(x)-1):
        color = '#00A19B' if delta[i] > 0 else '#FF0000'
        ax.plot(x[i:i+2], y[i:i+2], color=color, linewidth=5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"Track Dominance: {name1.split()[0]} vs {name2.split()[0]}", color='white')
    return fig

# MAIN UI
st.title("Apex Intelligence: Command Center")

# 1. Fetch available tables from SQLite
available_data = get_all_sessions()

if available_data:
    # 2. Map database names to readable names 
    display_names = [name.replace('telemetry_', '').replace('_', ' ').title() for name in available_data]
    name_map = dict(zip(display_names, available_data))
    drivers_list = display_names

    st.sidebar.header("Configuration")
    st.sidebar.info("💡 Select drivers here to analyze telemetry and rules.")
    
    # 3. SELECTOR
    selected_drivers = st.sidebar.multiselect(
        "Select Drivers:", 
        options=drivers_list, 
        key="main_driver_selector" # Unique key prevents duplicate widget errors
    )

    # 4. Load data ONLY for what is selected
    all_selected_data = {name: load_telemetry(name_map[name]) for name in selected_drivers}
else:
    st.sidebar.error("Database not found! Ensure 'data/f1_data.db' is on GitHub.")
    drivers_list = []
    selected_drivers = []
    all_selected_data = {}

#  TABS 
tab1, tab2 = st.tabs([" Performance Overview", " 2026 Rules Librarian"])

# Methodology Expander (Global)
with st.expander("Data Source & Methodology", expanded=False):
    st.write("""
    - **Dataset:** 2025 Spanish Grand Prix (Qualifying) via FastF1.
    - **Simulation:** 2026 MGU-K Energy Recovery Model ($0.05\%$ harvest, $0.08\%$ drain).
    - **AI Engine:** RAG using FAISS and Llama 3.3 via Groq.
    """)

# --- TAB 1: PERFORMANCE ---
with tab1:
    if not selected_drivers:
        st.warning(" Please select at least one driver in the sidebar to begin.")
    else:
        # 1. INDIVIDUAL ANALYSIS CARDS
        for driver in selected_drivers:
            # Safety check: ensures the driver actually exists in our data dictionary
            if driver in all_selected_data:
                with st.expander(f"Data Profile: {driver}", expanded=(len(selected_drivers)==1)):
                    df = all_selected_data[driver]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Top Speed", f"{df['Speed'].max():.1f} km/h")
                    c2.metric("Avg Speed", f"{df['Speed'].mean():.1f} km/h")
                    c3.metric("Data Points", len(df))
                    st.pyplot(plot_professional_telemetry(df, driver))

        # 2. BATTLE MODE (Active when exactly 2 are selected)
        if len(selected_drivers) == 2:
            st.divider()
            st.header("Head-to-Head Battle Analysis")
            
            d1_name, d2_name = selected_drivers[0], selected_drivers[1]
            data1 = calculate_2026_energy(all_selected_data[d1_name])
            data2 = calculate_2026_energy(all_selected_data[d2_name])

            col_left, col_right = st.columns([1.5, 1])
            with col_left:
                st.subheader("Circuit Dominance Map")
                st.pyplot(plot_track_dominance(data1, data2, d1_name, d2_name))
            
            with col_right:
                st.subheader("Sector Pace (km/h)")
                s1, s2 = get_sector_stats(data1), get_sector_stats(data2)
                comp_df = pd.DataFrame({
                    "Sector": ["S1", "S2", "S3"],
                    d1_name.split()[0].upper(): [f"{s1['S1']:.1f}", f"{s1['S2']:.1f}", f"{s1['S3']:.1f}"],
                    d2_name.split()[0].upper(): [f"{s2['S1']:.1f}", f"{s2['S2']:.1f}", f"{s2['S3']:.1f}"]
                })
                st.dataframe(comp_df, hide_index=True, use_container_width=True)
                
                if st.button("Generate AI Engineer Briefing"):
                    if "vector_db" in st.session_state:
                        from src.rule_processor import ask_ai
                        avg_v1, avg_v2 = data1['Speed'].mean(), data2['Speed'].mean()
                        faster = d1_name if avg_v1 > avg_v2 else d2_name
                        query = f"Compare {d1_name} and {d2_name}. {faster} is faster. Suggest 2026 MGU-K strategies."
                        with st.spinner("Consulting Rulebook..."):
                            st.info(ask_ai(query, st.session_state.vector_db))
                    else:
                        st.error("Go to Tab 2 and Initialize Librarian first!")

            st.subheader("2026 Energy Deployment Simulation (MGU-K)")
            fig_ers, ax_ers = plt.subplots(figsize=(12, 3))
            ax_ers.plot(data1.index, data1['SoC'], color='#00A19B', label=d1_name)
            ax_ers.plot(data2.index, data2['SoC'], color='#FF0000', label=d2_name)
            ax_ers.set_ylabel("Battery %")
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