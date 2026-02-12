import streamlit as st
import pandas as pd
import plotly.express as px

from src.kpi_engine import calculate_kpis
from src.decision_engine import recommend_option_with_explanation

st.set_page_config(page_title="DPP RL Dashboard", layout="wide")
st.title("DPP-Enabled Reverse Logistics Dashboard")

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")
grades = st.sidebar.multiselect("Condition grades", ["A", "B", "C", "D"], default=["A", "B", "C", "D"])

# -----------------------------
# Load raw data
# -----------------------------
df_raw = pd.read_csv("data/washing_machine_returns.csv")
df_raw = df_raw[df_raw["condition_grade"].isin(grades)]

# -----------------------------
# Scenario function
# -----------------------------
def apply_scenario(df: pd.DataFrame, without: bool) -> pd.DataFrame:
    df = df.copy()
    if without:
        df["info_completeness"] = (df["info_completeness"] * 0.55).clip(0, 1)
        df["disassembly_time_min"] = pd.NA
        df["repairability_score"] = pd.NA
        df["co2_mfg_kg"] = pd.NA
    return df

# -----------------------------
# Process BOTH scenarios (for impact comparison)
# -----------------------------
df_with = calculate_kpis(apply_scenario(df_raw, without=False))
df_without = calculate_kpis(apply_scenario(df_raw, without=True))

# Add decisions + explanations
def add_decisions(df):
    out = df.copy()
    recs = out.apply(recommend_option_with_explanation, axis=1, result_type="expand")
    out["recommended_option"] = recs[0]
    out["decision_score"] = recs[1]
    out["decision_reasons"] = recs[2]
    out["decision_confidence_%"] = (out["info_completeness"] * 100).round(0).astype(int)
    return out

df_with = add_decisions(df_with)
df_without = add_decisions(df_without)

# -----------------------------
# DPP Impact Summary (Δ)
# -----------------------------
impact_net = df_with["net_value_reman"].mean() - df_without["net_value_reman"].mean()
impact_co2 = df_with["avoided_co2"].sum() - df_without["avoided_co2"].sum()
impact_conf = df_with["decision_confidence_%"].mean() - df_without["decision_confidence_%"].mean()

st.subheader("DPP Impact (WITH DPP vs WITHOUT DPP)")
c1, c2, c3 = st.columns(3)
c1.metric("Δ Avg Net Value (€/return)", round(impact_net, 2))
c2.metric("Δ Total Avoided CO₂ (kg)", round(impact_co2, 2))
c3.metric("Δ Avg Confidence (%)", int(round(impact_conf, 0)))

# -----------------------------
# Plotly Charts (Professional look)
# -----------------------------
st.subheader("Charts")

# Option share comparison
opt_with = df_with["recommended_option"].value_counts().reset_index()
opt_with.columns = ["option", "count"]
opt_with["scenario"] = "WITH DPP"

opt_without = df_without["recommended_option"].value_counts().reset_index()
opt_without.columns = ["option", "count"]
opt_without["scenario"] = "WITHOUT DPP"

opt_all = pd.concat([opt_with, opt_without], ignore_index=True)

fig1 = px.bar(opt_all, x="option", y="count", color="scenario", barmode="group",
              title="Recommended EoL Options (WITH vs WITHOUT DPP)")
st.plotly_chart(fig1, use_container_width=True)

# Net value distribution comparison
dist = pd.concat([
    df_with.assign(scenario="WITH DPP")[["net_value_reman", "scenario"]],
    df_without.assign(scenario="WITHOUT DPP")[["net_value_reman", "scenario"]],
], ignore_index=True)

fig2 = px.histogram(dist, x="net_value_reman", color="scenario", nbins=12,
                    title="Net Value Distribution (Reman) — WITH vs WITHOUT DPP")
st.plotly_chart(fig2, use_container_width=True)

# Net value vs repairability (WITH DPP only, because WITHOUT has missing values)
fig3 = px.scatter(df_with, x="repairability_score", y="net_value_reman",
                  hover_data=["product_id", "condition_grade", "decision_reasons"],
                  title="Net Value vs Repairability (WITH DPP)")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Choose which scenario table to view
# -----------------------------
st.subheader("Processed Returns Table")
scenario_view = st.radio("View table for:", ["WITH DPP", "WITHOUT DPP"], horizontal=True)

df_view = df_with if scenario_view == "WITH DPP" else df_without
st.dataframe(
    df_view[[
        "product_id", "condition_grade", "info_completeness", "decision_confidence_%",
        "disassembly_time_min", "repairability_score", "co2_mfg_kg",
        "disassembly_cost", "processing_cost", "net_value_reman", "avoided_co2",
        "recommended_option", "decision_score", "decision_reasons"
    ]],
    use_container_width=True
)

# -----------------------------
# Export for Power BI
# -----------------------------
st.subheader("Export for Power BI")
csv_bytes = df_view.to_csv(index=False).encode("utf-8")
st.download_button(
    f"Download CSV ({scenario_view})",
    data=csv_bytes,
    file_name=f"processed_returns_{scenario_view.replace(' ', '_').lower()}.csv",
    mime="text/csv"
)
