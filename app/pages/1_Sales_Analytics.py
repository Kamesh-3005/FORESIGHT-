import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(page_title="FORESIGHT - Sales Analytics", page_icon="📈", layout="wide")

# --------------------------------------------------
# Load data
# --------------------------------------------------
sales_path = "data/processed/weekly_demand.csv"
sales_df = pd.read_csv(sales_path)

# --------------------------------------------------
# Prepare data
# --------------------------------------------------
sales_df["week_start"] = pd.to_datetime(sales_df["week_start"])

# --------------------------------------------------
# Page header
# --------------------------------------------------
st.title("Sales Analytics")
st.write("Historical demand analysis across products " "and categories.")

# --------------------------------------------------
# Category filter
# --------------------------------------------------
st.subheader("Historical Demand Trend")
categories = sorted(sales_df["category"].dropna().unique().tolist())
selected_category = st.selectbox("Select Category", ["All Categories"] + categories)

if selected_category == "All Categories": trend_df = sales_df.copy()
else: trend_df = sales_df[sales_df["category"] == selected_category].copy()
weekly_trend = (trend_df.groupby("week_start", as_index=False)["demand"].sum())
st.line_chart(weekly_trend.set_index("week_start")["demand"])

# --------------------------------------------------
# Category-wise demand
# --------------------------------------------------
st.subheader("Demand by Category")
category_demand = (sales_df.groupby("category", as_index=False)["demand"].sum().sort_values("demand", ascending=False))
st.bar_chart(category_demand.set_index("category")["demand"])

# --------------------------------------------------
# Top 10 Products by Demand
# --------------------------------------------------
st.subheader("Top 10 Products by Historical Demand")
top_products = (sales_df.groupby(["sku_id", "product_name"],as_index=False)["demand"].sum().sort_values("demand", ascending=False).head(10))
top_products["product_label"] = (top_products["sku_id"]+ " - " + top_products["product_name"])
st.bar_chart(top_products.set_index("product_label")["demand"], horizontal=True)

# --------------------------------------------------
# Yearly Demand
# --------------------------------------------------
st.subheader("Yearly Demand")
yearly_demand = (sales_df.groupby("year", as_index=False)["demand"].sum().sort_values("year"))
st.bar_chart(yearly_demand.set_index("year")["demand"])