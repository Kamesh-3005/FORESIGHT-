import pandas as pd

#laod project datasets
forecast = pd.read_csv("data/processed/combined_forecast.csv")
inventory = pd.read_csv("data/processed/inventory_daily.csv")
sku_master = pd.read_csv("data/processed/sku_master.csv")

print("forecast rows: ", len(forecast))
print("inventory rows: ", len(inventory))
print("SKU master rows: ", len(sku_master))

#convert date columns
forecast ["week_start"] = pd.to_datetime(forecast["week_start"])
inventory ["date"] = pd. to_datetime(inventory["date"])
sku_master ["launch_date"] = pd.to_datetime(sku_master["launch_date"])

print("Forecast Date Range: ", forecast ["week_start"].min(), "to", forecast ["week_start"].max())
print("Inventory Range: ", inventory ["date"].min(), "to", inventory ["date"].max())

# Latest inventory snapshot
latest_inventory_date = inventory["date"].max()
latest_inventory = (inventory[inventory["date"] == latest_inventory_date].groupby("sku_id")["closing_stock"].sum().reset_index())
latest_inventory = latest_inventory.rename(columns={"closing_stock": "latest_inventory"})

print("Latest inventory date:",latest_inventory_date.date())
print("SKUs with inventory:",latest_inventory["sku_id"].nunique())
print(latest_inventory.head())

# Keep inventory only for forecasted SKUs
forecast_skus = forecast["sku_id"].unique()
latest_inventory = latest_inventory[latest_inventory["sku_id"].isin(forecast_skus)].copy()

print("Forecasted SKUs:",len(forecast_skus))
print("Inventory SKUs after filter:",latest_inventory["sku_id"].nunique())

# Total 8-week forecast per SKU
forecast_total = (forecast.groupby("sku_id").agg(forecast_8_week=("forecast", "sum"),forecast_method=("forecast_method", "first"),forecast_confidence=("forecast_confidence", "first")).reset_index())
forecast_total = forecast_total.rename(columns={"forecast": "forecast_8_week"})

print("Forecast total rows:",len(forecast_total))
print(forecast_total.head())

# Merge inventory and forecast
risk_df = forecast_total.merge(latest_inventory,on="sku_id",how="left")

print("Risk dataset rows:",len(risk_df))
print("Missing inventory:",risk_df["latest_inventory"].isna().sum())
print(risk_df.head())

# Calculate inventory coverage
risk_df["coverage_ratio"] = (risk_df["latest_inventory"]/ risk_df["forecast_8_week"])

print("\nCoverage summary:")
print(risk_df["coverage_ratio"].describe())
print("\nFirst 5 coverage values:")
print(risk_df[["sku_id","latest_inventory","forecast_8_week","coverage_ratio"]].head())

# Classify stockout and overstock risk
risk_df["stockout_risk"] = (risk_df["coverage_ratio"] < 20).map({True: "High",False: "Low"})
risk_df["overstock_risk"] = (risk_df["coverage_ratio"] > 40).map({True: "High",False: "Low"})

print("\nStockout risk:")
print(risk_df["stockout_risk"].value_counts())
print("\nOverstock risk:")
print(risk_df["overstock_risk"].value_counts())

# Assign recommended action
def assign_action(row):
    if (row["stockout_risk"] == "High" and row["overstock_risk"] == "Low"): return "Reorder now"
    elif (row["stockout_risk"] == "Low" and row["overstock_risk"] == "High"): return "Markdown / clear"
    elif (row["stockout_risk"] == "High" and row["overstock_risk"] == "High"): return "Watch / volatile"
    else: return "Healthy"
risk_df["recommended_action"] = risk_df.apply(assign_action,axis=1)

print("\nRecommended actions:")
print(risk_df["recommended_action"].value_counts())

# Merge SKU master information
risk_df = risk_df.merge (sku_master[["sku_id","product_name","category","unit_cost","list_price"]], on="sku_id", how="left")

print("\nMissing unit cost:")
print(risk_df["unit_cost"].isna().sum())

# ============================================================
# Calculate value at stake
# ============================================================
risk_df["units_at_risk"] = 0.0

# Overstock exposure:
# inventory held above the 8-week forecast requirement
overstock_mask = (risk_df["recommended_action"] == "Markdown / clear")
risk_df.loc[overstock_mask, "units_at_risk"] = (risk_df.loc[overstock_mask, "latest_inventory"] - risk_df.loc[overstock_mask, "forecast_8_week"])

# Replenishment-risk exposure:
# We do NOT claim a physical stockout because the dataset
# does not contain lead-time, reorder-point, or on-order data.
# Instead, we report the current inventory value exposed
# to the low-coverage replenishment-risk proxy.
replenishment_mask = (risk_df["recommended_action"] == "Reorder now")
risk_df.loc[replenishment_mask, "units_at_risk"] = (risk_df.loc[replenishment_mask, "latest_inventory"])
risk_df["rupee_value_at_stake"] = (risk_df["units_at_risk"] * risk_df["unit_cost"])

print("\nValue at stake by action:")
print(risk_df.groupby("recommended_action")["rupee_value_at_stake"].sum())

print("\nTotal rupee value at stake:")
print(risk_df["rupee_value_at_stake"].sum())

# ============================================================
# Save final risk scoring output
# ============================================================
output_columns = ["sku_id","product_name","category","latest_inventory","forecast_8_week","forecast_method","forecast_confidence","coverage_ratio","stockout_risk","overstock_risk","recommended_action","unit_cost","units_at_risk","rupee_value_at_stake"]
risk_df[output_columns].to_csv("data/processed/risk_scoring.csv", index=False)

print("\nRisk scoring saved.")
print("Rows saved:", len(risk_df))