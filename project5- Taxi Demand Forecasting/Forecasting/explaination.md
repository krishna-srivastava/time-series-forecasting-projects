# Taxi Demand Forecasting — Forecasting Stage (Deployment)

This document explains the model-saving and forecasting steps carried out
after training the XGBoost model, including a year-over-year sanity check
of the forecast for **2026-01-01 (Airport zone)**.

---

## 1. Saving the Model for Reuse

```python
import joblib

joblib.dump(model, 'xgboost_model.pkl')

feature_columns = list(X_train.columns)
joblib.dump(feature_columns, 'feature_columns.pkl')
```

Two artifacts are saved:
- **`xgboost_model.pkl`** — the trained model itself
- **`feature_columns.pkl`** — the exact list and order of feature columns
  the model was trained on

Saving `feature_columns.pkl` alongside the model matters because XGBoost
expects new prediction data to have the **same columns, in the same
order**, as the training data. Without this, a mismatched or reordered
column set can silently produce incorrect predictions instead of an
obvious error.

This includes the one-hot encoded zone columns (`zone_Downtown`,
`zone_Midtown`, `zone_Suburb`, `zone_Uptown`). This is correct and
necessary — the model was trained with these columns, so any future
prediction request (for any zone) must reconstruct the same one-hot
pattern. For example, forecasting Airport (the reference category during
one-hot encoding) means all four zone dummy columns are set to `0`.

---

## 2. What's Needed to Forecast a New Day

Because the model relies heavily on lag and rolling features, forecasting
a future date is not just "plug in a date" — it requires:

1. **The previous 168 hours (1 week) of actual pickup data** for the zone
   being forecast, to compute `lag_1`, `lag_24`, `lag_168`,
   `rolling_mean_24`, `rolling_mean_168`.
2. **Weather and holiday inputs for the forecast date** (`temperature`,
   `precipitation`, `is_raining`, `is_holiday`) — these must be supplied
   in advance (e.g. from a weather forecast, or from historical data when
   testing).
3. **Correct one-hot zone encoding** matching the zone being forecast.
4. **Exact column order**, reconstructed using the saved
   `feature_columns.pkl`:
   ```python
   feature_columns = joblib.load('feature_columns.pkl')
   X_new = X_new[feature_columns]
   ```

---

## 3. Forecast Evaluation: 2026-01-01 (Airport)

Since the training data only goes up to the end of 2025, forecasting
**2026-01-01** tests the model on a genuinely unseen date. As a sanity
check, this forecast was compared against the **actual 2025-01-01** data
for the same zone (a year-over-year comparison, not a same-year accuracy
test).

### Daily shape comparison

| Time of day | 2025 actual | 2026 predicted |
|---|---|---|
| Morning peak (~8-9 AM) | 91 | 90 |
| Evening peak (~17-20h) | 70–81 | 74–81 |
| Overnight (low hours) | low | low |

**The daily rhythm matches closely** — both years show the same bimodal
pattern (morning commute peak, evening peak, quiet overnight hours). This
confirms the model has genuinely learned Airport's recurring daily demand
shape rather than producing arbitrary numbers.

### Overall level comparison

```
2025-01-01 actual average    ≈ 64.5 pickups/hour
2026-01-01 predicted average ≈ 60.1 pickups/hour   (≈ 6.8% LOWER)
```

This is the opposite of what would be expected. The dataset was
constructed with a built-in **~8% year-over-year growth trend**
(overall demand grew ~34% from 2021 to 2025), so a 2026 forecast should
logically be *higher* than the equivalent 2025 date, not lower.

---

## 4. Why the Growth Trend Isn't Showing Up

This traces back to something visible earlier in the feature importance
results: `time_index` — the feature meant to carry the long-term growth
signal — has very low importance (**0.4%**) in the trained model. The
model relies overwhelmingly on `lag_168` and `lag_1` instead.

This has a direct consequence when forecasting into a new date range:
when predicting 2026-01-01, the model's lag features pull from the
**last week of actual December 2025 data** (a natural post-holiday lull).
Since the model never learned an explicit upward trend from `time_index`,
it simply carries that recent baseline forward rather than adjusting it
upward for expected 2026 growth.

**This is a known and common limitation of tree-based models like
XGBoost**: they split on feature value ranges seen during training and do
not extrapolate a continuous trend beyond that range. If `time_index`
values for 2026 are higher than anything seen in training, the model
effectively cannot use that information to project growth — it falls back
on the lag features, which only reflect recent history, not the
long-term trajectory.

---

## 5. Interpretation

- **Short-term / seasonal forecasting**: strong. Daily and weekly patterns
  (rush hours, weekday vs. weekend, recent trends) are captured accurately.
- **Long-term trend extrapolation** (e.g. "how much will demand grow next
  year"): weak. The model under-projects growth into unseen future periods
  because tree-based models don't extrapolate trends the way linear models
  or trend-aware time series models (e.g. Prophet, SARIMA with a trend
  component) do.

This is a reasonable and known trade-off for XGBoost-based forecasting
models — it isn't a bug, but a limitation worth explicitly stating.

---

## 6. Possible Future Improvement

A natural next step would be a **hybrid approach**: model the long-term
trend separately (e.g. fit a simple linear/exponential growth curve on
`time_index`) and add it as a correction on top of the XGBoost model's
short-term predictions — combining XGBoost's strength at capturing
seasonal/cyclical patterns with a trend model's strength at extrapolating
growth into the future.