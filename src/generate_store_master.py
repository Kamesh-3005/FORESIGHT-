import pandas as pd

stores = [
    ["ST001", "FORESIGHT Central", "Bhubaneswar", "Odisha", "Large", 1.20],
    ["ST002", "FORESIGHT Metro", "Kolkata", "West Bengal", "Large", 1.30],
    ["ST003", "FORESIGHT Urban", "Ranchi", "Jharkhand", "Medium", 1.00],
    ["ST004", "FORESIGHT City", "Raipur", "Chhattisgarh", "Medium", 0.95],
    ["ST005", "FORESIGHT Home", "Cuttack", "Odisha", "Small", 0.80]
]
store_master = pd.DataFrame(
    stores,
    columns=[
        "store_id",
        "store_name",
        "city",
        "state",
        "store_size",
        "store_multiplier"
    ]
)

store_master.to_csv(
    "data/processed/store_master.csv",
    index=False
)

print("Store Master saved successfully.")