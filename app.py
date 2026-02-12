import streamlit as st
import pandas as pd
from src.kpi_engine import calculate_kpis
from src.decision_engine import recommend_option

st.title("DPP-Enabled Reverse Logistics Dashboard")

# Load data
df = pd.read_csv("data/washing_machine_returns.csv")

# Calculate KPIs
df = calculate_kpis(df)

# Apply decision engine
df["recommended_option"] = df.apply(recommend_option, axis=1)

st.subheader("Processed Returns")
st.dataframe(df)

st.subheader("Portfolio KPIs")
st.metric("Average Reman Net Value (€)", round(df["net_value_reman"].mean(), 2))
st.metric("Total Avoided CO2 (kg)", round(df["avoided_co2"].sum(), 2))
st.metric("Most Recommended Option", df["recommended_option"].mode()[0])

