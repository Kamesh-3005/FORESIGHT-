import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

# Load feature-engineered data
df = pd.read_csv(
    "data/processed/feature_engineered.csv"
)

# Convert date
df["week_start"] = pd.to_datetime(
    df["week_start"]
)

# Sort chronologically within each SKU
df = df.sort_values(
    ["sku_id", "week_start"]
).reset_index(drop=True)

# Create 52-week seasonal lag
df["lag_52"] = (
    df.groupby("sku_id")["demand"]
      .shift(52)
)

# -----------------------------------------
# Identify established SKUs
# -----------------------------------------

train_end = pd.Timestamp("2024-12-30")
test_start = pd.Timestamp("2025-01-06")

train_skus = set(
    df.loc[
        df["week_start"] <= train_end,
        "sku_id"
    ]
)

test_skus = set(
    df.loc[
        df["week_start"] >= test_start,
        "sku_id"
    ]
)

established_skus = sorted(
    train_skus.intersection(test_skus)
)

print("\nEstablished SKUs:")
print(len(established_skus))

# Keep only established SKUs
df = df[
    df["sku_id"].isin(established_skus)
].copy()

print("Rows after established-SKU filter:")
print(len(df))

print("SKUs after established-SKU filter:")
print(df["sku_id"].nunique())


print("\nlag_52 created.")
print(
    "lag_52 available:",
    df["lag_52"].notna().sum()
)

print(
    "lag_52 missing:",
    df["lag_52"].isna().sum()
)

# Forecast settings
forecast_horizon = 8
seasonal_period = 52

# Features
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

print("Rows:", len(df))
print("Features:", len(feature_cols))
print("Forecast horizon:", forecast_horizon)
# -----------------------------------------
# Generate rolling-origin dates
# -----------------------------------------

first_origin = pd.Timestamp("2024-01-01")
last_possible_origin = (
    df["week_start"].max()
    - pd.Timedelta(weeks=forecast_horizon - 1)
)

origins = pd.date_range(
    start=first_origin,
    end=last_possible_origin,
    freq=f"{forecast_horizon}W-MON"
)

print("\nRolling origins:")
for i, origin in enumerate(origins, start=1):
    print(f"{i}. {origin.date()}")

print("\nNumber of origins:")
print(len(origins))

# -----------------------------------------
# Rolling-origin backtest
# -----------------------------------------

backtest_results = []

for i, origin in enumerate(origins, start=1):

    print(f"\nRunning Origin {i}: {origin.date()}")

    # Create expanding training window
    train_window = df[
        df["week_start"] < origin
    ].copy()

    # Create 8-week test window
    test_window = df[
        (df["week_start"] >= origin)
        &
        (
            df["week_start"]
            < origin + pd.Timedelta(
                weeks=forecast_horizon
            )
        )
    ].copy()

    # Remove rows where required
    # training features are unavailable
    train_model = train_window.dropna(
        subset=feature_cols
    )

    X_train = train_model[feature_cols]
    y_train = train_model[target]

    # Common evaluation population:
    # only rows where seasonal-naive is available
    test_eval = test_window[
    test_window["lag_52"].notna()
].copy()

    X_test = test_eval[feature_cols]
    y_test = test_eval[target]

    # Train model
    model = HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    # ML predictions
    ml_prediction = model.predict(
        X_test
    )

    # Seasonal-naive prediction
    naive_prediction = (
    test_eval["lag_52"]
    .values
)

    actual = y_test.values
    

    # Absolute errors
    ml_abs_error = (
        actual - ml_prediction
    ).__abs__()

    naive_abs_error = (
        actual - naive_prediction
    ).__abs__()

    # WAPE
    ml_wape = (
        ml_abs_error.sum()
        / actual.sum()
    ) * 100

    naive_wape = (
        naive_abs_error.sum()
        / actual.sum()
    ) * 100

    # Bias
    ml_bias = (
        (ml_prediction - actual).sum()
        / actual.sum()
    ) * 100

    naive_bias = (
        (naive_prediction - actual).sum()
        / actual.sum()
    ) * 100

    backtest_results.append({
    "origin": origin,
    "test_rows": len(actual),
    "actual_total": actual.sum(),
    "ml_abs_error": ml_abs_error.sum(),
    "naive_abs_error": naive_abs_error.sum(),
    "ml_bias_error": (ml_prediction - actual).sum(),
    "naive_bias_error": (naive_prediction - actual).sum(),
    "ml_wape": ml_wape,
    "naive_wape": naive_wape,
    "ml_bias": ml_bias,
    "naive_bias": naive_bias
})

    print(
        f"ML WAPE: {ml_wape:.2f}%"
    )

    print(
        f"Naive WAPE: {naive_wape:.2f}%"
    )

    print(
        f"ML Bias: {ml_bias:.2f}%"
    )

    print(
        f"Naive Bias: {naive_bias:.2f}%"
    )
print("\nBacktest results:")
results_df = pd.DataFrame(backtest_results)

print("\nAverage WAPE:")
print("ML:", results_df["ml_wape"].mean())
print("Naive:", results_df["naive_wape"].mean())
print(pd.DataFrame(backtest_results))
print("\nTotal evaluation rows:")
print(results_df["test_rows"].sum())


print("\nAggregate WAPE:")
print(
    "ML:",
    results_df["ml_abs_error"].sum()
    / results_df["actual_total"].sum()
    * 100
)

print(
    "Naive:",
    results_df["naive_abs_error"].sum()
    / results_df["actual_total"].sum()
    * 100
)

print("\nAverage Bias:")
print("ML:", results_df["ml_bias"].mean())
print("Naive:", results_df["naive_bias"].mean())

results_df.to_csv(
    "data/processed/rolling_backtest_results.csv",
    index=False
)

print("\nRolling backtest results saved.")




