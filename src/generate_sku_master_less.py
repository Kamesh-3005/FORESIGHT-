import pandas as pd
storage_products = [
    "Clear Plastic Storage Bin",
    "Stackable Plastic Storage Bin",
    "Under-Bed Storage Box",
    "Foldable Fabric Storage Cube",
    "Large Plastic Storage Box",
    "File Storage Box",
]
print(storage_products) 
sku_ids = []

for i in range(1, len(storage_products) + 1):
    sku_ids.append(f"SKU{i:03d}")

categories = [
    "Storage & Organizers",
    "Storage & Organizers",
    "Storage & Organizers"
] 
launch_dates = [
    "2021-02-15",
    "2021-06-10",
    "2022-01-20"
]
unit_costs = [
    180,
    300,
    450
]

list_prices = [
    299,
    499,
    749
]
sku_master = pd.DataFrame({
    "sku_id": sku_ids,
    "product_name": storage_products,
    "category": categories,
    "launch_date": launch_dates,
    "unit_cost": unit_costs,
    "list_price": list_prices
})

print(sku_master)