import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(page_title="FORESIGHT - Risk Dashboard", page_icon="⚠️", layout="wide")

# --------------------------------------------------
# Load risk data
# --------------------------------------------------
risk_path = "data/processed/risk_scoring.csv"
risk_df = pd.read_csv(risk_path)

# --------------------------------------------------
# Page header
# --------------------------------------------------
st.title("Risk Dashboard")
st.write("Portfolio-level risk prioritization based on " "inventory coverage, forecast demand, and recommended actions.")

# --------------------------------------------------
# Risk KPIs
# --------------------------------------------------
total_skus = risk_df["sku_id"].nunique()
high_stockout = (risk_df["stockout_risk"] == "High").sum()
high_overstock = (risk_df["overstock_risk"] == "High").sum()
reorder_now = (risk_df["recommended_action"] == "Reorder now").sum()
markdown_clear = (risk_df["recommended_action"] == "Markdown / clear").sum()

# --------------------------------------------------
# KPI display
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Total SKUs",f"{total_skus:,}")
with col2: st.metric("High Stockout Risk", f"{high_stockout:,}")
with col3: st.metric("High Overstock Risk", f"{high_overstock:,}")
with col4: st.metric("Reorder Now", f"{reorder_now:,}")
with col5: st.metric("Markdown / Clear", f"{markdown_clear:,}")

# --------------------------------------------------
# Risk Priority Table
# --------------------------------------------------
st.subheader("Risk Priority — Lowest Coverage First")
risk_priority = (risk_df[["sku_id", "product_name", "category", "latest_inventory", "forecast_8_week", "coverage_ratio", "stockout_risk", "overstock_risk", "recommended_action", "forecast_confidence"]].sort_values("coverage_ratio"))
st.dataframe(risk_priority, use_container_width=True, hide_index=True,
    column_config={
        "latest_inventory": st.column_config.NumberColumn("Current Inventory", format="%d"),
        "forecast_8_week": st.column_config.NumberColumn("8-Week Forecast", format="%.0f"),
        "coverage_ratio": st.column_config.NumberColumn("Coverage Ratio", format="%.2fx")})

# --------------------------------------------------
# Risk Action Distribution
# --------------------------------------------------
st.subheader("Risk Action Distribution")
action_summary = (risk_df["recommended_action"]
    .value_counts()
    .rename_axis("recommended_action")
    .reset_index(name="sku_count"))
st.bar_chart(action_summary.set_index("recommended_action")["sku_count"], horizontal=True)

# --------------------------------------------------
# Risk Action Filter
# --------------------------------------------------
st.subheader("Filter Risk Priorities")
selected_risk_action = st.selectbox("Recommended Action", ["All Actions"] + sorted(risk_df["recommended_action"].dropna().unique().tolist()))
filtered_risk = risk_df.copy()
if selected_risk_action != "All Actions": filtered_risk = filtered_risk[filtered_risk["recommended_action"] == selected_risk_action]
filtered_priority = (filtered_risk[["sku_id", "product_name", "category", "latest_inventory", "forecast_8_week", "coverage_ratio", "stockout_risk", "overstock_risk", "recommended_action", "forecast_confidence"]].sort_values("coverage_ratio"))
st.dataframe(filtered_priority, use_container_width=True, hide_index=True,
    column_config={
        "latest_inventory": st.column_config.NumberColumn("Current Inventory", format="%d"),
        "forecast_8_week": st.column_config.NumberColumn("8-Week Forecast", format="%.0f"),
        "coverage_ratio": st.column_config.NumberColumn("Coverage Ratio", format="%.2fx")})