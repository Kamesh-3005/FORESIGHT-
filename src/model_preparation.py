import pandas as pd

df = pd.read_csv(
    "data/processed/feature_engineered.csv"
)

df["week_start"] = pd.to_datetime(df["week_start"])

df = df.sort_values(
    ["sku_id", "week_start"]
).reset_index(drop=True)

df["lag_52"] = (
    df.groupby("sku_id")["demand"]
      .shift(52)
)

print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nDate range:")
print(df["week_start"].min(), "to", df["week_start"].max())

print("\nlag_52 missing:")
print(df["lag_52"].isna().sum())
train_period = df[
    df["week_start"] < "2025-01-01"
]

test_period = df[
    df["week_start"] >= "2025-01-01"
]

established_skus = (
    set(train_period["sku_id"])
    & set(test_period["sku_id"])
)

print("\nEstablished SKUs:")
print(len(established_skus))

print("\nTraining rows:")
print(len(train_period))

print("\nTest rows:")
print(len(test_period))
model_df = df[
    df["sku_id"].isin(established_skus)
].copy()

train = model_df[
    model_df["week_start"] < "2025-01-01"
].copy()

test = model_df[
    model_df["week_start"] >= "2025-01-01"
].copy()

print("\nModel training rows:")
print(len(train))

print("\nModel test rows:")
print(len(test))

print("\nTraining SKUs:")
print(train["sku_id"].nunique())

print("\nTest SKUs:")
print(test["sku_id"].nunique())
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

print("\nNumber of features:")
print(len(feature_cols))

print("\nFeatures:")
for feature in feature_cols:
    print("-", feature)

print("\nTarget:")
print(target)
X_train = train[feature_cols]
y_train = train[target]

X_test = test[feature_cols]
y_test = test[target]

print("\nX_train shape:")
print(X_train.shape)

print("\nX_test shape:")
print(X_test.shape)

print("\ny_train shape:")
print(y_train.shape)

print("\ny_test shape:")
print(y_test.shape)
print("\nMissing values in X_train:")
print(X_train.isna().sum())

print("\nMissing values in X_test:")
print(X_test.isna().sum())
print("\nMissing values in X_train:")
print(X_train.isna().sum())

print("\nMissing values in X_test:")
print(X_test.isna().sum())
from sklearn.ensemble import HistGradientBoostingRegressor

model = HistGradientBoostingRegressor(
    max_iter=200,
    learning_rate=0.05,
    max_leaf_nodes=31,
    random_state=42
)

print("\nModel created:")
print(model)
print("\nModel created:")
print(model)
print("\nTraining model...")

model.fit(
    X_train,
    y_train
)

print("Model training completed.")
print("\nGenerating predictions...")

y_pred = model.predict(X_test)

print("Predictions generated.")

print("\nFirst 10 predictions:")
print(y_pred[:10])
results = test[
    ["sku_id", "week_start", "demand"]
].copy()

results["prediction"] = y_pred

print("\nPrediction sample:")
print(results.head(10))
absolute_error = (
    results["demand"] - results["prediction"]
).abs()

model_wape = (
    absolute_error.sum()
    / results["demand"].sum()
) * 100

print("\nModel WAPE:")
print(f"{model_wape:.2f}%")
error = (
    results["prediction"]
    - results["demand"]
)

model_bias = (
    error.sum()
    / results["demand"].sum()
) * 100

print("\nModel Bias:")
print(f"{model_bias:.2f}%")
results["seasonal_naive_52"] = (
    df.groupby("sku_id")["demand"]
      .shift(52)
)

results["naive_error"] = (
    results["seasonal_naive_52"]
    - results["demand"]
)

naive_wape = (
    results["naive_error"].abs().sum()
    / results["demand"].sum()
) * 100

naive_bias = (
    results["naive_error"].sum()
    / results["demand"].sum()
) * 100

print("\nFair Seasonal-Naive Comparison")
print("===============================")

print(f"Naive WAPE: {naive_wape:.2f}%")
print(f"Naive Bias: {naive_bias:.2f}%")

from sklearn.inspection import permutation_importance

print("\nCalculating permutation importance...")

importance = permutation_importance(
    model,
    X_test,
    y_test,
    n_repeats=5,
    random_state=42,
    scoring="neg_mean_absolute_error"
)

importance_df = pd.DataFrame({
    "feature": feature_cols,
    "importance": importance.importances_mean
})

importance_df = importance_df.sort_values(
    "importance",
    ascending=False
)

print("\nFeature importance:")
print(importance_df.to_string(index=False))
#
#
#
# -----------------------------------------
# Rolling-origin backtest setup
# -----------------------------------------
forecast_horizon = 8

all_weeks = (
    model_df["week_start"]
    .drop_duplicates()
    .sort_values()
    .reset_index(drop=True)
)

print("\nTotal model weeks:")
print(len(all_weeks))

print("\nFirst 10 model weeks:")
print(all_weeks.head(10).to_string(index=False))

print("\nLast 10 model weeks:")
print(all_weeks.tail(10).to_string(index=False))


# First rolling-origin window

origin = pd.Timestamp("2024-12-02")

train_window = model_df[
    model_df["week_start"] < origin
].copy()

test_window = model_df[
    (model_df["week_start"] >= origin)
    & (
        model_df["week_start"]
        < origin + pd.Timedelta(weeks=forecast_horizon)
    )
].copy()

print("\nFirst rolling-origin window")
print("===========================")

print("\nOrigin:")
print(origin)

print("\nTraining period:")
print(
    train_window["week_start"].min(),
    "to",
    train_window["week_start"].max()
)

print("\nTraining rows:")
print(len(train_window))

print("\nForecast period:")
print(
    test_window["week_start"].min(),
    "to",
    test_window["week_start"].max()
)

print("\nTest rows:")
print(len(test_window))

print("\nTest weeks:")
print(
    test_window["week_start"]
    .drop_duplicates()
    .sort_values()
    .to_string(index=False)
)

print("\nTest SKUs:")
print(test_window["sku_id"].nunique())
print("\nMissing features in first test window:")
print(
    test_window[feature_cols]
    .isna()
    .sum()
)

#
#
# Train model for first rolling origin

X_train_origin = train_window[feature_cols]
y_train_origin = train_window[target]

X_test_origin = test_window[feature_cols]
y_test_origin = test_window[target]

origin_model = HistGradientBoostingRegressor(
    max_iter=200,
    learning_rate=0.05,
    max_leaf_nodes=31,
    random_state=42
)

print("\nTraining first rolling-origin model...")

origin_model.fit(
    X_train_origin,
    y_train_origin
)

print("First rolling-origin model trained.")
print("\nGenerating Origin 1 predictions...")

origin_pred = origin_model.predict(
    X_test_origin
)

print("Predictions generated.")

print("\nFirst 10 predictions:")
print(origin_pred[:10])
# -----------------------------------------
# Origin 1 comparison
# -----------------------------------------

origin_results = test_window[
    ["sku_id", "week_start", "demand"]
].copy()

origin_results["ml_prediction"] = origin_pred

origin_results["seasonal_naive_52"] = (
    df.groupby("sku_id")["demand"]
      .shift(52)
      .reindex(test_window.index)
      .values
)

print("\nOrigin 1 comparison:")
print(
    origin_results.head(10).to_string(index=False)
)
# Calculate WAPE

ml_abs_error = (
    origin_results["demand"]
    - origin_results["ml_prediction"]
).abs()

naive_abs_error = (
    origin_results["demand"]
    - origin_results["seasonal_naive_52"]
).abs()

ml_wape = (
    ml_abs_error.sum()
    / origin_results["demand"].sum()
) * 100

naive_wape = (
    naive_abs_error.sum()
    / origin_results["demand"].sum()
) * 100


# Calculate bias

ml_bias = (
    (
        origin_results["ml_prediction"]
        - origin_results["demand"]
    ).sum()
    / origin_results["demand"].sum()
) * 100

naive_bias = (
    (
        origin_results["seasonal_naive_52"]
        - origin_results["demand"]
    ).sum()
    / origin_results["demand"].sum()
) * 100


print("\nOrigin 1 Results")
print("================")

print(f"ML WAPE:       {ml_wape:.2f}%")
print(f"Naive WAPE:    {naive_wape:.2f}%")

print(f"ML Bias:        {ml_bias:.2f}%")
print(f"Naive Bias:     {naive_bias:.2f}%")
print("\nOrigin 7 seasonal-naive check:")

check_dates = pd.to_datetime([
    "2024-12-02",
    "2024-12-09",
    "2024-12-16",
    "2024-12-23",
    "2024-12-30",
    "2025-01-06",
    "2025-01-13",
    "2025-01-20"
])

check = df[
    df["week_start"].isin(check_dates)
][
    ["sku_id", "week_start", "demand", "lag_52"]
]

print(check.head(20).to_string(index=False))