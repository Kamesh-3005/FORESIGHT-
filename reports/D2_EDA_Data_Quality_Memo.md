# FORESIGHT — D2 EDA & Data-Quality Memo

## 1. Objective

This memo summarizes the exploratory data analysis, data-quality checks, demand patterns, and inventory-risk findings supporting the FORESIGHT demand forecasting and inventory-risk platform.

The analysis uses the processed project datasets currently available in `data/processed/`.

---

## 2. Data Overview

### Dataset summary

|       Dataset     |  Rows  | Columns |
|-------------------|-------:|--------:|
| weekly_demand.csv | 13,856 |    20   |
|   sku_master.csv  |   100  |    6    |
| risk_scoring.csv  |   100  |   14    |

The weekly demand dataset covers:

**2020-12-28 to 2025-12-29**

Total recorded demand:

**6,379,938 units**

---

## 3. Data Quality Assessment

The following checks were performed on the processed datasets:

- `weekly_demand.csv` contains **0 missing values**.
- `weekly_demand.csv` contains **0 duplicate rows**.
- `sku_master.csv` contains **0 duplicate rows**.
- The weekly demand dataset contains **13,856 observations** across **100 SKUs**.

### Data-quality conclusion

The checked processed datasets are structurally clean for the tested conditions. No missing values were found in the weekly demand dataset, and no duplicate records were found in the weekly demand or SKU master datasets.

---

## 4. Demand Trend

Annual demand increased continuously from 2021 through 2025.

| Year  |   Demand  |
|-------|----------:|
| 2020* |    168    |
| 2021  |  354,139  |
| 2022  |  850,140  |
| 2023  | 1,312,874 |
| 2024  | 1,748,977 |
| 2025  | 2,113,640 |

\* 2020 is a partial year because the dataset begins on 2020-12-28.

Annual growth moderated over time:

| Year | YoY change |
|------|-----------:|
| 2022 |  +140.06%  |
| 2023 |  +54.43%   |
| 2024 |   +33.22%  |
| 2025 |   +20.85%  |

### Insight

Demand is showing strong long-term growth, reaching approximately **2.11 million units in 2025**. However, the rate of annual growth is moderating, which should be considered when planning future demand expectations.

---

## 5. Seasonality

Monthly demand shows stronger demand concentration toward the latter part of the year.

|   Month  |  Demand |
|----------|--------:|
|  October | 707,711 |
| December | 651,604 |
| September| 578,770 |
| August   | 555,416 |
| November | 553,601 |

The lowest monthly totals were:

|    Month |  Demand |
|----------|--------:|
| February | 417,607 |
|  January | 464,790 |
|   April  | 465,218 |

Average demand was also highest around weeks 42–44 and week 52.

### Insight

The data shows an observed **late-year demand concentration**, particularly from August through December, with October having the highest monthly demand.

This seasonal pattern supports the use of time-based features in the forecasting pipeline.

---

## 6. Demand by Category

|     Category           | Total demand |
|------------------------|-------------:|
|  Storage & Organizers  |   2,278,094  |
|       Appliances       |   1,685,843  |
|       Furniture        |   1,180,907  |
|       Home Decor       |    790,850   |
|  Cookware & Tableware  |   444,244    |

### Insight

**Storage & Organizers** is the largest demand category with approximately **2.28 million units**, followed by Appliances and Furniture.

These high-volume categories should receive particular attention during forecasting and inventory planning because forecasting errors in high-volume categories can have larger operational consequences.

---

## 7. Top Demand Movers

|  SKU   |           Product               |  Demand |
|--------|---------------------------------|--------:|
| SKU019 | Laundry Hamper                  | 136,407 |
| SKU029 | Document Storage Box            | 127,443 |
| SKU053 | LED Television                  | 126,810 |
| SKU026 | Magazine Holder                 | 125,501 |
| SKU025 | Desktop Organizer               | 124,759 |
| SKU023 | Bathroom Shower Caddy           | 124,080 |
| SKU056 | Sound System                    | 123,939 |
| SKU027 | File Organizer                  | 122,978 |
| SKU047 | Fully Automatic Washing Machine | 122,643 |
| SKU046 | Semi-Automatic Washing Machine  | 121,196 |

### Insight

The highest-volume SKUs are concentrated mainly in Storage & Organizers and Appliances. These products are important candidates for close forecast and replenishment monitoring.

---

## 8. Lowest-Demand SKUs / Slow-Mover Candidates

|  SKU   |        Product        | Demand |
|--------|-----------------------|-------:|
| SKU079 | Jute Rug              |   788  |
| SKU062 | Double Bed            |  1,449 |
| SKU016 | Food Storage Canister |  1,818 |
| SKU100 | Serving Spoon         |  2,256 |
| SKU084 | Cotton Door Curtain   |  2,778 |
| SKU088 | Bamboo Wind Chime     |  3,911 |
| SKU096 | Thali                 |  4,625 |
| SKU071 | Study Table           |  5,147 |
| SKU008 | 5-Tier Shoe Rack      | 11,494 |
| SKU028 | Drawer Divider        | 11,594 |

### Insight

SKU079 (Jute Rug) has the lowest recorded demand at **788 units**.

Low historical demand can be used as a slow-mover screening signal. However, low demand alone should not be interpreted as confirmed dead stock. Inventory ageing, time since last sale, and current inventory should also be considered.

---

## 9. Inventory Risk Distribution

### Recommended actions

| Recommended Action | SKUs |
|--------------------|-----:|
| Healthy            |  40  |
| Reorder now        |  36  |
| Markdown / clear   |  24  |

### Stockout risk

| Risk | SKUs |
|------|-----:|
| nLow |  64  |
| High |  36  |

### Overstock risk

| Risk | SKUs |
|------|-----:|
|  Low |  76  |
| High |  24  |

### Insight

The inventory portfolio has risks in both directions:

- **36 SKUs require immediate reorder action.**
- **24 SKUs are candidates for markdown / clearance.**
- **40 SKUs are currently classified as healthy.**

This indicates that the business needs to balance service-level protection against excess inventory and working-capital exposure.

---

## 10. Key Business Insights

### 1. Demand is growing

Demand reached approximately **2.11 million units in 2025**, continuing a multi-year upward trend, although the annual growth rate is moderating.

### 2. Demand is concentrated toward the end of the year

August–December shows relatively strong demand, with **October recording the highest monthly demand at 707,711 units**.

### 3. Inventory risk is two-sided

The portfolio contains both shortage and excess-inventory problems: **36% of SKUs require reorder action while 24% require markdown/clearance action**.

### 4. High-volume categories deserve priority

Storage & Organizers is the largest category at **2,278,094 units**, making it an important category for forecast accuracy and inventory planning.

### 5. Slow movers require targeted investigation

SKU079 (Jute Rug) has only **788 units** of historical demand and should be investigated for inventory ageing and potential clearance exposure.

---

## 11. Limitations

The current analysis supports data-quality checks, demand ranking, category comparison, trend analysis, observed seasonal patterns, and inventory-risk distribution.

The current analysis does not independently quantify:

- confirmed dead-stock ageing,
- promotion uplift,
- causal holiday effects,
- or causal drivers of the observed demand trend.

These should not be interpreted beyond the evidence available in the processed datasets.

---

## 12. Conclusion

FORESIGHT identifies a growing demand environment combined with meaningful inventory imbalance.

The most important management priorities are:

1. Protect high-volume products from stockouts.
2. Prioritize replenishment for the 36 SKUs classified as **Reorder now**.
3. Address the 24 SKUs classified as **Markdown / clear**.
4. Closely monitor high-volume categories, particularly Storage & Organizers and Appliances.
5. Use the forecasting and risk-scoring outputs as decision-support tools rather than replacing business judgment.

The findings provide the analytical foundation for the FORESIGHT forecasting, inventory-risk dashboard, and deployed scoring API.