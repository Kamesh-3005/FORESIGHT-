import pandas as pd

files = {
    "calendar": "data/processed/calendar.csv",
    "sku_master": "data/processed/sku_master.csv",
    "store_master": "data/processed/store_master.csv",
    "sales_daily": "data/processed/sales_daily.csv",
    "inventory_daily": "data/processed/inventory_daily.csv"
}

for name, path in files.items():

    df = pd.read_csv(path)

    print("\n" + "=" * 60)
    print(name.upper())
    print("=" * 60)

    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Column names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())