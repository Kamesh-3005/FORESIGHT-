import pandas as pd

# ============================================================
# Load weekly demand data
# ============================================================
df = pd.read_csv("data/processed/weekly_demand.csv")

# ============================================================
# Convert week_start to datetime
# ============================================================
df["week_start"] = pd.to_datetime(df["week_start"])

# ============================================================
# Sort by SKU and week
# ============================================================
df = df.sort_values(["sku_id", "week_start"]).reset_index(drop=True)

print("Rows:", len(df))
print("Columns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())

# ============================================================
# Create previous-week demand
# ============================================================
df["lag_1"] = (df.groupby("sku_id")["demand"].shift(1))

print("\nFirst 10 rows with lag_1:")
print(df[["sku_id", "week_start", "demand", "lag_1"]].head(10))

# ============================================================
# Create lag features
# ============================================================
for lag in [2, 4, 8]: df[f"lag_{lag}"] = (df.groupby("sku_id")["demand"].shift(lag))

print("\nLag feature sample:")
print(df[["sku_id", "week_start", "demand", "lag_1", "lag_2", "lag_4", "lag_8"]].head(15))

# ============================================================
# 4-week rolling average using past demand only
# ============================================================
df["rolling_mean_4"] = (df.groupby("sku_id")["demand"].transform(lambda x: x.shift(1).rolling(4).mean()))

print("\nRolling mean sample:")
print(df[["sku_id", "week_start", "demand", "rolling_mean_4"]].iloc[0:15])

# ============================================================
# 4-week rolling median using past demand only
# ============================================================
df["rolling_median_4"] = (df.groupby("sku_id")["demand"].transform(lambda x: x.shift(1).rolling(4).median()))

# ============================================================
# 4-week rolling standard deviation using past demand only
# ============================================================
df["rolling_std_4"] = (df.groupby("sku_id")["demand"].transform(lambda x: x.shift(1).rolling(4).std()))

print("\nRolling feature sample:")
print(df[["sku_id", "week_start", "demand", "rolling_mean_4", "rolling_median_4", "rolling_std_4"]].iloc[0:10])
print("\nSeason values:")
print(df["season"].value_counts(dropna=False))

# ============================================================
# Convert holiday indicator from True/False to 1/0
# ============================================================
df["is_holiday"] = df["is_holiday"].astype(int)

print("\nHoliday values:")
print(df["is_holiday"].value_counts(dropna=False))
print("\nPromotion events:")
print(df["promo_event"].value_counts(dropna=False))

# ============================================================
# Load daily calendar
# ============================================================
calendar = pd.read_csv("data/processed/calendar.csv")

calendar["date"] = pd.to_datetime(calendar["date"])

# ============================================================
# Create Monday-based week_start
# ============================================================
calendar["week_start"] = (calendar["date"] - pd.to_timedelta(calendar["date"].dt.dayofweek, unit="D"))

# ============================================================
# Identify promotional days
# ============================================================
calendar["is_promotion"] = (calendar["promo_event"] != "No Promotion").astype(int)

# ============================================================
# Aggregate promotion information to weekly level
# ============================================================
weekly_promo = (calendar.groupby("week_start").agg(promotion_days=("is_promotion", "sum")).reset_index())

# ============================================================
# Merge weekly promotion information
# ============================================================
df = df.merge(weekly_promo, on="week_start", how="left")

# ============================================================
# Weeks without a promotion have zero promotion days
# ============================================================
df["promotion_days"] = (df["promotion_days"].fillna(0).astype(int))

print("\nPromotion-day sample:")
print(df[["sku_id", "week_start", "promo_event", "promotion_days"]].head(15))
print("\nPromotion days missing values:")
print(df["promotion_days"].isna().sum())

print("\nPromotion days range:")
print(df["promotion_days"].min(), "to", df["promotion_days"].max())
print("\nPromotion-day distribution:")
print(df["promotion_days"].value_counts().sort_index())

# ============================================================
# Load sales pricing data
# ============================================================
sales = pd.read_csv("data/processed/sales_daily.csv", usecols=["date", "sku_id", "unit_price", "list_price"])
sales["date"] = pd.to_datetime(sales["date"])

# ============================================================
# Create Monday-based week_start
# ============================================================
sales["week_start"] = (sales["date"]- pd.to_timedelta(sales["date"].dt.dayofweek,unit="D"))

# ============================================================
# Calculate discount percentage
# ============================================================
sales["discount_pct"] = ((sales["list_price"] - sales["unit_price"])/ sales["list_price"]) * 100

# ============================================================
# Aggregate discount to SKU-week level
# ============================================================
weekly_discount = (sales.groupby(["sku_id", "week_start"]).agg(avg_discount_pct=("discount_pct", "mean")).reset_index())

# ============================================================
# Merge into weekly modelling dataset
# ============================================================
df = df.merge(weekly_discount, on=["sku_id", "week_start"], how="left")

print("\nDiscount feature sample:")
print(df[["sku_id", "week_start", "avg_discount_pct"]].head(10))
print("\nDiscount feature validation:")

print("Missing values:")
print(df["avg_discount_pct"].isna().sum())

print("\nMinimum discount:")
print(df["avg_discount_pct"].min())

print("\nMaximum discount:")
print(df["avg_discount_pct"].max())
print(df["season"].value_counts())
print("\nMissing season values:", df["season"].isna().sum())

# ============================================================
# One-hot encode season
# ============================================================
season_dummies = pd.get_dummies(df["season"], prefix="season", dtype=int)
df = pd.concat([df, season_dummies], axis=1)

print("\nSeason encoding:")
print(df[["season", "season_Autumn", "season_Rain", "season_Summer", "season_Winter"]].head(10))
print("\nSeason encoding validation:")
season_cols = ["season_Autumn", "season_Rain", "season_Summer", "season_Winter"]

print("Rows with exactly one season:")
print((df[season_cols].sum(axis=1) == 1).sum(), "of", len(df))

print("\nRows with invalid season encoding:")
print((df[season_cols].sum(axis=1) != 1).sum())

# ============================================================
# Save final forecasting feature dataset
# ============================================================
feature_cols = [
    "lag_1",
    "lag_2",
    "lag_4",
    "lag_8",
    "rolling_mean_4",
    "rolling_median_4",
    "rolling_std_4",
    "month",
    "week",
    "quarter",
    "is_holiday",
    "promotion_days",
    "season_Autumn",
    "season_Rain",
    "season_Summer",
    "season_Winter"
]

output_cols = ["sku_id", "week_start", "demand"] + feature_cols
feature_df = df[output_cols].copy()
feature_df.to_csv("data/processed/feature_engineered.csv", index=False)

print("\nFinal feature dataset saved:")
print("data/processed/feature_engineered.csv")

print("\nShape:")
print(feature_df.shape)

print("\nColumns:")
print(feature_df.columns.tolist())