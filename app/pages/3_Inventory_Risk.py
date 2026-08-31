import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(page_title="FORESIGHT - Inventory & Risk", page_icon="📦", layout="wide")

# --------------------------------------------------
# Load risk data
# --------------------------------------------------
risk_path = "data/processed/risk_scoring.csv"
risk_df = pd.read_csv(risk_path)

# --------------------------------------------------
# Page header
# --------------------------------------------------
st.title("Inventory & Risk")
st.write("Inventory coverage, replenishment risk, " "overstock exposure, and recommended actions.")

# --------------------------------------------------
# Filters
# --------------------------------------------------
filter_col1, filter_col2 = st.columns(2)
with filter_col1: category_options = sorted(risk_df["category"].dropna().unique().tolist())
selected_category = st.selectbox("Category", ["All Categories"] + category_options)
with filter_col2: action_options = sorted(risk_df["recommended_action"].dropna().unique().tolist())
selected_action = st.selectbox("Recommended Action",["All Actions"] + action_options) 

#----------------------------------------------------
#filtered dataset
#----------------------------------------------------
filtered_risk_df = risk_df.copy()
if selected_category != "All Categories": filtered_risk_df = filtered_risk_df[filtered_risk_df["category"] == selected_category]
if selected_action != "All Actions": filtered_risk_df = filtered_risk_df[filtered_risk_df["recommended_action"] == selected_action]

# --------------------------------------------------
# Risk KPIs
# --------------------------------------------------
total_skus = risk_df["sku_id"].nunique()
reorder_count = (risk_df["recommended_action"] == "Reorder now").sum()
markdown_count = (risk_df["recommended_action"] == "Markdown / clear").sum()
healthy_count = (risk_df["recommended_action"] == "Healthy").sum()
total_value_at_stake = (risk_df["rupee_value_at_stake"].sum())

# --------------------------------------------------
# KPI display
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Total SKUs",f"{total_skus:,}")
with col2: st.metric("Reorder Now", f"{reorder_count:,}")
with col3: st.metric("Markdown / Clear", f"{markdown_count:,}")
with col4: st.metric("Healthy", f"{healthy_count:,}")
with col5: st.metric("Value at Stake", f"₹{total_value_at_stake / 1_000_000_000:.2f} B")

# --------------------------------------------------
# Risk Summary
# --------------------------------------------------
st.subheader("Inventory Risk Summary")
risk_col1, risk_col2 = st.columns(2)

# --------------------------------------------------
# Stockout risk
# --------------------------------------------------
with risk_col1: stockout_summary = (filtered_risk_df["stockout_risk"].value_counts().rename_axis("risk_level").reset_index(name="sku_count"))
st.write("Stockout Risk")
st.bar_chart(stockout_summary.set_index("risk_level")["sku_count"], horizontal=True)

# --------------------------------------------------
# Overstock risk
# --------------------------------------------------
with risk_col2: overstock_summary = (filtered_risk_df["overstock_risk"].value_counts().rename_axis("risk_level").reset_index(name="sku_count"))
st.write("Overstock Risk")
st.bar_chart(overstock_summary.set_index("risk_level")["sku_count"], horizontal=True)

# --------------------------------------------------
# Inventory Coverage
# --------------------------------------------------
st.subheader("Inventory Coverage")
coverage_summary = (filtered_risk_df[["sku_id","product_name","category","latest_inventory","forecast_8_week","coverage_ratio","recommended_action"]].sort_values("coverage_ratio"))
st.dataframe(coverage_summary, use_container_width=True, hide_index=True, 
             column_config={
                "coverage_ratio": st.column_config.NumberColumn("Coverage Ratio", format="%.2fx"), 
                "latest_inventory": st.column_config.NumberColumn("Current Inventory", format="%d"), 
                "forecast_8_week": st.column_config.NumberColumn("8-Week Forecast", format="%.0f")})

# --------------------------------------------------
# Recommended Actions
# --------------------------------------------------
st.subheader("Recommended Actions")
action_summary = (filtered_risk_df["recommended_action"].value_counts().rename_axis("recommended_action").reset_index(name="sku_count"))
st.bar_chart(action_summary.set_index("recommended_action")["sku_count"], horizontal=True)

# --------------------------------------------------
# Markdown / Clear — Excess Inventory
# --------------------------------------------------
st.subheader("Markdown / Clear — Excess Inventory")
markdown_df = (filtered_risk_df[filtered_risk_df["recommended_action"] == "Markdown / clear"][["sku_id", "product_name", "category", "latest_inventory", "forecast_8_week", "coverage_ratio", "unit_cost","units_at_risk", "rupee_value_at_stake"]].sort_values("rupee_value_at_stake", ascending=False))
st.dataframe(markdown_df, use_container_width=True, hide_index=True, column_config={
        "latest_inventory": st.column_config.NumberColumn("Current Inventory", format="%d"), 
        "forecast_8_week": st.column_config.NumberColumn("8-Week Forecast", format="%.0f"),
        "coverage_ratio": st.column_config.NumberColumn("Coverage Ratio",format="%.2fx"),
        "unit_cost": st.column_config.NumberColumn("Unit Cost", format="₹%.0f"),
        "units_at_risk": st.column_config.NumberColumn("Units at Risk",format="%.0f"),
        "rupee_value_at_stake": st.column_config.NumberColumn("Value at Stake", format="₹%.0f")})