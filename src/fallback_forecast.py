import pandas as pd

# ============================================================
# Load datasets
# ============================================================
weekly = pd.read_csv("data/processed/weekly_demand.csv")
forecast = pd.read_csv("data/processed/final_forecast.csv")
sku_master = pd.read_csv("data/processed/sku_master.csv")

# ============================================================
# Identify established and fallback SKUs
# ============================================================
established_skus = set(forecast["sku_id"].unique())
all_skus = set(sku_master["sku_id"].unique())
fallback_skus = sorted(all_skus - established_skus)

print("Established SKUs:", len(established_skus))
print("Fallback SKUs:", len(fallback_skus))

# ============================================================
# Prepare historical weekly demand
# ============================================================
weekly["week_start"] = pd.to_datetime(weekly["week_start"])
weekly_fallback = weekly[weekly["sku_id"].isin(fallback_skus)].copy()

# ============================================================
# Calculate SKU-level historical averages
# ============================================================
sku_history = (weekly_fallback.groupby("sku_id").agg(weeks=("week_start", "nunique"),total_demand=("demand", "sum")).reset_index())
sku_history["avg_weekly_demand"] = (sku_history["total_demand"]/ sku_history["weeks"])

# ============================================================
# Identify history groups
# ============================================================
sku_history["history_group"] = (sku_history["weeks"].apply(lambda x:"sparse_<20"
        if x < 20
        else "moderate_20plus"))

print("\nHistory groups:")
print(sku_history["history_group"].value_counts())

# ============================================================
# Build category benchmark from established SKUs
# ============================================================
established_history = weekly[weekly["sku_id"].isin(established_skus)].copy()
category_reference = (established_history.groupby("category").agg(category_demand=("demand", "sum"),category_sku_weeks=("demand", "size")).reset_index())
category_reference["category_avg_demand_per_sku_week"] = (category_reference["category_demand"]/ category_reference["category_sku_weeks"])

# ============================================================
# Add category information
# ============================================================
sku_history = sku_history.merge(sku_master[["sku_id","product_name","category"]],on="sku_id",how="left")
sku_history = sku_history.merge(category_reference[["category","category_avg_demand_per_sku_week"]],on="category",how="left")

# ============================================================
# Select fallback weekly demand
# ============================================================
sku_history["fallback_weekly_demand"] = (sku_history["avg_weekly_demand"])
sparse_mask = (sku_history["history_group"] == "sparse_<20")
sku_history.loc[sparse_mask, "fallback_weekly_demand"] = (0.5 * sku_history.loc[sparse_mask, "avg_weekly_demand"] + 0.5 * sku_history.loc[sparse_mask,"category_avg_demand_per_sku_week"])

# ============================================================
# Confidence
# ============================================================
sku_history["forecast_confidence"] = (sku_history["history_group"].map({"moderate_20plus": "Medium","sparse_<20": "Low"}))

# ============================================================
# Create 8-week fallback forecast
# ============================================================
forecast_weeks = pd.date_range(start="2026-01-05",periods=8,freq="W-MON")
fallback_rows = []
for week in forecast_weeks: 
    for _, row in sku_history.iterrows():fallback_rows.append({"sku_id": row["sku_id"],"week_start": week,"forecast": (row["fallback_weekly_demand"]),"forecast_method": "category_fallback","forecast_confidence": (row["forecast_confidence"])})
fallback_forecast = pd.DataFrame(fallback_rows)

# ============================================================
# Validation1
# ============================================================
print("\nFallback forecast rows:")
print(len(fallback_forecast))
print("Fallback SKUs:",fallback_forecast["sku_id"].nunique())
print("Forecast weeks:",fallback_forecast["week_start"].nunique())
print("\nConfidence:")
print(fallback_forecast[["sku_id", "forecast_confidence"]].drop_duplicates()["forecast_confidence"].value_counts())
print("\nFirst 10 fallback forecasts:")
print(fallback_forecast.head(10))

# ============================================================
# Validation2
# ============================================================
print("\nMissing fallback forecasts:")
print(fallback_forecast["forecast"].isna().sum())
print("\nNon-positive fallback forecasts:")
print((fallback_forecast["forecast"] <= 0).sum())
print("\nFallback SKU counts:")
print(fallback_forecast["sku_id"].value_counts().describe())

# ============================================================
# Save fallback forecast
# ============================================================
fallback_forecast.to_csv("data/processed/fallback_forecast.csv",index=False)

print("\nFallback forecast saved.")
print("Rows saved:", len(fallback_forecast))