import pandas as pd

dates = pd.date_range(
    start="2021-01-01",
    end="2025-12-31",
    freq="D"
)

calendar = pd.DataFrame({
    "date": dates
})

calendar["year"] = calendar["date"].dt.year
calendar["month"] = calendar["date"].dt.month
calendar["week"] = calendar["date"].dt.isocalendar().week
calendar["quarter"] = calendar["date"].dt.quarter
calendar["day_of_week"] = calendar["date"].dt.day_name()

calendar["is_weekend"] = calendar["date"].dt.dayofweek >= 5


def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8]:
        return "Rain"
    else:
        return "Autumn"


calendar["season"] = calendar["month"].apply(get_season)

def get_promo_event(date):

    month = date.month
    day = date.day

     # New Year Sale
    if month == 1 and day <= 7:
        return "New Year Sale"
    # End of Season Sale
    elif month == 3 and day <= 7:
        return "End of Season Sale"

    # Independence Day Sale
    elif month == 8 and 10 <= day <= 15:
        return "Independence Day Sale"

    # Festive Sale
    elif (month == 10 and day >= 15) or (month == 11 and day <= 5):
        return "Festive Sale"

    # Black Friday
    elif month == 11 and date.dayofweek == 4 and 23 <= day <= 29:
        return "Black Friday"

    # Stock Clearance Sale
    elif month == 12 and day >= 26:
        return "Stock Clearance Sale"

    else:
        return "No Promotion"
    
calendar["promo_event"] = calendar["date"].apply(get_promo_event)    

def check_holiday(date):
    month_day = date.strftime("%m-%d")

    if month_day in ["01-26", "04-14", "08-15", "10-02", "12-25", ]:
        return True
    else:
        return False
    
calendar["is_holiday"] = calendar["date"].apply(check_holiday)    

calendar = calendar[
    [
        "date",
        "year",
        "month",
        "week",
        "quarter",
        "season",
        "day_of_week",
        "is_weekend",
        "is_holiday",
        "promo_event"
    ]
]

calendar.to_csv("data/processed/calendar.csv", index=False)