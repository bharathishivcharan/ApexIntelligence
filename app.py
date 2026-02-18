import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- PAGE SETUP ---
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

# --- PLOTTING FUNCTIONS ---
def plot_professional_telemetry(df, driver_name):
    fig, (ax_speed, ax_throttle, ax_brake) = plt.subplots(3, 1, figsize=(12, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})
    ax_speed.plot(df.index, df['Speed'], color='#00A19B', linewidth=2)
    ax_speed.set_ylabel("Speed (km/h)")
    ax_speed.set_title(f"Performance Signature: {driver_name}", fontsize=16)
    if 'Throttle' in df.columns:
        ax_throttle.plot(df.index, df['Throttle'], color='#15FF00', linewidth=1.5)
        ax_throttle.fill_between(df.index, df['Throttle'], color='#15FF00', alpha=0.2)
    if 'Brake' in df.columns:
        ax_brake.plot(df.index, df['Brake'], color='#FF0000', linewidth=1.5)
        ax_brake.fill_between(df.index, df['Brake'], color='#FF0000', alpha=0.2)
    plt.tight_layout()
    return fig

def plot_comparison_telemetry(data_dict):
    fig, (ax_speed, ax_throttle) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    colors = ['#00A19B', '#FF0000', '#15FF00', '#FFFFFF']
    for i, (name, df) in enumerate(data_dict.items()):
        color = colors[i % len(colors)]
        ax_speed.plot(df.index, df['Speed'], label=name, color=color, linewidth=2)
        if 'Throttle' in df.columns:
            ax_throttle.plot(df.index, df['Throttle'], color=color, alpha=0.3)
    ax_speed.set_ylabel("Speed (km/h)")
    ax_speed.legend()
    ax_throttle.set_ylabel("Throttle %")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig) 

# --- MAIN UI ---
st.title("Apex Intelligence: Command Center")

# 1. Sidebar Setup
available_data = get_all_sessions()
if available_data:
    display_names = [name.replace('telemetry_', '').replace('_', ' ').title() for name in available_data]
    name_map = dict(zip(display_names, available_data))
    
    selected_drivers = st.sidebar.multiselect(
        "Select Drivers (Pick 1 for Detail, 2 for Battle):", 
        display_names, 
        default=[display_names[0]] if display_names else []
    )
    
    # Load data
    all_selected_data = {name: load_telemetry(name_map[name]) for name in selected_drivers}

# 2. Tab Layout
tab1, tab2 = st.tabs([" Performance Overview", " 2026 Rules"])

with tab1:
    if not selected_drivers:
        st.info("👈 Please select drivers in the sidebar to begin analysis.")
    
    # CASE A: BATTLE MODE (2 Drivers)
    elif len(selected_drivers) == 2:
        d1, d2 = selected_drivers[0], selected_drivers[1]
        
        # 1. METRIC CARDS
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{d1}**")
            st.metric("Max Speed", f"{all_selected_data[d1]['Speed'].max():.1f} km/h")
            st.metric("Avg Speed", f"{all_selected_data[d1]['Speed'].mean():.1f} km/h")
            
        with col2:
            st.markdown(f"**{d2}**")
            st.metric("Max Speed", f"{all_selected_data[d2]['Speed'].max():.1f} km/h")
            st.metric("Avg Speed", f"{all_selected_data[d2]['Speed'].mean():.1f} km/h")

        st.divider()

        # 2. PERFORMANCE INSIGHT
        avg1 = all_selected_data[d1]['Speed'].mean()
        avg2 = all_selected_data[d2]['Speed'].mean()
        diff = abs(avg1 - avg2)
        faster = d1.split()[0] if avg1 > avg2 else d2.split()[0]
        
        st.success(f"🏎️ Race Engineer Insight: **{faster}** is faster by **{diff:.2f} km/h** on average.")
        
        # 3. DISPLAY GRAPHS
        st.subheader("Head-to-Head Telemetry")
        plot_comparison_telemetry(all_selected_data)
        
        # 4. SPEED DELTA
        st.subheader(f"Live Speed Delta: {d1.split()[0]} vs {d2.split()[0]}")
        
        s1 = all_selected_data[d1]['Speed'].values
        s2 = all_selected_data[d2]['Speed'].values
        min_len = min(len(s1), len(s2))
        delta = s1[:min_len] - s2[:min_len]
        
        fig_delta, ax_delta = plt.subplots(figsize=(12, 4))
        
        # Color the area: Green if Driver 1 is faster, Red if Driver 2 is faster
        ax_delta.fill_between(range(min_len), delta, 0, where=(delta >= 0), color='#15FF00', alpha=0.3, label=f"{d1.split()[0].upper()} Faster")
        ax_delta.fill_between(range(min_len), delta, 0, where=(delta < 0), color='#FF0000', alpha=0.3, label=f"{d2.split()[0].upper()} Faster")
        
        ax_delta.plot(delta, color='white', linewidth=0.8, alpha=0.7)
        ax_delta.axhline(0, color='white', linestyle='--', alpha=0.5)
        
        # Adding labels for better understanding
        ax_delta.set_ylabel("Speed Difference (km/h)", fontsize=10)
        ax_delta.set_xlabel("Track Position (Samples)", fontsize=10)
        ax_delta.legend(loc='upper right', fontsize=8)
        
        # Add "Zones" understanding
        st.pyplot(fig_delta)
        
        st.caption(f"💡 **How to read this:** When the graph is **Green**, {d1.split()[0].upper()} is gaining time. When it is **Red**, {d2.split()[0].upper()} is faster at that specific point on the track.")

    # CASE B: SINGLE OR MULTI DETAIL
    else:
        for driver in selected_drivers:
            df = all_selected_data[driver]
            st.subheader(f"Detailed Analysis: {driver}")
            
            # Adding Metric Cards back to single view too
            c1, c2, c3 = st.columns(3)
            c1.metric("Max Speed", f"{df['Speed'].max():.1f} km/h")
            c2.metric("Avg Speed", f"{df['Avg Speed'].mean() if 'Avg Speed' in df.columns else df['Speed'].mean():.1f} km/h")
            c3.metric("Samples", len(df))

            st.pyplot(plot_professional_telemetry(df, driver))
            st.divider()

with tab2:
    st.header("2026 Technical Assistant")
    if st.button("Initialize Librarian"):
        if "vector_db" not in st.session_state:
            with st.spinner("Reading Rulebook..."):
                from src.rule_processor import load_rules, create_chunks, get_vector_db
                raw_text = load_rules("knowledge_base/2026_regs.pdf")
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