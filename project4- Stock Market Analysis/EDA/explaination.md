# TCS Stock Data — EDA & Analysis Explanation

## Project Overview

This project is based on **15 years of daily stock price data (2010–2024)** for **Tata Consultancy Services (TCS)**. The project is divided into two notebooks:

1. **Basic-Eda.ipynb** — Understanding the dataset, data cleaning, and initial exploration.
2. **analysis.ipynb** — In-depth analysis, trend identification, feature engineering, and visualization.

---

# Dataset Information

```
File Name : TCS_stock_data.csv
Rows      : 3,850
Columns   : 6 (Date, Open, High, Low, Close, Volume)
Date Range: 2010-01-01 to 2024-12-31 (~15 Years)
Missing Values: 0 (Clean Dataset)
Memory Usage: 0.18 MB
```

### Column Description

| Column | Description |
|--------|-------------|
| Date | Trading date |
| Open | Opening stock price |
| High | Highest price of the day |
| Low | Lowest price of the day |
| Close | Closing stock price |
| Volume | Number of shares traded |

---

# Part 1 — Basic-Eda.ipynb (Understanding the Data)

## Step 1: Load & Preprocess

```python
df = pd.read_csv('../Data/TCS_stock_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
```

The **Date** column was converted from string format into a proper datetime format, which is the foundation of any time series project.

---

## Step 2: Basic Dataset Checks

```
✓ 3,850 rows and 6 columns
✓ Approximately 15 years of historical data
✓ 0 Missing Values
✓ Correct Data Types
```

Although the dataset spans approximately **5,478 calendar days**, it contains only **3,850 records** because stock markets remain closed on weekends and public holidays.

---

## Step 3: Statistical Summary (`describe()`)

### Close Price

```
Minimum Price : ₹375.60
Maximum Price : ₹10,312.71
Average Price : ₹3,844.01
Median Price  : ₹3,461.28
```

### Trading Volume

```
Minimum Volume : 1.8 Million shares
Maximum Volume : 19.4 Million shares
Average Volume : 4.3 Million shares
```

### Key Insight

The closing price increased from approximately **₹375** to more than **₹10,300**, representing nearly **27× growth** over 15 years. This confirms a **strong long-term upward trend**.

---

# Part 2 — analysis.ipynb (Detailed Analysis)

## Step 1: Feature Engineering

```python
df["Daily_Return"] = df["Close"].pct_change() * 100
df["Absolute_difference"] = df["Close"] - df["Open"]
df["Daily_Range"] = df["High"] - df["Low"]
```

Three new features were created.

| Feature | Formula | Purpose |
|---------|---------|---------|
| Daily_Return | Percentage change in closing price | Daily gain/loss (%) |
| Absolute_difference | Close − Open | Intraday price movement |
| Daily_Range | High − Low | Daily volatility |

These engineered features provide much more useful information than raw prices for both analysis and machine learning.

---

## Step 2: Long-Term Trend Analysis

```python
coeffs = np.polyfit(x, y, deg=1)
```

A linear trend line was fitted to the closing prices over the entire 15-year period.

### Observation

The slope of the trend line is clearly positive, confirming a **strong and consistent long-term upward trend** with only normal market fluctuations.

---

## Step 3: Yearly Trend Analysis

```python
yearly = df.groupby('year')['Close'].mean()
```

The average closing price for each year was calculated.

### Purpose

This analysis helps identify yearly growth patterns and shows which years experienced stronger or weaker stock performance.

---

## Step 4: Monthly Analysis

```python
month_avg = df.groupby('month')['Close'].mean()
```

The average closing price for each month (January–December) was calculated across all years.

### Purpose

The objective was to identify any calendar-based seasonality in stock prices.

### Observation

Unlike retail sales, stock prices generally do not exhibit strong monthly seasonality because they are influenced more by company performance and market sentiment than by recurring calendar events.

---

## Step 5: Best & Worst Trading Days

```python
df['Daily_Return'].nlargest(5)
df['Daily_Return'].nsmallest(5)
```

The five largest gains and five largest losses were identified.

### Purpose

These extreme events usually correspond to important company announcements, earnings reports, market crashes, or significant economic news.

---

## Step 6: Daily Return Statistics

```python
df['Daily_Return'].describe()
```

The statistical distribution of daily returns was analyzed.

### Purpose

The standard deviation of returns represents the stock's daily volatility.

---

## Step 7: Volume Analysis

```python
30-Day Moving Average of Volume
```

Trading volume was analyzed along with its 30-day moving average.

### Purpose

The moving average smooths short-term fluctuations and highlights long-term changes in trading activity.

---

## Step 8: Volume vs Daily Return

```python
plt.scatter(df['Volume'], df['Daily_Return'])
```

A scatter plot was created to examine the relationship between trading volume and daily returns.

### Purpose

To determine whether large trading volumes are associated with significant price movements.

---

## Step 9: Highest Volume Trading Days

```python
df.nlargest(10, 'Volume')
```

The ten highest-volume trading days were identified.

### Purpose

These days often coincide with major market events, earnings announcements, or significant news affecting the company.

---

## Step 10: Daily Price Range (Volatility)

```python
Daily_Range = High - Low
```

The daily trading range and its 30-day moving average were analyzed.

### Purpose

Daily Range serves as a direct measure of market volatility, helping identify highly volatile and relatively stable periods.

---

## Step 11: COVID-19 Market Crash

```python
plt.axvspan(
    '2020-01-01',
    '2020-12-31',
    color='red',
    alpha=0.3,
    label='COVID Crash'
)
```

The year 2020 was highlighted on the price chart.

### Observation

The COVID-19 market crash is a classic example of a **cyclical event**, not seasonality.

### Why?

- It did not occur at fixed calendar intervals.
- It was triggered by an unexpected global event.
- Its timing and duration were unpredictable.
- It disrupted normal business cycles.

The chart clearly shows the sharp decline during 2020 followed by the recovery phase.

---

# Overall Project Summary

```
✓ Applied datetime handling and moving averages
✓ Identified long-term trends using linear regression
✓ Explored yearly and monthly patterns
✓ Created engineered features for analysis
✓ Measured volatility using Daily Range
✓ Highlighted the COVID-19 market crash
✓ Validated multiple time series concepts using real stock market data
```

---

# Key Findings

1. **TCS stock price increased nearly 27× over 15 years**, demonstrating strong long-term growth.

2. **The dataset is completely clean**, with no missing values and correct data types.

3. **The COVID-19 crash is clearly visible**, making it an excellent real-world example of a cyclical event.

4. **Higher trading volume generally corresponds to greater price volatility.**

5. **Extreme gain and loss days were successfully identified**, providing opportunities for further investigation using financial news.

---