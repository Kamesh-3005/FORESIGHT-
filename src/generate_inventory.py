import pandas as pd
import numpy as np

# Load data
sku_master = pd.read_csv("data/processed/sku_master.csv")
store_master = pd.read_csv("data/processed/store_master.csv")
sales = pd.read_csv("data/processed/sales_daily.csv")

# Create inventory base from sales data
inventory = sales[
    ["date", "sku_id", "store_id", "units_sold"]
].copy()

# Add product category
inventory = inventory.merge(
    sku_master[["sku_id", "category"]],
    on="sku_id",
    how="left"
)
# Define initial stock by category
category_stock = {
    "Storage & Organizers": 120,
    "Appliances": 50,
    "Furniture": 30,
    "Home Decor": 80,
    "Cookware & Tableware": 100
}

inventory["initial_stock"] = inventory["category"].map(
    category_stock
)
# Generate units received
inventory["units_received"] = np.random.randint(
    10,
    31,
    size=len(inventory)
)

inventory.loc[
    inventory["category"] == "Storage & Organizers",
    "units_received"
] += 20

inventory.loc[
    inventory["category"] == "Appliances",
    "units_received"
] += 15

inventory.loc[
    inventory["category"] == "Furniture",
    "units_received"
] += 10

# Sort inventory chronologically
inventory = inventory.sort_values(
    ["sku_id", "store_id", "date"]
).reset_index(drop=True)

# Calculate inventory flow
def calculate_inventory(group):

    sku_id = group.name[0]
    store_id = group.name[1]

    group = group.sort_values("date").copy()

    opening_stock = []
    closing_stock = []

    current_stock = int(group["initial_stock"].iloc[0])

    for _, row in group.iterrows():

        opening = current_stock

        closing = (
            opening
            + row["units_received"]
            - row["units_sold"]
        )

        closing = max(0, closing)

        opening_stock.append(opening)
        closing_stock.append(closing)

        current_stock = closing

    group["sku_id"] = sku_id
    group["store_id"] = store_id

    group["opening_stock"] = opening_stock
    group["closing_stock"] = closing_stock

    return group


inventory = (
    inventory
    .groupby(
        ["sku_id", "store_id"],
        group_keys=False
    )
    .apply(calculate_inventory)
)


inventory.to_csv(
    "data/processed/inventory_daily.csv",
    index=False
)

print("Inventory Daily saved successfully.")