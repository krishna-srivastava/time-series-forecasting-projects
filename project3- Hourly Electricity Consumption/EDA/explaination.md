# Electricity Demand Forecasting — EDA Summary

## Dataset Overview

This dataset contains **3 years of hourly electricity demand data** collected from a power grid.
Each row represents one hour, including the electricity demand at that time along with the corresponding weather conditions.

| Property | Value |
|---|---|
| Total Rows | 26,280 (Hourly × 3 Years) |
| Total Columns | 13 |
| Date Range | 2021-01-01 to 2023-12-31 |
| Frequency | Hourly |

**Target Variable:** `demand_MW` — Electricity demand measured in Megawatts (MW).

---

## Basic EDA Findings

### Missing Values

```
No missing values were found. ✅
The dataset is completely clean.
```

### Data Types

```
Float  : demand_MW, temperature, humidity, wind_speed, pressure, precipitation
Integer: holiday, weekend, hour, day_of_week, month
Object : datetime, season
```

### Unique Values

```
holiday      → 2   (0 = No, 1 = Yes)
weekend      → 2   (0 = Weekday, 1 = Weekend)
season       → 4   (Winter, Spring, Summer, Autumn)
day_of_week  → 7   (0 = Monday to 6 = Sunday)
month        → 12  (January to December)
hour         → 24  (0–23)
demand_MW    → 18,951 unique values (continuous target)
```

### Distribution Summary

```
Holiday Hours      : 648   (2.4% of data)
Non-Holiday Hours  : 25,632 (97.6%)

Weekend Hours      : 7,536  (28.6%)
Weekday Hours      : 18,744 (71.4%)

Season Distribution:
Spring  : 6,624 hours
Summer  : 6,624 hours
Autumn  : 6,552 hours
Winter  : 6,480 hours
```

---

# Demand Analysis

## Basic Statistics

| Metric | Value |
|---|---|
| Total Demand (3 Years) | 108,858,196 MW |
| Average Hourly Demand | 4,142 MW |
| Standard Deviation | 1,087 MW |
| Minimum Demand | 1,344 MW |
| Maximum Demand | 6,527 MW |

The electricity demand ranges from **1,344 MW to 6,527 MW**, indicating a nearly **five-fold difference** between the minimum and maximum values. This clearly demonstrates the significant impact of time and seasonality on electricity consumption.

---

## Demand Distribution

- The demand distribution is **slightly right-skewed**.
- Most hourly demand values fall between **3,500 MW and 5,000 MW**.
- Low demand is typically observed during nighttime, while peak demand occurs during evening hours.

---

# Trend Analysis

**Trend Slope:** **+0.0192 MW per hour**

```
2021 Average: 3,942 MW
2022 Average: 4,143 MW (+5.1%)
2023 Average: 4,340 MW (+4.8%)
```

A clear upward trend is observed over the three-year period.

Possible reasons include:

- Population growth
- Increased usage of electrical appliances
- Electric vehicle (EV) adoption
- Industrial expansion

> Unlike the Rossmann sales dataset, which showed almost no long-term trend, this dataset exhibits a consistent increase in electricity demand.

---

# Hourly Demand Pattern

| Hour | Average Demand | Explanation |
|---|---|---|
| 00–04 | ~2,200 MW | Most people are sleeping |
| 05–07 | ~3,000 MW | Morning activities begin |
| 08–11 | ~5,000 MW | Offices and industries start operating |
| 12–13 | ~4,500 MW | Slight decrease during lunch hours |
| 14–17 | ~4,800 MW | Afternoon working hours |
| 18–21 | ~5,500 MW | Evening peak demand |
| 22–23 | ~3,500 MW | Nighttime decline |

**Hour** is expected to be one of the most important predictive features because electricity demand changes dramatically throughout the day.

A clear **double-peak pattern** is observed:

- Morning Peak (08:00–11:00)
- Evening Peak (18:00–21:00)

---

# Weekly Pattern

| Day | Average Demand (MW) |
|---|---:|
| Monday | 4,209 |
| Tuesday | 4,216 |
| Wednesday | 4,217 |
| Thursday | 4,238 |
| Friday | 4,234 |
| Saturday | 3,941 |
| Sunday | 3,939 |

### Key Finding

```
Weekday Average : 4,223 MW
Weekend Average : 3,941 MW
Difference      : -282 MW (-6.7%)
```

Electricity demand is noticeably lower during weekends, mainly because industrial and commercial activities are reduced, while residential demand remains relatively stable.

---

# Monthly Pattern

| Month | Average Demand (MW) | Season |
|---|---:|---|
| January | 4,819 | Winter ❄️ |
| February | 4,835 | Winter ❄️ |
| March | 3,222 | Spring 🌸 |
| April | 3,229 | Spring 🌸 |
| May | 3,224 | Spring 🌸 |
| June | 5,007 | Summer ☀️ |
| July | 4,999 | Summer ☀️ |
| August | 5,000 | Summer ☀️ |
| September | 3,528 | Autumn 🍂 |
| October | 3,512 | Autumn 🍂 |
| November | 3,516 | Autumn 🍂 |
| December | 4,835 | Winter ❄️ |

A clear **U-shaped seasonal pattern** is visible.

```
Summer (Jun–Aug)  → Highest Demand (~5,000 MW)
Winter (Dec–Feb)  → High Demand (~4,830 MW)
Spring (Mar–May)  → Lowest Demand (~3,225 MW)
Autumn (Sep–Nov)  → Moderate Demand (~3,519 MW)
```

---

# Seasonal Pattern

| Season | Average Demand (MW) | Rank |
|---|---:|---|
| Summer | 5,002 | 🥇 Highest |
| Winter | 4,830 | 🥈 Second |
| Autumn | 3,518 | 🥉 Third |
| Spring | 3,225 | 4th |

The difference between **Summer and Spring** is approximately **1,777 MW**, representing nearly **55% higher electricity demand** during the summer season.

---

# Holiday & Weekend Effect

## Holiday Effect

```
Non-Holiday Average : 4,146 MW
Holiday Average     : 3,991 MW
Difference          : -155 MW (-3.7%)
```

Electricity demand is slightly lower during holidays because commercial and industrial activities decrease.

---

## Weekend Effect

```
Weekday Average : 4,223 MW
Weekend Average : 3,940 MW
Difference      : -283 MW (-6.7%)
```

The weekend effect is stronger than the holiday effect, primarily due to reduced industrial and office operations.

---

# Correlation Analysis

| Feature Pair | Correlation | Interpretation |
|---|---:|---|
| demand_MW ↔ temperature | +0.23 | Higher temperatures increase electricity demand (air conditioning usage). |
| demand_MW ↔ humidity | -0.04 | Negligible relationship. |
| demand_MW ↔ wind_speed | -0.01 | Almost no relationship. |
| demand_MW ↔ pressure | -0.01 | Almost no relationship. |
| demand_MW ↔ precipitation | -0.00 | No significant relationship. |
| demand_MW ↔ holiday | -0.02 | Slight reduction in demand during holidays. |
| temperature ↔ humidity | -0.59 | Strong negative relationship (physically expected). |

### Important Observation

```
Most weather variables show very weak direct correlations with electricity demand.

The primary drivers of demand are:

- Hour
- Day of Week
- Month
- Season

Temperature provides some useful predictive information because it reflects air-conditioning and heating usage.

Other weather variables such as humidity, wind speed, pressure, and precipitation contribute very little.
```

---

# Key Takeaways

1. **Hour** is expected to be the most important feature, with demand ranging from approximately **2,000 MW at night** to **5,500 MW during evening peak hours**.

2. The dataset exhibits a **clear upward trend**, with electricity demand increasing by roughly **10% between 2021 and 2023**.

3. **Summer and Winter** are the highest-demand seasons, while **Spring** has the lowest electricity consumption.

4. Electricity demand decreases by approximately **6.7% on weekends**, reflecting reduced industrial and commercial activity.

5. Weather variables generally have **weak direct correlations** with demand, while **time-based features** provide much stronger predictive signals.

6. The dataset contains **no missing values**, making it suitable for immediate feature engineering and model development.

7. The wide demand range (**1,344 MW to 6,527 MW**) indicates substantial variability that forecasting models must accurately capture.