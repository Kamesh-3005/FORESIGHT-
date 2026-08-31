import pandas as pd

# ============================================================
# Load primary and fallback forecasts
# ============================================================
primary = pd.read_csv("data/processed/final_forecast.csv")
fallback = pd.read_csv("data/processed/fallback_forecast.csv")

# ============================================================
# Add metadata to primary ML forecast
# ============================================================
primary["forecast_method"] = "primary_ml"
primary["forecast_confidence"] = "Established"

# ============================================================
# Combine both forecast populations
# ============================================================
combined_forecast = pd.concat([primary[["sku_id","week_start","forecast","forecast_method","forecast_confidence"]],
                               fallback[["sku_id","week_start","forecast","forecast_method","forecast_confidence"]]],
                               ignore_index=True)

# ============================================================
# Validation
# ============================================================
print("Total forecast rows:", len(combined_forecast))
print("Unique SKUs:",combined_forecast["sku_id"].nunique())
print("Forecast weeks:",combined_forecast["week_start"].nunique())
print("\nForecast method:")
print(combined_forecast["forecast_method"].value_counts())
print("\nForecast confidence:")
print(combined_forecast["forecast_confidence"].value_counts())
print("\nMissing values:")
print(combined_forecast.isna().sum())
print("\nDuplicate SKU-week rows:")
print(combined_forecast.duplicated(["sku_id", "week_start"]).sum())

# ============================================================
# Save combined forecast
# ============================================================
combined_forecast.to_csv("data/processed/combined_forecast.csv",index=False)

print("\nCombined forecast saved.")
print("Rows saved:",len(combined_forecast))