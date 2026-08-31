import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config( page_title="FORESIGHT - Forecast", page_icon="🔮", layout="wide")

# --------------------------------------------------
# Load forecast data
# --------------------------------------------------
forecast_path = "data/processed/combined_forecast.csv"
forecast_df = pd.read_csv(forecast_path)

# --------------------------------------------------
# Prepare data
# --------------------------------------------------
forecast_df["week_start"] = pd.to_datetime(forecast_df["week_start"])

# --------------------------------------------------
# Page header
# --------------------------------------------------
st.title("Forecast Dashboard")
st.write("8-week demand forecast across the complete " "100-SKU portfolio.")

# --------------------------------------------------
# Forecast KPIs
# --------------------------------------------------
total_skus = forecast_df["sku_id"].nunique()
forecast_weeks = forecast_df["week_start"].nunique()
total_forecast = forecast_df["forecast"].sum()
primary_count = (forecast_df["forecast_method"] == "primary_ml").sum()
fallback_count = (forecast_df["forecast_method"] == "category_fallback").sum()

# --------------------------------------------------
# KPI display
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Forecast SKUs", f"{total_skus:,}")
with col2: st.metric("Forecast Weeks", f"{forecast_weeks:,}")
with col3: st.metric("Total Forecast", f"{total_forecast:,.0f}")
with col4: st.metric( "Primary ML Points", f"{primary_count:,}")
with col5: st.metric("Fallback Points", f"{fallback_count:,}")

# --------------------------------------------------
# 8-Week Forecast Trend
# --------------------------------------------------
st.subheader("8-Week Demand Forecast")
weekly_forecast = (forecast_df.groupby("week_start", as_index=False)["forecast"].sum().sort_values("week_start"))
st.line_chart(weekly_forecast.set_index("week_start")["forecast"])

# --------------------------------------------------
# SKU-level Forecast
# --------------------------------------------------
st.subheader("SKU-Level Forecast")
sku_list = sorted(forecast_df["sku_id"].unique().tolist())
selected_sku = st.selectbox("Select SKU", sku_list)
sku_forecast = (forecast_df[forecast_df["sku_id"] == selected_sku].sort_values("week_start"))
st.line_chart(sku_forecast.set_index("week_start")["forecast"])

# --------------------------------------------------
# Forecast Method Summary
# --------------------------------------------------
st.subheader("Forecast Method Summary")
method_summary = (forecast_df.groupby("forecast_method")["sku_id"].nunique().reset_index(name="sku_count"))
st.bar_chart(method_summary.set_index("forecast_method")["sku_count"])

# --------------------------------------------------
# Forecast Confidence Summary
# --------------------------------------------------
st.subheader("Forecast Confidence")
confidence_summary = (forecast_df.groupby("forecast_confidence")["sku_id"].nunique().reset_index(name="sku_count"))
st.bar_chart(confidence_summary.set_index("forecast_confidence")["sku_count"])