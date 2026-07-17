# Rossmann Store Sales — Exploratory Data Analysis (EDA)

## Dataset Overview

Rossmann is one of the largest pharmacy retail chains in Germany, operating **1,115 stores**.  
This dataset contains **daily sales records** from **January 2013 to April 2015**.

| Property | Value |
|----------|-------|
| Total Rows | 911,284 |
| Total Columns | 9 |
| Date Range | 2013-01-01 to 2015-04-27 |
| Total Stores | 1,115 |

### Features

| Column | Description |
|---------|-------------|
| **Store** | Unique store identifier |
| **DayOfWeek** | Day number (1 = Monday, 7 = Sunday) *(Dropped because it can be derived from Date)* |
| **Date** | Daily transaction date |
| **Sales** | Daily sales amount (Target Variable) |
| **Customers** | Number of customers visiting the store |
| **Open** | Store status (1 = Open, 0 = Closed) |
| **Promo** | Promotion running (1 = Yes, 0 = No) |
| **StateHoliday** | State holiday type (0 = None, a = Public Holiday, b = Easter Holiday, c = Christmas) |
| **SchoolHoliday** | School holiday indicator (1 = Yes, 0 = No) |

---

# Data Cleaning

## Missing Values

The dataset contains **no missing values**, making it a clean dataset for analysis.

---

## StateHoliday Data Type Issue

The **StateHoliday** column contained mixed data types. Some values were stored as integers (`0`), while others were stored as strings (`"0"`), causing duplicate categories.

### Before Cleaning

| Value | Count |
|------|------:|
| 0 (string) | 818,809 |
| 0 (integer) | 65,536 |
| a | 16,149 |
| b | 6,690 |
| c | 4,100 |

### After Cleaning

| Value | Count |
|------|------:|
| 0 | 884,345 |
| a | 16,149 |
| b | 6,690 |
| c | 4,100 |

The issue was resolved by converting the column into a consistent string data type.

```python
df["StateHoliday"] = df["StateHoliday"].astype(str)
```

---

## Removing Redundant Feature

The **DayOfWeek** column was removed because the same information can be extracted directly from the **Date** column.

---

## Closed Stores

Rows where **Open = 0** have **Sales = 0**.

These records will be excluded during model training because they do not represent actual customer purchasing behavior and may negatively affect forecasting performance.

---

# Sales Analysis

## Sales Statistics

| Metric | Value |
|---------|--------|
| Total Sales | ~1 Billion+ |
| Average Daily Sales | ~5,774 |
| Standard Deviation | ~3,849 |
| Maximum Sales | 41,551 |
| Minimum Sales | 0 (Closed Store) |

---

## Sales Distribution

The sales distribution is **positively (right) skewed**.

Observations:

- Most stores generate daily sales between **4,000–7,000**.
- A small number of stores generate exceptionally high sales (outliers).
- Zero-sales observations correspond to closed stores.

---

## Store Performance

A significant difference exists between the highest-performing and lowest-performing stores.

This variation is expected because stores differ in:

- Location
- Store size
- Customer demand
- Market conditions

---

## Overall Sales Trend

The estimated trend slope is approximately **-0.0008**, which is practically zero.

This indicates that Rossmann maintained relatively stable sales during the observed period.

Rather than long-term growth, the dataset is mainly influenced by:

- Weekly seasonality
- Monthly seasonality
- Promotions
- Holidays

---

# Time-Based Analysis

## Weekly Sales Pattern

Sales follow a clear weekly pattern.

- Monday–Friday: Stable sales
- Saturday: Highest sales
- Sunday: Lowest (or zero) sales because most stores remain closed

**Business Insight**

Sunday should be treated separately while building forecasting models because it follows a completely different sales pattern.

---

## Monthly Sales Pattern

Seasonality is clearly visible.

- December shows the highest sales due to Christmas shopping.
- January and February record the lowest sales because of the post-holiday slowdown.
- July and August experience a moderate seasonal increase.

---

## Yearly Comparison

Sales remain relatively consistent across 2013, 2014, and 2015.

No significant year-over-year growth is observed, indicating that Rossmann operates as a mature retail business.

---

## Weekend vs Weekday

Average weekend sales are higher than weekday sales.

Higher customer traffic during weekends directly contributes to increased revenue.

---

# Promotion Analysis

## Promotion Impact

Promotion is one of the strongest business drivers in the dataset.

| | No Promotion | Promotion |
|---|-------------:|----------:|
| Average Sales | ~4,500 | ~7,000+ |

Stores running promotions generate approximately **55% higher average sales** compared to stores without promotions.

---

## Promotion by Day

Promotion effectiveness varies across the week.

- Weekdays experience the largest increase.
- Saturdays already have naturally high traffic.
- Sundays show almost no promotion impact because most stores are closed.

---

## Promotion During Holidays

Promotions performed best on regular business days.

Holiday promotions showed mixed performance depending on the holiday type.

---

# Holiday Analysis

## State Holiday Impact

| Holiday Type | Description | Sales Impact |
|--------------|-------------|--------------|
| 0 | No Holiday | Normal sales |
| a | Public Holiday | Lower sales |
| b | Easter Holiday | Moderate effect |
| c | Christmas | High sales before the holiday, lower sales on the holiday itself |

Overall, holidays reduce average sales because many stores operate with limited hours or remain closed.

However, sales usually increase significantly just before major holidays.

---

## School Holiday Impact

Sales increase slightly during school holidays.

Families tend to spend more time shopping during vacation periods, although the effect is much weaker than promotional campaigns.

---

# Customer Analysis

## Customer Statistics

| Metric | Value |
|---------|--------|
| Average Customers | ~633 |
| Maximum Customers | 7,388 |
| Minimum Customers | 0 |

---

## Customer Distribution

Customer counts also follow a right-skewed distribution.

Only a small number of stores attract exceptionally high daily customer traffic.

---

## Store Performance

Stores with the highest customer traffic are generally the same stores that generate the highest revenue.

This indicates a strong relationship between customer volume and sales.

---

## Weekly Customer Pattern

Customer traffic closely follows the sales trend.

- Saturday has the highest footfall.
- Sunday records the lowest footfall.
- Weekdays remain relatively consistent.

---

## Monthly Customer Pattern

Customer seasonality closely matches sales seasonality.

- December has the highest customer traffic.
- January experiences a noticeable decline after the holiday season.

---

## Promotion Impact on Customers

Promotions attract significantly more customers.

This indicates that promotions function not only as a revenue driver but also as a customer acquisition strategy.

---

# Sales vs Customers Relationship

The correlation between Sales and Customers is approximately:

```
0.82
```

This represents a **very strong positive relationship**.

Key observations:

- Higher customer traffic generally leads to higher sales.
- Average revenue per customer is approximately **9.5**.
- Some stores have high customer traffic but lower spending per customer.
- Other stores attract fewer customers but achieve higher revenue per customer.

**Machine Learning Insight**

Although **Customers** is a highly predictive feature, future customer counts are unavailable during forecasting.

Therefore, customer-related lag features should be created instead of directly using future customer values.

---

# Correlation Summary

| Feature Pair | Correlation | Interpretation |
|--------------|------------:|---------------|
| Sales ↔ Customers | ~0.82 | Very Strong Positive |
| Sales ↔ Promo | ~0.36 | Moderate Positive |
| Sales ↔ Open | ~0.27 | Positive |
| Sales ↔ SchoolHoliday | ~0.05 | Weak Positive |
| Customers ↔ Promo | ~0.28 | Moderate Positive |

---

# Key Findings

### 1. Promotions are the strongest business driver.

Stores running promotions achieve approximately **55% higher sales**, making **Promo** one of the most important predictive features.

---

### 2. Sales and Customers are strongly correlated.

Customer count has a correlation of approximately **0.82** with sales.

However, future customer counts are unknown, so lag-based customer features should be used during forecasting.

---

### 3. Long-term sales remain stable.

Rossmann exhibits little long-term growth.

Most variation is explained by promotions and seasonality rather than trend.

---

### 4. Strong seasonal behavior exists.

December consistently records the highest sales, while January experiences the lowest.

---

### 5. Weekly seasonality is significant.

Saturday produces the highest revenue, whereas Sunday contributes almost no sales due to store closures.

---

### 6. Store performance varies considerably.

Individual stores perform very differently, suggesting that store-specific modeling may improve forecasting accuracy.

---

### 7. Closed-store records should be excluded during modeling.

Rows with **Open = 0** always have **Sales = 0** and do not represent actual purchasing behavior.

---
