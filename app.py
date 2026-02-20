import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# PAGE SETUP 
st.set_page_config(page_title="Apex Intelligence 2026", layout="wide")
plt.style.use('dark_background') 

# --- DATA LOGIC ---
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
available_data = get_all_sessions()
if available_data:
    display_names = [name.replace('telemetry_', '').replace('_', ' ').title() for name in available_data]
    name_map = dict(zip(display_names, available_data))
    st.sidebar.info("💡 Select 2 drivers to unlock the 'Battle Mode' analytics suite.")
    selected_drivers = st.sidebar.multiselect("Select Drivers:", display_names)
    all_selected_data = {name: load_telemetry(name_map[name]) for name in selected_drivers}

tab1, tab2 = st.tabs([" Performance Overview", " 2026 Rules Librarian"])

with st.expander(" Data Source & Methodology", expanded=False):
    st.write("""
    - **Dataset:** 2025 Spanish Grand Prix (Qualifying) via FastF1.
    - **Simulation:** 2026 MGU-K Energy Recovery Model ($0.05\%$ harvest on brake, $0.08\%$ drain on >80% throttle).
    - **AI Engine:** RAG (Retrieval-Augmented Generation) using FAISS and Llama 3.1 via Groq.
    """)

with tab1:
    if not selected_drivers:
        st.info("Please select drivers in the sidebar to begin analysis.")
    else:
        # 1. INDIVIDUAL ANALYSIS CARDS
        for driver in selected_drivers:
            with st.expander(f"Data Profile: {driver}", expanded=(len(selected_drivers)==1)):
                df = all_selected_data[driver]
                c1, c2, c3 = st.columns(3)
                c1.metric("Top Speed", f"{df['Speed'].max():.1f} km/h")
                c2.metric("Avg Speed", f"{df['Speed'].mean():.1f} km/h")
                c3.metric("Data Points", len(df))
                st.pyplot(plot_professional_telemetry(df, driver))

        # 2. BATTLE MODE (Maximum Detailing)
        if len(selected_drivers) == 2:
            st.divider()
            st.header("Head-to-Head Battle Analysis")
            
            d1_name, d2_name = selected_drivers[0], selected_drivers[1]
            data1 = calculate_2026_energy(all_selected_data[d1_name])
            data2 = calculate_2026_energy(all_selected_data[d2_name])

            # Layout: Track Map and Sector Table
            col_left, col_right = st.columns([1.5, 1])
            with col_left:
                st.subheader("Circuit Dominance Map")
                st.pyplot(plot_track_dominance(data1, data2, d1_name, d2_name))
                st.caption(f"Color Key: {d1_name} (#00A19B) | {d2_name} (#FF0000)")
            
            with col_right:
                st.subheader("Sector Pace (km/h)")
                s1, s2 = get_sector_stats(data1), get_sector_stats(data2)
                comp_df = pd.DataFrame({
                    "Sector": ["S1", "S2", "S3"],
                    d1_name.split()[0].upper(): [f"{s1['S1']:.1f}", f"{s1['S2']:.1f}", f"{s1['S3']:.1f}"],
                    d2_name.split()[0].upper(): [f"{s2['S1']:.1f}", f"{s2['S2']:.1f}", f"{s2['S3']:.1f}"]
                })

                # Display it without the index column
                st.dataframe(comp_df, hide_index=True, width="stretch")
                
                
                # AI Insights Button

                if st.button("Generate AI Engineer Briefing"):
                    if "vector_db" in st.session_state:
                        from src.rule_processor import ask_ai
        
                        # Create a detailed prompt based on the actual data we see on screen
                        avg_v1 = data1['Speed'].mean()
                        avg_v2 = data2['Speed'].mean()
                        faster_driver = d1_name if avg_v1 > avg_v2 else d2_name
        
                        summary_query = (
                            f"Compare {d1_name} and {d2_name}. "
                            f"{faster_driver} is faster on average by {abs(avg_v1-avg_v2):.1f} km/h. "
                            f"Based on 2026 Technical Regulations, how should the slower driver adjust "
                            f"their energy recovery (MGU-K) strategy to compete?"
                        )
        
                        with st.spinner("Race Engineer is thinking..."):
                            response = ask_ai(summary_query, st.session_state.vector_db)
                            st.markdown(f"Engineer's Report\n{response}")
                    else:
                        st.warning("Please go to the '2026 Rules Librarian' tab and click 'Initialize Librarian' first!")

            # 3. ENERGY SIMULATION
            st.subheader("2026 Energy Deployment Simulation (MGU-K)")
            fig_ers, ax_ers = plt.subplots(figsize=(12, 3))
            ax_ers.plot(data1.index, data1['SoC'], color='#00A19B', label=f"{d1_name} SoC")
            ax_ers.plot(data2.index, data2['SoC'], color='#FF0000', label=f"{d2_name} SoC")
            ax_ers.set_ylabel("Battery %")
            ax_ers.legend()
            st.pyplot(fig_ers)

            # 4. SPEED DELTA
            st.subheader(f"Live Speed Delta: {d1_name.split()[0].upper()} vs {d2_name.split()[0].upper()}")
            v1, v2 = data1['Speed'].values, data2['Speed'].values
            min_l = min(len(v1), len(v2))
            delta = v1[:min_l] - v2[:min_l]
            fig_d, ax_d = plt.subplots(figsize=(12, 3))
            ax_d.fill_between(range(min_l), delta, 0, where=(delta>=0), color='#15FF00', alpha=0.3, label=f"{d1_name.split()[0]} Faster")
            ax_d.fill_between(range(min_l), delta, 0, where=(delta<0), color='#FF0000', alpha=0.3, label=f"{d2_name.split()[0]} Faster")
            ax_d.plot(delta, color='white', linewidth=0.5, alpha=0.5)
            ax_d.axhline(0, color='gray', linestyle='--')
            ax_d.legend(loc='upper right')
            st.pyplot(fig_d)

with tab2:
    st.header("2026 Technical Assistant")
    if st.button("Initialize Librarian"):
        with st.spinner("Analyzing Knowledge Base..."):
            from src.rule_processor import load_rules, create_chunks, get_vector_db
            raw_text = load_rules("knowledge_base") 
            chunks = create_chunks(raw_text)
            st.session_state.vector_db = get_vector_db(chunks)
            st.success("Librarian is ready!")

    if "vector_db" in st.session_state:
        query = st.chat_input("Ask a question about the 2026 rules...")
        if query:
            with st.chat_message("user"): st.write(query)
            with st.chat_message("assistant"):
                from src.rule_processor import ask_ai
                st.write(ask_ai(query, st.session_state.vector_db))