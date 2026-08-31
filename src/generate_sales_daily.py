import pandas as pd
import numpy as np

calendar = pd.read_csv("data/processed/calendar.csv")
sku_master = pd.read_csv("data/processed/sku_master.csv")
store_master = pd.read_csv("data/processed/store_master.csv")

# Create a small test dataset
sales_calendar = calendar.copy()

test_skus = sku_master.copy()

sales = sales_calendar.merge(
    test_skus,
    how="cross"
)
sales = sales[
    sales["date"] >= sales["launch_date"]
].copy()
sales = sales.merge(
    store_master,
    how="cross"
)
# Category-based demand multiplier # Generate base units sold

category_multiplier = {
    "Storage & Organizers": 1.30,
    "Appliances": 1.20,
    "Furniture": 1.00,
    "Home Decor": 0.90,
    "Cookware & Tableware": 0.80
}

sales["category_multiplier"] = sales["category"].map(category_multiplier)

# Generate base demand
sales["units_sold"] = (
    np.random.randint(5, 16, size=len(sales))
    * sales["category_multiplier"]
    * sales["store_multiplier"]
).round().astype(int)


# Increase demand on weekends
sales.loc[sales["is_weekend"], "units_sold"] += 3


# Increase demand during promotions
sales.loc[
    sales["promo_event"] != "No Promotion",
    "units_sold"
] += 5

# Increase demand on holidays
sales.loc[
    sales["is_holiday"],
    "units_sold"
] += 3

sales["unit_price"] = sales["list_price"].astype(float)

sales.loc[
    sales["promo_event"] != "No Promotion",
    "unit_price"
] = (
    sales.loc[
        sales["promo_event"] != "No Promotion",
        "list_price"
    ] * 0.90
)
sales["revenue"] = sales["units_sold"] * sales["unit_price"]

sales.drop(
    columns=["category_multiplier", "store_multiplier"],
    inplace=True
)

print("\nRevenue by Category:")

category_summary = (
    sales.groupby("category")
    .agg(
        total_units=("units_sold", "sum"),
        total_revenue=("revenue", "sum")
    )
    .sort_values("total_revenue", ascending=False)
)

print(category_summary)

print("\nAverage Unit Price by Category:")

price_summary = (
    sales.groupby("category")
    .agg(
        avg_unit_price=("unit_price", "mean"),
        total_units=("units_sold", "sum"),
        total_revenue=("revenue", "sum")
    )
    .sort_values("avg_unit_price", ascending=False)
)

print(price_summary.round(2))

print("\nTop 20 Products by Unit Price:")

product_price_check = (
    sales.groupby(
        ["sku_id", "product_name", "category"]
    )
    .agg(
        avg_unit_price=("unit_price", "mean"),
        total_units=("units_sold", "sum"),
        total_revenue=("revenue", "sum")
    )
    .sort_values(
        "avg_unit_price",
        ascending=False
    )
)

print(product_price_check.head(20).round(2))