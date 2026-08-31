# FORESIGHT
## Demand Forecasting & Inventory Risk Intelligence Platform

FORESIGHT is an end-to-end demand forecasting and inventory-risk decision-support platform for a life appliances and furniture business.

The system combines historical demand, inventory information, SKU attributes, calendar features, forecasting models, risk scoring, interactive dashboards, and a deployed API to convert demand forecasts into actionable inventory decisions.

---

## 1. Business Objective

The objective of FORESIGHT is to help Operations and Finance teams:

- Forecast SKU-level demand for the next 8 weeks.
- Identify products at risk of stockout.
- Identify products at risk of overstock.
- Recommend replenishment or markdown actions.
- Quantify inventory exposure in rupee terms.
- Provide decision support through interactive dashboards.
- Expose SKU-level forecast and risk results through a public API.

---

## 2. Project Architecture

```text
Historical Data
      │
      ▼
Data Preparation
      │
      ▼
Feature Engineering
      │
      ▼
Demand Forecasting
      │
      ├──────────────► Rolling Backtest
      │
      ▼
Final Forecast
      │
      ▼
Inventory Risk Scoring
      │
      ├──────────────► Streamlit Dashboards
      │
      └──────────────► FastAPI Scoring Service
                              │
                              ▼
                       Public API Deployment

```

---
## Live Demo & API

### Public FastAPI Scoring Service

- [FORESIGHT Scoring API](https://foresight-w1p0.onrender.com)
- [Interactive Swagger Documentation](https://foresight-w1p0.onrender.com/docs)
- [API Health Check](https://foresight-w1p0.onrender.com/health)
- [Example SKU — SKU079](https://foresight-w1p0.onrender.com/score/SKU079)


---

## 3. Dataset

The current processed demand dataset contains:

- 13,856 weekly demand observations
- 100 SKUs
- 20 variables
- Demand coverage from 2020-12-28 to 2025-12-29
- 6,379,938 total recorded demand units

Data-quality checks found:

- 0 missing values in `weekly_demand.csv`
- 0 duplicate rows in `weekly_demand.csv`
- 0 duplicate rows in `sku_master.csv`


---

## 4. Key Demand Insights

### Demand Trend

Annual demand increased continuously from 2021 through 2025:

| Year |   Demand  |
|------|----------:|
| 2021 |  354,139  |
| 2022 |  850,140  |
| 2023 | 1,312,874 |
| 2024 | 1,748,977 |
| 2025 | 2,113,640 |

The growth rate moderated over time:

- 2022: +140.06%
- 2023: +54.43%
- 2024: +33.22%
- 2025: +20.85%

Demand is therefore showing strong long-term growth, while the annual growth rate is moderating.

### Seasonality

Demand shows stronger activity toward the latter part of the year.

|   Month   |  Demand  |
|-----------|---------:|
| October   |  707,711 |
| December  |  651,604 |
| September |  578,770 |
| August    |  555,416 |
| November  |  553,601 |

October recorded the highest monthly demand.

### Category Demand

|        Category      |   Demand  |
|----------------------|----------:|
| Storage & Organizers | 2,278,094 |
| Appliances           | 1,685,843 |
| Furniture            | 1,180,907 |
| Home Decor           |  790,850  |
| Cookware & Tableware |  444,244  |

Storage & Organizers is the largest demand category.

### Top Demand SKU

The highest-demand SKU is:

**SKU019 — Laundry Hamper: 136,407 units**

Other high-volume products include Document Storage Box, LED Television, Magazine Holder, Desktop Organizer, Bathroom Shower Caddy, and Sound System.

### Slow-Mover Candidates

The lowest-demand SKU is:

**SKU079 — Jute Rug: 788 units**

Low historical demand should be treated as a screening signal rather than confirmed dead stock. Inventory ageing and other business information should also be considered.

---

## 5. Forecasting & Model Performance

FORESIGHT produces an 8-week SKU-level demand forecast.

Forecast outputs include:

- Weekly demand forecast
- Forecast method
- Forecast confidence

The forecasting pipeline also includes fallback logic for cases where the primary forecasting approach is not appropriate.

### Rolling Backtest

Forecast performance was evaluated using 13 rolling backtest windows.

| Metric | ML Forecast | Naive Baseline |
|--------|------------:|---------------:|
|  WAPE  |    4.45%    |      6.28%     |

The ML forecasting approach achieved approximately **29.1% relative improvement in WAPE** compared with the naive baseline.

Across the rolling windows, ML WAPE ranged approximately from **4.00% to 4.77%**.

### Interpretation

The backtest results indicate that the ML forecasting approach consistently outperformed the naive baseline across the evaluated test windows.

Forecast confidence and forecast method are retained in the final forecast outputs so that downstream inventory decisions can consider the reliability of each forecast.

---

## 6. Inventory Risk Scoring

The risk-scoring layer combines forecast and inventory information to classify SKU-level inventory risk and recommend business actions.

### Recommended Actions

| Recommended Action | SKUs |
|--------------------|-----:|
| Healthy            |  40  |
| Reorder now        |  36  |
| Markdown / clear   |  24  |

### Stockout Risk

| Stockout Risk | SKUs |
|---------------|-----:|
|      Low      |  64  |
|      High     |  36  |

### Overstock Risk

| Overstock Risk | SKUs |
|----------------|-----:|
|       Low      |  76  |
|      High      |  24  |

### Risk Outputs

The scoring layer provides:

- Latest inventory
- 8-week forecast demand
- Forecast method
- Forecast confidence
- Coverage ratio
- Stockout risk
- Overstock risk
- Recommended action
- Unit cost
- Units at risk
- Rupee value at stake

### Business Interpretation

The portfolio contains both shortage and excess-inventory pressure.

- **36 SKUs** are classified as `Reorder now`.
- **24 SKUs** are classified as `Markdown / clear`.
- **40 SKUs** are currently classified as `Healthy`.

This allows Operations and Finance teams to prioritize replenishment, inventory reduction, and working-capital decisions at SKU level.

---

## 7. Dashboard & API

### Streamlit Dashboard

FORESIGHT includes six interactive Streamlit pages:

1. Sales Analytics
2. Forecast
3. Inventory Risk
4. Risk Dashboard
5. Product Details
6. Executive Summary

The dashboards provide:

- KPI monitoring
- Historical demand analysis
- Forecast visualization
- Inventory-risk analysis
- SKU-level investigation
- Executive-level summaries
- Recommended business actions

### FastAPI Scoring Service

The project also provides a deployed FastAPI scoring service for SKU-level forecast and inventory-risk results.

#### Main Endpoints
```text
GET /
GET /health
GET /score/{sku_id}
```

## 8. Technology Stack

### Programming & Data

- Python
- Pandas
- NumPy
- Scikit-learn

### Forecasting & Analytics

- Machine-learning forecasting
- Feature engineering
- Rolling backtesting
- Forecast fallback logic
- Inventory risk scoring

### Visualization & Applications

- Streamlit
- FastAPI
- Swagger / OpenAPI

### Deployment & Version Control

- Render
- Git
- GitHub

### Data Outputs

The project generates processed datasets and analytical outputs including:

- Weekly demand data
- Feature-engineered data
- Final forecasts
- Fallback forecasts
- Inventory data
- Risk-scoring results
- Rolling backtest results

---

## 9. Project Structure

```text
FORESIGHT/
│
├── app/
│   ├── api/
│   │   └── main.py
│   │
│   ├── pages/
│   │   ├── 1_Sales_Analytics.py
│   │   ├── 2_Forecast.py
│   │   ├── 3_Inventory_Risk.py
│   │   ├── 4_Risk_Dashboard.py
│   │   ├── 5_Product_Details.py
│   │   └── 6_Executive_Summary.py
│   │
│   └── app.py
│
├── data/
│   ├── processed/
│   └── raw/
│
├── notebooks/
│
├── reports/
│   ├── D2_EDA_Data_Quality_Memo.md
│   └── FORESIGHT_Executive_Readout.pptx
│
├── src/
│   ├── combine_forecast.py
│   ├── fallback_forecast.py
│   ├── feature_engineering.py
│   ├── final_forecast.py
│   ├── generate_calendar.py
│   ├── generate_inventory.py
│   ├── generate_sales_daily.py
│   ├── generate_sku_master
│   ├── generate_sku_master_less.py
│   ├── generate_store_master.py
│   ├── inspect_data.py
│   ├── model_preparation.py
│   ├── risk_scoring.py
│   └── rolling_backtest.py
│
├── .gitignore
├── README.md
└── requirements.txt

```

### Main Components

|       Component    |                  Purpose                          |
|--------------------|---------------------------------------------------|
| `app/`             | Streamlit application and FastAPI service         |
| `app/pages/`       | Interactive business dashboards                   |
| `src/`             | Data preparation, forecasting, validation, and risk-scoring pipeline |
| `data/`            | Raw and processed datasets                        |  
| `reports/`         | Project reports and executive deliverables        |
| `requirements.txt` | Python dependencies                               |
| `.gitignore`       | Files excluded from version control               |