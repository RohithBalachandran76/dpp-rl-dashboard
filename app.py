import streamlit as st
import pandas as pd

from src.kpi_engine import calculate_kpis
from src.decision_engine import recommend_option

st.set_page_config(layout="wide")
st.title("DPP-Enabled Reverse Logistics Dashboard")

# -------------------------
# Sidebar Controls
# -------------------------
st.sidebar.header("Scenario Settings")

scenario = st.sidebar.radio(
    "Select Scenario",
    ["WITH DPP (High Information)", "WITHOUT DPP (Low Information)"]
)

grades = st.sidebar.multiselect(
    "Filter Condition Grades",
    ["A", "B", "C", "D"],
    default=["A", "B", "C", "D"]
)

# -------------------------
# Load Data
# -------------------------
df = pd.read_csv("data/washing_machine_returns.csv")

df = df[df["condition_grade"].isin(grades)]

# -------------------------
# Scenario Simulation
# -------------------------
if "WITHOUT" in scenario:
    df["info_completeness"] = df["info_completeness"] * 0.5
    df["disassembly_time_min"] = pd.NA
    df["repairability_score"] = pd.NA
    df["co2_mfg_kg"] = pd.NA

# -------------------------
# KPI & Decision Processing
# -------------------------
df = calculate_kpis(df)

df["recommended_option"] = df.apply(recommend_option, axis=1)

df["decision_confidence_%"] = (df["info_completeness"] * 100).round(0)

# -------------------------
# KPI Overview
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Avg Net Value (€)", round(df["net_value_reman"].mean(), 2))
col2.metric("Total Avoided CO₂ (kg)", round(df["avoided_co2"].sum(), 2))
col3.metric("Avg Decision Confidence (%)", int(df["decision_confidence_%"].mean()))

# -------------------------
# Table Output
# -------------------------
st.subheader("Processed Returns")
st.dataframe(df, use_container_width=True)

# -------------------------
# Export for Power BI
# -------------------------
st.subheader("Export Data")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Processed CSV",
    data=csv,
    file_name="processed_returns.csv",
    mime="text/csv"
)
