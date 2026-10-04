# India CPI Inflation Analysis (2013–2023)

Analysis of All-India Consumer Price Index (CPI) data to uncover inflation trends,
category-wise drivers, COVID-19 impact, and the relationship between global crude
oil prices and domestic inflation.

Originally built in Excel (pivot tables, formulas, charts); this repo re-implements
the same analysis in Python/pandas for portability and reproducibility.

## Dataset
- Source: All India CPI Index (Ministry of Statistics and Programme Implementation, GOI)
- Coverage: Jan 2013 – May 2023, Rural / Urban / Rural+Urban, 29 CPI sub-categories

## Key Questions Answered
1. **Category contribution** — which broader category (Food, Health, Transport, etc.)
   contributes most to the latest month's CPI basket
2. **YoY inflation trend (2017+)** — identifying 2022 as the peak inflation year,
   driven by the Russia-Ukraine war's impact on global commodity prices
3. **Food inflation deep-dive** — month-on-month trend + which individual
   sub-category (e.g. Spices) drove food inflation most
4. **COVID-19 impact** — comparing pre/post-lockdown inflation for Health,
   Food, and Essential Services (Housing + Fuel)
5. **Oil price correlation** — testing whether global crude oil price changes
   correlate with domestic CPI categories, including a lagged-correlation test
   (fuel/transport costs respond ~1 month after oil price moves, not immediately)

## Project Structure
```
cpi_project/
├── cpi_analysis.py      # main analysis functions (Q1-Q5)
├── All_India_CPI.csv    # source dataset (not included - add your own)
└── README.md
```

## Requirements
```
pandas
```

## Usage
```bash
python cpi_analysis.py
```

## Notes
- Food and Clothing+Footwear buckets are built from their raw sub-items
  (not the pre-aggregated CPI columns) for methodological consistency.
- Oil price data (Indian Basket Crude Oil, $/barrel) sourced separately from
  PPAC (Petroleum Planning & Analysis Cell, Govt of India) — not part of the
  original CPI dataset.
