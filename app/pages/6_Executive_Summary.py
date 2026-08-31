import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(page_title="FORESIGHT - Executive Summary", page_icon="📊", layout="wide")

# --------------------------------------------------
# Load data
# --------------------------------------------------
weekly_path = "data/processed/weekly_demand.csv"
forecast_path = "data/processed/combined_forecast.csv"
risk_path = "data/processed/risk_scoring.csv"
weekly_df = pd.read_csv(weekly_path)
forecast_df = pd.read_csv(forecast_path)
risk_df = pd.read_csv(risk_path)

# --------------------------------------------------
# Prepare dates
# --------------------------------------------------
weekly_df["week_start"] = pd.to_datetime(weekly_df["week_start"])
forecast_df["week_start"] = pd.to_datetime(forecast_df["week_start"])

# --------------------------------------------------
# Page header
# --------------------------------------------------
st.title("Executive Summary")
st.write("Management overview of demand, forecasting, " "inventory risk, and recommended actions.")

# --------------------------------------------------
# Executive KPIs
# --------------------------------------------------
total_skus = risk_df["sku_id"].nunique()
historical_demand = weekly_df["demand"].sum()
forecast_demand = forecast_df["forecast"].sum()
reorder_count = (risk_df["recommended_action"] == "Reorder now").sum()
markdown_count = (risk_df["recommended_action"] == "Markdown / clear").sum()
value_at_stake = risk_df["rupee_value_at_stake"].sum()

# --------------------------------------------------
# KPI display
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Portfolio SKUs", f"{total_skus:,}")
with col2: st.metric("Historical Demand", f"{historical_demand / 1_000_000:.2f} M")
with col3: st.metric("8-Week Forecast", f"{forecast_demand / 1_000:.1f} K")
with col4: st.metric("Reorder Now", f"{reorder_count:,}")
with col5: st.metric("Value at Stake", f"₹{value_at_stake / 1_000_000_000:.2f} B")

# --------------------------------------------------
# Executive Action Summary
# --------------------------------------------------
st.subheader("Recommended Actions")
action_summary = (risk_df["recommended_action"].value_counts().rename_axis("recommended_action").reset_index(name="sku_count"))
st.bar_chart(action_summary.set_index("recommended_action")["sku_count"], horizontal=True)

# --------------------------------------------------
# Financial Exposure Summary
# --------------------------------------------------
st.subheader("Financial Exposure by Recommended Action")
value_summary = (risk_df.groupby("recommended_action", as_index=False)["rupee_value_at_stake"].sum().sort_values("rupee_value_at_stake", ascending=False))
st.bar_chart(value_summary.set_index("recommended_action")["rupee_value_at_stake"], horizontal=True)