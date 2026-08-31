import pandas as pd

from sklearn.ensemble import HistGradientBoostingRegressor

# ============================================================
# Load feature-engineered data
# ============================================================
df = pd.read_csv(
    "data/processed/feature_engineered.csv"
)

# ============================================================
# Convert date
# ============================================================
df["week_start"] = pd.to_datetime(
    df["week_start"]
)

# ============================================================
# Sort data
# ============================================================
df = df.sort_values(
    ["sku_id", "week_start"]
).reset_index(drop=True)

print("Rows:", len(df))
print("SKUs:", df["sku_id"].nunique())
print("SKUs:", df["sku_id"].nunique())

# ============================================================
# Create 52-week seasonal lag
# ============================================================
df["lag_52"] = (
    df.groupby("sku_id")["demand"]
      .shift(52)
)

print("lag_52 available:", df["lag_52"].notna().sum())

# ============================================================
# Keep established SKUs
# ============================================================
established_skus = (
    df.loc[
        df["lag_52"].notna(),
        "sku_id"
    ]
    .unique()
)

df = df[
    df["sku_id"].isin(established_skus)
].copy()

print("Established SKUs:", len(established_skus))
print("Rows after filter:", len(df))

feature_cols = [
    "lag_1",
    "lag_2",
    "lag_4",
    "lag_8",
    "lag_52",
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

target = "demand"

print("Features:", len(feature_cols))
print("Target:", target)

model = HistGradientBoostingRegressor(
    max_iter=200,
    learning_rate=0.05,
    max_leaf_nodes=31,
    random_state=42
)

print("Model:", model)

# ============================================================
# Use all available historical rows with complete features
# ============================================================
train_model = df.dropna(
    subset=feature_cols
).copy()

X_train = train_model[feature_cols]
y_train = train_model[target]

print("Training rows:", len(train_model))
print("X_train shape:", X_train.shape)
print("y_train shape:", y_train.shape)

print("\nTraining final model...")

model.fit(
    X_train,
    y_train
)

print("Final model trained.")

# ============================================================
# Forecast period
# ============================================================
last_week = df["week_start"].max()

forecast_start = last_week + pd.Timedelta(weeks=1)

forecast_weeks = pd.date_range(
    start=forecast_start,
    periods=8,
    freq="W-MON"
)

print("\nForecast period:")
print(forecast_weeks)

# ============================================================
# Create future forecast rows
# ============================================================
future_rows = pd.MultiIndex.from_product(
    [
        established_skus,
        forecast_weeks
    ],
    names=["sku_id", "week_start"]
).to_frame(index=False)

print("\nFuture forecast rows:", len(future_rows))
print("Future SKUs:", future_rows["sku_id"].nunique())
print("Future weeks:", future_rows["week_start"].nunique())

# ============================================================
# Add calendar features
# ============================================================
future_rows["month"] = future_rows["week_start"].dt.month
future_rows["week"] = future_rows["week_start"].dt.isocalendar().week.astype(int)
future_rows["quarter"] = future_rows["week_start"].dt.quarter

print("Calendar features created.")

# ============================================================
# Holiday feature
# ============================================================
future_rows["is_holiday"] = 0

print("Holiday feature created.")

# ============================================================
# Promotion feature
# ============================================================
future_rows["promotion_days"] = 0

print("Promotion feature created.")

# ============================================================
# Create future lag_52
# ============================================================
historical_lag = df[
    ["sku_id", "week_start", "demand"]
].copy()

historical_lag["week_start"] = (
    historical_lag["week_start"]
    + pd.Timedelta(weeks=52)
)

historical_lag = historical_lag.rename(
    columns={
        "week_start": "forecast_week",
        "demand": "lag_52"
    }
)

future_rows = future_rows.merge(
    historical_lag,
    left_on=["sku_id", "week_start"],
    right_on=["sku_id", "forecast_week"],
    how="left"
)

future_rows = future_rows.drop(
    columns=["forecast_week"]
)

print("Future lag_52 prepared.")
print(
    "Future lag_52 missing:",
    future_rows["lag_52"].isna().sum()
)

# ============================================================
# Historical demand lookup
# ============================================================
history = df[
    ["sku_id", "week_start", "demand"]
].copy()

history = history.set_index(
    ["sku_id", "week_start"]
)["demand"]

print("Historical demand lookup created.")

# ============================================================
# Recursive 8-week forecast
# ============================================================
forecast_results = []

for week in forecast_weeks:

    print(f"Forecasting: {week.date()}")

# ============================================================
# Build lag features
# ============================================================
    lag_values = {}

    for lag in [1, 2, 4, 8]:

        values = []

        for sku in established_skus:

            lag_week = (
                week
                - pd.Timedelta(weeks=lag)
            )

            try:
                value = history.loc[
                    (sku, lag_week)
                ]
            except KeyError:
                value = None

            values.append(value)

        lag_values[f"lag_{lag}"] = values

    print(
        "Lag availability:",
        {
            key: sum(
                value is not None
                for value in values
            )
            for key, values
            in lag_values.items()
        }
    )

# ============================================================    
# Build feature table for this week
# ============================================================
    week_features = pd.DataFrame({
        "sku_id": established_skus,
        "week_start": week,
        "lag_1": lag_values["lag_1"],
        "lag_2": lag_values["lag_2"],
        "lag_4": lag_values["lag_4"],
        "lag_8": lag_values["lag_8"],
    })

    print("Week feature rows:", len(week_features))
    print(
        "Week feature columns:",
        week_features.columns.tolist()
    )

# ============================================================    
# Add remaining model features
# ============================================================
    week_features["month"] = week.month
    week_features["week"] = week.isocalendar().week
    week_features["quarter"] = week.quarter
    week_features["is_holiday"] = 0
    week_features["promotion_days"] = 0

# ============================================================
# Seasonal indicators
# Season encoding
# ============================================================
    season = {
        1: "Winter",
        2: "Winter",
        3: "Summer",
        4: "Summer",
        5: "Summer",
        6: "Rain",
        7: "Rain",
        8: "Rain",
        9: "Autumn",
        10: "Autumn",
        11: "Autumn",
        12: "Winter"
    }[week.month]

    week_features["season_Autumn"] = int(
        season == "Autumn")
    week_features["season_Rain"] = int(
        season == "Rain"
    )

    week_features["season_Summer"] = int(
        season == "Summer"
    )

    week_features["season_Winter"] = int(
        season == "Winter"
    )

# ============================================================    
# Rolling features
# ============================================================
    rolling_values = {
        "rolling_mean_4": [],
        "rolling_median_4": [],
        "rolling_std_4": []
    }

    for sku in established_skus:

        previous_weeks = [
            week - pd.Timedelta(weeks=i)
            for i in range(1, 5)
        ]

        values = []

        for previous_week in previous_weeks:

            try:
                value = history.loc[
                    (sku, previous_week)
                ]
                values.append(value)
            except KeyError:
                pass

        rolling_values[
            "rolling_mean_4"
        ].append(
            pd.Series(values).mean()
        )

        rolling_values[
            "rolling_median_4"
        ].append(
            pd.Series(values).median()
        )

        rolling_values[
            "rolling_std_4"
        ].append(
            pd.Series(values).std()
        )

    week_features["rolling_mean_4"] = (
        rolling_values["rolling_mean_4"]
    )

    week_features["rolling_median_4"] = (
        rolling_values["rolling_median_4"]
    )

    week_features["rolling_std_4"] = (
        rolling_values["rolling_std_4"]
    )

    print("Rolling features prepared.")

# ============================================================
# Add 52-week seasonal lag
# ============================================================
week_features["lag_52"] = (future_rows.loc[future_rows["week_start"] == week,"lag_52"].values)

# ============================================================
# Verify all model features exist
# ============================================================
missing_features = [col
    for col in feature_cols
    if col not in week_features.columns]

print("Missing model features:", missing_features)

X_future = week_features[feature_cols]

print("X_future shape:", X_future.shape)

# ============================================================    
# Generate forecast
# ============================================================
prediction = model.predict(X_future) 

print("Prediction rows:", len(prediction))
print("First 5 predictions:", prediction[:5])

# ============================================================
# Store predictions in history
# ============================================================
for sku, value in zip(established_skus, prediction):history.loc[(sku, week)] = value

print("Predictions added to history:", len(prediction))

# ============================================================    
# Store forecast results
# ============================================================
week_forecast = pd.DataFrame({"sku_id": established_skus, "week_start": week, "forecast": prediction})

forecast_results.append(week_forecast)

print("Forecast results stored:", len(week_forecast))

# ============================================================
# Combine all forecast weeks
# ============================================================
forecast_df = pd.concat(forecast_results, ignore_index=True)

print("Total forecast rows:", len(forecast_df))
print("Forecast SKUs:", forecast_df["sku_id"].nunique())
print("Forecast weeks:", forecast_df["week_start"].nunique())   

forecast_df.to_csv("data/processed/final_forecast.csv",index=False)

print("Final forecast saved.")