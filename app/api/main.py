import pandas as pd
from fastapi import FastAPI

# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="FORESIGHT Scoring API",
    description="Forecast and inventory risk scoring service",
    version="1.0.0"
)

# --------------------------------------------------
# Load project data
# --------------------------------------------------

forecast_path = "data/processed/combined_forecast.csv"
risk_path = "data/processed/risk_scoring.csv"

forecast_df = pd.read_csv(forecast_path)
risk_df = pd.read_csv(risk_path)

# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "FORESIGHT Scoring API",
        "status": "running",
        "version": "1.0.0"
    }


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# --------------------------------------------------
# SKU scoring endpoint
# --------------------------------------------------

@app.get("/score/{sku_id}")
def score_sku(sku_id: str):

    # Find risk record for the requested SKU
    risk_match = risk_df[
        risk_df["sku_id"] == sku_id
    ]

    # Handle unknown SKU
    if risk_match.empty:
        return {
            "status": "error",
            "message": f"SKU '{sku_id}' was not found."
        }

    # Get the single risk record
    risk = risk_match.iloc[0]

    # Get 8-week forecast for the SKU
    forecast_match = (
        forecast_df[
            forecast_df["sku_id"] == sku_id
        ]
        .sort_values("week_start")
    )

    # Prepare forecast response
    forecast = []

    for _, row in forecast_match.iterrows():
        forecast.append({
            "week_start": str(row["week_start"]),
            "forecast": float(row["forecast"])
        })

    # Return forecast + risk
    return {
        "status": "success",

        "sku": {
            "sku_id": str(risk["sku_id"]),
            "product_name": str(risk["product_name"]),
            "category": str(risk["category"])
        },

        "forecast": {
            "weeks": forecast,
            "forecast_8_week": float(risk["forecast_8_week"]),
            "forecast_method": str(risk["forecast_method"]),
            "forecast_confidence": str(risk["forecast_confidence"])
        },

        "inventory": {
            "latest_inventory": float(risk["latest_inventory"]),
            "coverage_ratio": float(risk["coverage_ratio"])
        },

        "risk": {
            "stockout_risk": str(risk["stockout_risk"]),
            "overstock_risk": str(risk["overstock_risk"]),
            "recommended_action": str(risk["recommended_action"])
        },

        "financial": {
            "unit_cost": float(risk["unit_cost"]),
            "units_at_risk": float(risk["units_at_risk"]),
            "rupee_value_at_stake": float(
                risk["rupee_value_at_stake"]
            )
        }
    }