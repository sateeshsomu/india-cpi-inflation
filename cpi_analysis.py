"""
India CPI Inflation Case Study (2013–2023)
--------------------------------------------
Replicates the Excel-based analysis in Python/pandas:
  Q1 - Broader category contribution to latest month's CPI
  Q2 - YoY inflation trend since 2017
  Q3 - Food bucket MoM trend + biggest sub-category contributor
  Q4 - Pre/Post COVID inflation comparison
  Q5 - Correlation between oil price changes and CPI categories (with lag)

Data: All India CPI Index (MOSPI), Rural/Urban/Rural+Urban, Jan 2013–May 2023
"""

import pandas as pd

# ---------------------------------------------------------
# Load & clean data
# ---------------------------------------------------------
df = pd.read_csv("All_India_CPI.csv")

# fix known data quality issues
df["Month"] = df["Month"].str.strip().replace({"Marcrh": "March"})
MONTH_ORDER = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
df["MonthNum"] = df["Month"].map(lambda m: MONTH_ORDER.index(m) + 1)

ru = df[df["Sector"] == "Rural+Urban"].sort_values(["Year", "MonthNum"]).reset_index(drop=True)

# NOTE: the raw MOSPI file has a few genuine gaps (e.g. May 2020 fully missing,
# April 2019 missing entirely). In the real project these were imputed in Excel
# using a moving-average fill before this stage. Doing the same here so the
# demo numbers line up with the original analysis.
NUMERIC_COLS = [c for c in ru.columns if c not in ("Sector", "Year", "Month", "MonthNum")]
ru[NUMERIC_COLS] = ru[NUMERIC_COLS].apply(pd.to_numeric, errors="coerce")
ru[NUMERIC_COLS] = ru[NUMERIC_COLS].interpolate(limit_direction="both")

FOOD_SUBS = ["Cereals and products", "Meat and fish", "Egg", "Milk and products",
             "Oils and fats", "Fruits", "Vegetables", "Pulses and products",
             "Sugar and Confectionery", "Spices", "Non-alcoholic beverages",
             "Prepared meals, snacks, sweets etc."]

CLOTHING_SUBS = ["Clothing", "Footwear"]

# build buckets from raw sub-items (not the pre-aggregated columns)
ru["Food Bucket"] = ru[FOOD_SUBS].mean(axis=1)
ru["Clothing Bucket"] = ru[CLOTHING_SUBS].mean(axis=1)

OTHER_BUCKETS = ["Pan, tobacco and intoxicants", "Housing", "Fuel and light",
                 "Household goods and services", "Health", "Transport and communication",
                 "Recreation and amusement", "Education", "Personal care and effects",
                 "Miscellaneous"]

BUCKETS = ["Food Bucket", "Clothing Bucket"] + OTHER_BUCKETS


# ---------------------------------------------------------
# Q1: Contribution of each bucket to latest month's CPI
# ---------------------------------------------------------
def bucket_contribution(data: pd.DataFrame, year: int, month: str) -> pd.Series:
    row = data[(data.Year == year) & (data.Month == month)].iloc[0]
    values = row[BUCKETS].astype(float)
    return (values / values.sum() * 100).sort_values(ascending=False)


# ---------------------------------------------------------
# Q2: Year-on-Year inflation trend (General index)
# ---------------------------------------------------------
def yoy_trend(data: pd.DataFrame, start_year: int = 2017) -> pd.DataFrame:
    d = data.copy()
    d["YoY_%"] = d.groupby("MonthNum")["General index"].pct_change() * 100
    return d[d.Year >= start_year][["Year", "Month", "YoY_%"]]


# ---------------------------------------------------------
# Q3: Food bucket MoM trend + biggest sub-category mover
# ---------------------------------------------------------
def food_mom_trend(data: pd.DataFrame, start=(2022, 6), end=(2023, 5)) -> pd.DataFrame:
    mask = ((data.Year == start[0]) & (data.MonthNum >= start[1] - 1)) | \
           ((data.Year == end[0]) & (data.MonthNum <= end[1]))
    period = data[mask].copy()
    period["Food_MoM_%"] = period["Food Bucket"].pct_change() * 100
    return period[["Year", "Month", "Food Bucket", "Food_MoM_%"]]


def biggest_food_contributor(data: pd.DataFrame, start_ym=(2022, 5), end_ym=(2023, 5)) -> pd.Series:
    start = data[(data.Year == start_ym[0]) & (data.MonthNum == start_ym[1])][FOOD_SUBS].iloc[0]
    end = data[(data.Year == end_ym[0]) & (data.MonthNum == end_ym[1])][FOOD_SUBS].iloc[0]
    return (end.astype(float) - start.astype(float)).sort_values(ascending=False)


# ---------------------------------------------------------
# Q4: Pre vs Post COVID average MoM inflation
# ---------------------------------------------------------
def covid_impact(data: pd.DataFrame) -> pd.DataFrame:
    d = data.copy()
    d["Essential"] = d[["Housing", "Fuel and light"]].mean(axis=1)
    for col in ["General index", "Health", "Food Bucket", "Essential"]:
        d[col + "_MoM"] = d[col].astype(float).pct_change() * 100

    pre = d[((d.Year == 2019) & (d.MonthNum >= 3)) | ((d.Year == 2020) & (d.MonthNum <= 2))]
    post = d[((d.Year == 2020) & (d.MonthNum >= 4)) | ((d.Year == 2021) & (d.MonthNum <= 3))]

    summary = pd.DataFrame({
        "Pre_COVID_avg_MoM": [pre[c + "_MoM"].mean() for c in ["General index", "Health", "Food Bucket", "Essential"]],
        "Post_COVID_avg_MoM": [post[c + "_MoM"].mean() for c in ["General index", "Health", "Food Bucket", "Essential"]],
    }, index=["General index", "Health", "Food Bucket", "Essential Services"])
    return summary


# ---------------------------------------------------------
# Q5: Oil price correlation (with lag)
# ---------------------------------------------------------
def oil_correlation(data: pd.DataFrame, oil_prices: pd.Series, categories: list, max_lag: int = 3) -> pd.DataFrame:
    """
    oil_prices: pd.Series of monthly Indian Basket Crude Oil $/barrel,
                indexed same order as `data` rows for the test window.
    """
    oil_mom = oil_prices.pct_change() * 100
    results = {}
    for cat in categories:
        cat_mom = data[cat].astype(float).pct_change() * 100
        results[cat] = {
            f"lag_{lag}": oil_mom.corr(cat_mom.shift(-lag)) for lag in range(max_lag + 1)
        }
    return pd.DataFrame(results).T.sort_values("lag_1", ascending=False)


if __name__ == "__main__":
    print("Q1 - Bucket contribution (latest month):")
    print(bucket_contribution(ru, 2023, "May"), "\n")

    print("Q2 - YoY inflation trend (2017+), yearly average:")
    yoy = yoy_trend(ru)
    print(yoy.groupby("Year")["YoY_%"].mean(), "\n")

    print("Q3 - Food MoM trend (Jun'22-May'23):")
    print(food_mom_trend(ru), "\n")
    print("Q3 - Biggest food sub-category contributor (May'22-May'23):")
    print(biggest_food_contributor(ru), "\n")

    print("Q4 - Pre vs Post COVID avg MoM inflation:")
    print(covid_impact(ru), "\n")

    print("Q5 - Oil price correlation: see oil_correlation() — requires external oil price series")
