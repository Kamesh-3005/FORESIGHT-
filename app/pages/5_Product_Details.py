import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(page_title="FORESIGHT - Product Details", page_icon="🔎", layout="wide")

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
st.title("Product Details")
st.write("Detailed historical demand, forecast, inventory, " "and risk information for an individual SKU.")

# --------------------------------------------------
# SKU selector
# --------------------------------------------------
sku_list = sorted(risk_df["sku_id"].unique().tolist())
selected_sku = st.selectbox("Select SKU", sku_list)

# --------------------------------------------------
# Selected product information
# --------------------------------------------------
product_info = risk_df[risk_df["sku_id"] == selected_sku].iloc[0]

# --------------------------------------------------
# Product information
# --------------------------------------------------
st.subheader("Product Information")
info_col1, info_col2, info_col3 = st.columns(3)
with info_col1: st.write(f"**Product:** {product_info['product_name']}")
with info_col2: st.write(f"**Category:** {product_info['category']}")
with info_col3: st.write(f"**SKU:** {product_info['sku_id']}")

# --------------------------------------------------
# Product KPIs
# --------------------------------------------------
current_inventory = product_info["latest_inventory"]
forecast_8_week = product_info["forecast_8_week"]
coverage_ratio = product_info["coverage_ratio"]
recommended_action = product_info["recommended_action"]
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Current Inventory", f"{current_inventory:,.0f}")
with col2: st.metric("8-Week Forecast", f"{forecast_8_week:,.0f}")
with col3: st.metric("Coverage Ratio", f"{coverage_ratio:.2f}x")
with col4: st.metric("Recommended Action", recommended_action)

# --------------------------------------------------
# Historical Demand
# --------------------------------------------------
st.subheader("Historical Demand")
sku_history = (weekly_df[weekly_df["sku_id"] == selected_sku].groupby("week_start", as_index=False)["demand"].sum().sort_values("week_start"))
st.line_chart(sku_history.set_index("week_start")["demand"])

# --------------------------------------------------
# 8-Week Forecast
# --------------------------------------------------
st.subheader("8-Week Forecast")
sku_forecast = (forecast_df[forecast_df["sku_id"] == selected_sku].sort_values("week_start"))
st.line_chart(sku_forecast.set_index("week_start")["forecast"])

# --------------------------------------------------
# Risk & Forecast Details
# --------------------------------------------------
st.subheader("Risk & Forecast Details")
detail_col1, detail_col2 = st.columns(2)
with detail_col1:
    st.write("### Risk Assessment")
    st.write(f"**Stockout Risk:** " f"{product_info['stockout_risk']}")
    st.write(f"**Overstock Risk:** " f"{product_info['overstock_risk']}")
    st.write(f"**Recommended Action:** " f"{product_info['recommended_action']}")
with detail_col2:
    st.write("### Forecast Information")
    st.write(f"**Forecast Method:** " f"{product_info['forecast_method']}")
    st.write(f"**Forecast Confidence:** " f"{product_info['forecast_confidence']}")
    st.write(f"**8-Week Forecast:** " f"{product_info['forecast_8_week']:,.0f}")

# --------------------------------------------------
# Financial Exposure
# --------------------------------------------------
st.subheader("Financial Exposure")
unit_cost = product_info["unit_cost"]
units_at_risk = product_info["units_at_risk"]
value_at_stake = product_info["rupee_value_at_stake"]
finance_col1, finance_col2, finance_col3 = st.columns(3)
with finance_col1: st.metric("Unit Cost", f"₹{unit_cost:,.0f}")
with finance_col2: st.metric("Units at Risk", f"{units_at_risk:,.0f}")
with finance_col3: st.metric("Value at Stake", f"₹{value_at_stake:,.0f}")

