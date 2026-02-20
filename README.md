# 🏎️ Apex Intelligence: 2026 F1 Command Center

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://apexintelligence.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![F1](https://img.shields.io/badge/Formula--1-2026--Ready-E10600?logo=formula1&logoColor=white)

**Apex Intelligence** is a high-fidelity Formula 1 analytics platform designed to bridge the gap between current telemetry and the upcoming **2026 Technical Regulations**. Built for engineers and strategy enthusiasts, it combines real-world data with AI-driven regulatory insights.

---

## 🚀 Key Features

### 📊 Performance Overview (Telemetry Suite)
* **Performance Signatures:** Detailed Speed, Throttle, and Brake telemetry traces for the Spanish Grand Prix.
* **Track Dominance Map:** A spatial visualization showing exactly where one driver is faster than another on the circuit.
* **Battle Mode:** A side-by-side comparison engine that calculates live speed deltas and sector-by-sector performance.

### 🔋 2026 Energy Simulation
* **MGU-K Harvesting Model:** A custom simulation of the 2026 power unit regs (50/50 power split).
* **SoC Tracking:** Visualizes State of Charge (SoC) drain and recovery based on real throttle/brake input data.

### 🤖 2026 Rules Librarian (RAG AI)
* **AI Race Engineer:** A RAG-powered assistant (Retrieval-Augmented Generation) trained on the 2026 FIA Technical Regulations.
* **Knowledge Base:** Processes PDF/Text documentation to provide instant answers on MGU-K limits, aero changes, and fuel flow regs.
* **Lead Engineer:** Directed by **Shivcharan**, providing professional engineering briefings.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **Telemetry Data** | [FastF1 API](https://github.com/theOehrly/Fast-F1) & SQLite |
| **Data Science** | Pandas, NumPy, Matplotlib |
| **AI Model** | Llama 3.1 (via [Groq](https://groq.com/)) |
| **Vector Database** | FAISS (Facebook AI Similarity Search) |
| **Embeddings** | HuggingFace (Sentence-Transformers) |

---

## 📂 Project Structure

```text
├── app.py                # Main Streamlit application & UI logic
├── data/
│   └── f1_data.db        # SQLite database containing session telemetry
├── knowledge_base/       # Source PDFs/txt for the AI Librarian
├── src/
│   └── rule_processor.py # AI RAG logic and Vector DB management
├── requirements.txt      # Project dependencies
└── .github/workflows/    # Automation for data updates