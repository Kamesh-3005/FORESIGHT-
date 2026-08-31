import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(page_title="FORESIGHT", page_icon="🔭", layout="wide")

# --------------------------------------------------
# Load project data
# --------------------------------------------------
risk_path = "data/processed/risk_scoring.csv"
forecast_path = "data/processed/combined_forecast.csv"
risk_df = pd.read_csv(risk_path)
forecast_df = pd.read_csv(forecast_path)
sales_path = "data/processed/weekly_demand.csv"
sales_df = pd.read_csv(sales_path)

# --------------------------------------------------
# Home page
# --------------------------------------------------
st.title("FORESIGHT")
st.subheader("Demand & Inventory Intelligence")
st.write("Planning dashboard for demand forecasting, " "inventory risk, and operational decision-making.")

# --------------------------------------------------
# Historical Demand Trend
# --------------------------------------------------
st.subheader("Historical Demand Trend")
sales_df["week_start"] = pd.to_datetime(sales_df["week_start"])
weekly_sales = (sales_df.groupby("week_start", as_index=False)["demand"].sum())
st.line_chart(weekly_sales.set_index("week_start")["demand"])

# --------------------------------------------------
# KPI calculations
# --------------------------------------------------
total_skus = risk_df["sku_id"].nunique()
forecast_points = len(forecast_df)
reorder_count = (risk_df["recommended_action"] == "Reorder now").sum()
markdown_count = (risk_df["recommended_action"] == "Markdown / clear").sum()
total_value_at_stake = risk_df["rupee_value_at_stake"].sum()
healthy_count = (risk_df["recommended_action"] == "Healthy").sum()

# --------------------------------------------------
# KPI display
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Total SKUs", f"{total_skus:,}")
with col2: st.metric("Forecast Points", f"{forecast_points:,}")
with col3: st.metric("Reorder Now", f"{reorder_count:,}")
with col4: st.metric("Markdown / Clear", f"{markdown_count:,}")
with col5: st.metric("Value at Stake", f"₹{total_value_at_stake / 1_000_000_000:.2f} B")

# --------------------------------------------------
# Action Summary
# --------------------------------------------------
st.subheader("Inventory Action Summary")
action_col1, action_col2, action_col3 = st.columns(3)
with action_col1: st.metric("Healthy", f"{healthy_count:,}")
with action_col2: st.metric("Reorder Now", f"{reorder_count:,}")
with action_col3: st.metric("Markdown / Clear", f"{markdown_count:,}")
st.success("FORESIGHT dashboard is running successfully.")