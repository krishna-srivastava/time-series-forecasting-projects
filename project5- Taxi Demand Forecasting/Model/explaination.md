# Taxi/Uber Demand Forecasting — Feature Engineering & Modeling

This document explains the feature engineering (`python.ipynb`) and model
training (`model.ipynb`) stages of the project, built on top of the
5-year hourly `uber_taxi_demand_5years.csv` dataset (5 zones: Airport,
Downtown, Midtown, Suburb, Uptown).

---

## 1. Data Loading & Preprocessing

The raw dataset was loaded, `datetime` was converted to a proper pandas
datetime type, and the dataframe was sorted chronologically and set as the
index. A `time_index` column (hours elapsed since the start of the
dataset) was created immediately after loading — this later serves as a
simple, bounded way to let the model capture the multi-year growth trend
seen in the EDA (~34% growth from 2021 to 2025) without relying on
unbounded cumulative statistics.

---

## 2. Feature Engineering

### 2.1 Time-based features
From the datetime index, the following were derived:
- `hours`, `day_of_month`, `day_of_week`, `month`, `quarter` (raw calendar values)
- `is_weekend` (flag for Saturday/Sunday)
- **Cyclical encodings**: `hour_sin`/`hour_cos` and `month_sin`/`month_cos`

Cyclical encoding matters because raw hour/month values are misleading to
a model — for example, hour 23 and hour 0 are numerically far apart but
are actually adjacent in time. Encoding them as sine/cosine pairs places
them next to each other on a circle, which lets the model correctly treat
the end and start of a day (or year) as close together.

### 2.2 Lag features
Computed **per zone** using `groupby('zone')` before shifting, to avoid
one zone's history leaking into another zone's row:
```python
df['lag_1']   = df.groupby('zone')['pickup_count'].shift(1)
df['lag_2']   = df.groupby('zone')['pickup_count'].shift(2)
df['lag_3']   = df.groupby('zone')['pickup_count'].shift(3)
df['lag_24']  = df.groupby('zone')['pickup_count'].shift(24)   # same hour, previous day
df['lag_168'] = df.groupby('zone')['pickup_count'].shift(168)  # same hour, previous week
```
`lag_168` (one week prior) turned out to be the single strongest predictor
in the model — it directly encodes the weekly demand cycle (e.g. Friday
evenings are consistently busy, Sunday mornings are consistently quiet)
that was first identified during EDA.

### 2.3 Rolling and expanding statistics
Rolling means were computed with `.shift(1)` applied **before** `.rolling()`,
which is essential — without the shift, a row's rolling average would
include its own current value, which is a form of data leakage (the model
would effectively be allowed to "see the answer" through the feature).
```python
df['rolling_mean_24']  = df.groupby('zone')['pickup_count'].transform(lambda x: x.shift(1).rolling(24).mean())
df['rolling_mean_168'] = df.groupby('zone')['pickup_count'].transform(lambda x: x.shift(1).rolling(168).mean())
```
`expanding_sum`, `expanding_mean`, and `expanding_std` were also computed
(again with a leading `.shift(1)` to avoid leakage) but were ultimately
**excluded from the final feature set**. These statistics are unbounded —
they only ever grow as more history accumulates — which makes them prone
to extrapolation problems in tree-based models and largely redundant with
`time_index`, which captures the same long-term trend more cleanly.

### 2.4 Zone encoding
The `zone` column was preserved separately as `zone_data` (for later
per-zone analysis and debugging) and also one-hot encoded with
`drop_first=True`, producing `zone_Downtown`, `zone_Midtown`,
`zone_Suburb`, `zone_Uptown` (Airport becomes the implicit reference
category — its effect is captured in the model's baseline rather than a
dedicated column).

### 2.5 Handling missing values
Because lag/rolling features need historical data that doesn't exist for
the very first rows of each zone (`lag_168` needs 168 prior hours), those
rows were dropped:
```
Original rows : 219,120
After dropna  : 218,280
Rows removed  : 840   (0.4% data loss)
```
This is expected and an acceptable trade-off — 840 rows out of 219,120 is
a minimal loss, and there is no way to compute a genuine 1-week lag
without at least a week of prior history per zone.

### 2.6 Final feature set (22 features used for training)
```
time_index, lag_1, lag_2, lag_3, lag_24, lag_168,
rolling_mean_24, rolling_mean_168,
hour_sin, hour_cos, day_of_week, is_weekend, month_sin, month_cos,
temperature, precipitation, is_raining, is_holiday,
zone_Downtown, zone_Midtown, zone_Suburb, zone_Uptown
```
(`zone_data` and `pickup_count` were kept in the saved CSV for reference
but excluded from the actual model inputs.)

---

## 3. Train/Test Split

A **chronological split** was used — not a random split — because this is
a time series problem. Randomly shuffling rows before splitting would let
the model "see" data from the future during training (since lag/rolling
features from nearby time points would leak across the train/test
boundary), producing an artificially inflated, unrealistic accuracy score.

```
Train: 2021-01-08 to 2025-01-02   (174,624 rows, ~80%)
Test:  2025-01-02 to 2025-12-31   ( 43,656 rows, ~20%)
```

The test set spans a full calendar year (2025), which is important — it
means the evaluation covers every season, every day of the week, and every
holiday in the dataset, rather than a narrow slice that might not
represent the model's true generalization ability.

---

## 4. Model: XGBoost Regressor

```python
XGBRegressor(
    n_estimators=350,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)
```
`subsample=0.8` and `colsample_bytree=0.8` add regularization by training
each tree on a random 80% of rows/columns, which helps prevent
overfitting given how strongly the lag features dominate.

Training validation RMSE (on the held-out test set, tracked during
boosting):
```
[0]    validation_0-rmse: 40.20
[50]   validation_0-rmse: 11.10
[100]  validation_0-rmse: 10.71
[200]  validation_0-rmse: 10.37
[300]  validation_0-rmse: 10.06
[349]  validation_0-rmse:  9.96
```
The steep drop in the first 50 rounds, followed by a long, gentle decline,
is a healthy training curve — it shows the model finding strong signal
early (largely from the lag features) and then squeezing out smaller
gains from the remaining features without the error swinging back up
(which would indicate overfitting).

---

## 5. Results

| Metric | Value |
|---|---|
| MAE | 6 |
| RMSE | 10 |
| R² | 0.942 |

An R² of 0.94 means the model explains about 94% of the variance in
hourly pickup demand across all 5 zones and a full year of test data —
a strong result, especially considering demand ranges from single digits
(Suburb, late night) to 500+ (Midtown, rush hour).

### Per-zone MAE
```
Airport:   7.73
Downtown:  7.12
Midtown:  10.01
Suburb:    2.52
Uptown:    4.56
```
Midtown has the highest raw error, but it also has by far the highest
demand volume — its errors should be interpreted relative to its scale
(a MAE of 10 on values that regularly exceed 300 is proportionally small).
Suburb's MAE of 2.52 looks best in absolute terms, but Suburb's demand
rarely exceeds 30, so this comparison is not entirely apples-to-apples;
a percentage-based metric (MAPE) per zone would give a fairer comparison
across zones with very different demand scales.

### Actual vs. Predicted (visual check)
A full-year overlay of actual vs. predicted values for the test set shows
the predicted line tracking the actual line very closely across daily and
weekly cycles. The one place a visible gap appears is at the very end of
the test period — New Year's Eve 2025 — where actual demand spikes to
~440 but the model's prediction comes in noticeably lower (~360). This is
consistent with the feature importance findings below: the model has no
way to distinguish New Year's Eve from any other holiday, since all
holidays currently share a single generic `is_holiday` flag.

---

## 6. Feature Importance

```
lag_168             0.418   <- strongest: last week, same hour
lag_1               0.162   <- most recent hour
is_raining          0.134   <- weather has a real, learned effect
lag_24              0.063   <- same hour, yesterday
precipitation       0.049
zone_Midtown        0.026
is_weekend          0.024
day_of_week         0.024
is_holiday          0.018
hour_cos            0.013
zone_Downtown       0.010
hour_sin            0.009
zone_Uptown         0.009
rolling_mean_168    0.008
month_cos           0.007
lag_3               0.006
rolling_mean_24     0.005
time_index          0.004
temperature         0.003
lag_2               0.003
zone_Suburb         0.003
month_sin           0.003
```

**Key takeaway:** the model relies most heavily on `lag_168` — meaning it
has effectively learned the weekly seasonality pattern found in the EDA
(Friday is the busiest day, Sunday the quietest) rather than defaulting to
a naive "just copy the last hour" strategy. `is_raining` earning 13.4%
importance also confirms the model picked up on the strong rain effect
(+41% demand) identified earlier in the EDA. `time_index` and `temperature`
have very low importance — this is expected, since `lag_168` already
implicitly carries most of the year-over-year growth signal (last week's
value is already somewhat "grown" relative to a year ago), and demand's
relationship with temperature is weak and non-linear.

---

## 7. Known Limitations / Possible Next Steps

1. **Generic `is_holiday` flag** — currently all holidays are treated
   identically, which causes the model to under-predict extreme spikes
   like New Year's Eve and over-predict quiet holidays like Christmas
   Day, since their opposite effects average out into one flag. Splitting
   this into per-holiday indicators (`is_nye`, `is_christmas`, etc.) would
   likely close the gap seen at the end of the actual-vs-predicted plot.
2. **MAE vs. MAPE for zone comparison** — raw MAE naturally scales with
   each zone's demand volume, so it currently makes Midtown look "worse"
   than Suburb even though its relative accuracy may be similar or
   better. Reporting MAPE per zone would give a fairer picture.
3. **Sort stability at the train/test boundary** — sorting by `datetime`
   alone (not `['datetime', 'zone']`) with a non-stable sort can, in rare
   cases, shuffle which zone's row lands on which side of the train/test
   split boundary for the single hour where the 80/20 cut falls. The
   impact is negligible (a handful of rows) but using
   `sort_values(['datetime', 'zone'], kind='stable')` would make the
   split fully deterministic.

None of these are correctness bugs — the pipeline is leakage-free and the
reported metrics (MAE, RMSE, R²) are trustworthy. They are refinements
that would likely push performance and interpretability a bit further if
this project is extended.