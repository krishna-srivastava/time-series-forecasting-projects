# Taxi Demand — Exploratory Data Analysis Summary

This document explains the analysis performed across the two notebooks:
`TIme_and_demand_analysis.ipynb` (overall time-based patterns) and
`zone_analysis.ipynb` (zone-level and external-factor patterns), on the
5-year hourly `uber_taxi_demand_5years.csv` dataset.

---

## 1. Dataset Overview

- **Total pickups (5 years, all zones):** 8,630,596
- **Average pickups per hour:** 39.39
- **Median pickups per hour:** 29.0
- **Standard deviation:** 36.27

The gap between mean (39.39) and median (29.0) tells us the distribution is
**right-skewed** — most hours have relatively low demand, but a smaller
number of peak hours pull the average up. This was confirmed visually by the
pickup distribution histogram, which showed a long right tail rather than a
symmetric bell curve.

- **Peak demand:** 571 pickups, recorded on **2024-12-31 08:00** in **Midtown**
- **Lowest demand:** 0 pickups, recorded on **2021-01-01 03:00** in **Suburb**

These two extremes already hint at the two strongest drivers of demand:
*time of day* (early morning vs. rush hour) and *zone type* (a quiet suburb
vs. a dense business district).

---

## 2. Overall Demand Trend Over Time

A 5-year line plot of raw pickups was overlaid with a 30-hour rolling average
(labeled `SMA_7` in the notebook, but using a 30-period window) and a
linear trend line (`np.polyfit`, degree 1).

- **Trend slope:** +0.0001 pickups/hour step

Although the slope looks tiny in raw units, because it's applied across
~43,800 hourly steps it corresponds to a real, gradual **upward trend** in
demand over the 5 years — consistent with the year-over-year averages below.
The rolling average line smooths out the hour-to-hour noise and makes this
slow upward drift visible underneath the daily/weekly oscillations.

---

## 3. Hourly Demand Pattern

Average pickups were grouped by hour-of-day (0–23) and plotted as a bar
chart. The result shows a clear **bimodal (two-peak) daily pattern**:

- A **morning peak** around 7–9 AM (commute to work)
- An **evening peak** around 5–7 PM (commute home)
- A **trough** in the early morning hours (roughly 2–5 AM), when demand is
  at its lowest

This is the classic urban ride-hailing signature — demand tracks the
workday, not a flat or random distribution.

---

## 4. Weekday Pattern

Grouping by day of week produced:

| Day | Avg Demand |
|---|---|
| Monday | 43.02 |
| Tuesday | 43.67 |
| Wednesday | 43.34 |
| Thursday | 42.80 |
| **Friday** | **49.38** |
| Saturday | 29.83 |
| Sunday | 23.69 |

**Key insight:** Weekdays (Mon–Thu) are fairly flat and close to each other
(~43), but **Friday stands out as the highest-demand day** (evening
social/nightlife trips stacking on top of the normal commute), while
**Saturday and especially Sunday drop off sharply** — commute demand
disappears and isn't fully replaced by leisure trips.

---

## 5. Monthly and Quarterly Patterns

Monthly averages range from a low of **33.92 (March)** to a high of
**45.24 (July)**, with demand generally rising through spring into summer
and dipping again in winter (Feb–March are the lowest months).

Grouping the same data by quarter makes the seasonal shape even clearer:

| Quarter | Avg Demand |
|---|---|
| Q1 (Jan–Mar) | 35.57 |
| Q2 (Apr–Jun) | 39.00 |
| Q3 (Jul–Sep) | **43.83** (highest) |
| Q4 (Oct–Dec) | 39.07 |

**Key insight:** Demand is clearly **seasonal**, peaking in the summer
quarter (Q3) and bottoming out in winter (Q1) — likely reflecting more
travel, events, and outdoor activity in warmer months.

---

## 6. Year-over-Year Growth

| Year | Avg Demand |
|---|---|
| 2021 | 33.92 |
| 2022 | 36.35 |
| 2023 | 39.08 |
| 2024 | 42.27 |
| 2025 | 45.32 |

Demand has grown **every single year**, from ~34 in 2021 to ~45 in 2025 —
roughly a **34% increase over 5 years**. This confirms the small positive
slope detected in the overall trend line and shows the platform/city's ride
demand is on a steady growth path rather than staying flat or declining.

---

## 7. Zone-Level Demand

Total pickups summed by zone over the full 5 years:

| Zone | Total Pickups |
|---|---|
| **Midtown** | 2,708,473 (highest) |
| Airport | 2,399,322 |
| Downtown | 2,160,030 |
| Uptown | 1,025,075 |
| **Suburb** | 337,696 (lowest) |

**Key insight:** Midtown, a dense business zone, generates the most demand
overall, followed closely by Airport (which has steady round-the-clock
traffic). Suburb generates roughly **8x less** demand than Midtown,
reflecting lower population density and greater reliance on personal
vehicles.

---

## 8. Effect of Holidays

| Condition | Avg Demand |
|---|---|
| Normal day | 39.32 |
| Holiday | 44.35 |

**Holiday effect: +12.81%** — demand is noticeably higher on holidays than
on an average day. (Note: this is the *blended* effect across all holiday
types; some individual holidays like Christmas or New Year's Day actually
*reduce* demand, while others like New Year's Eve massively *increase* it —
the aggregate number here averages all of that together.)

---

## 9. Effect of Rain

| Condition | Avg Demand |
|---|---|
| No rain | 36.94 |
| Rain | 52.20 |

**Rain effect: +41.31%** — this is the **single strongest external factor**
found in the analysis. When it's raining, people are far more likely to
call a ride instead of walking, biking, or waiting outside for public
transit.

---

## 10. Combined Holiday × Rain Effect

| Holiday | Rain | Avg Demand |
|---|---|---|
| No | No | 36.90 |
| No | Yes | 52.04 |
| Yes | No | 40.01 |
| **Yes** | **Yes** | **60.87** (highest) |

**Key insight:** The two effects **stack** — a rainy holiday produces the
highest average demand of any condition combination (60.87), about **65%
higher** than a normal dry weekday. This shows holiday and weather effects
are not just independent add-ons; combined, they compound.

---

## 12. Correlation Between Demand and Weather Variables

| | pickup_count | temperature | precipitation |
|---|---|---|---|
| **pickup_count** | 1.00 | 0.10 | 0.13 |
| temperature | 0.10 | 1.00 | 0.03 |
| precipitation | 0.13 | 0.03 | 1.00 |

Both temperature and precipitation show **weak positive linear
correlation** with pickup demand (0.10 and 0.13 respectively). This might
look like weather barely matters — but it doesn't contradict the strong
+41% rain effect found earlier. Correlation only captures **linear**
relationships across the whole range of values, while the rain effect is
closer to a **threshold/on-off effect** (it's not "more rain = proportionally
more rides," it's "raining at all vs. not raining at all" that matters
most). This is a good reminder that correlation coefficients alone can
understate the importance of a variable that acts more like a switch than a
dial.

---

## 13. Overall Takeaways

1. Demand is **not random** — it's driven by predictable, stackable
   patterns: time of day, day of week, month/season, holidays, weather, and
   zone type.
2. The **strongest single external driver** found was rain (+41%), followed
   by holidays (+13%) — and these two compound when they co-occur.
3. **Midtown and Airport** are the highest-demand, most commercially
   important zones; **Suburb** is a minor contributor.
4. Demand has a **clear multi-year upward trend** (+34% from 2021 to 2025),
   which any forecasting model should account for (e.g., using a trend
   term, differencing, or a growth-aware model) rather than assuming demand
   is stationary.
5. For forecasting, the most useful engineered features based on this EDA
   would be: **hour-of-day**, **day-of-week (especially Friday/weekend
   flags)**, **month/quarter (seasonality)**, **is_holiday**,
   **is_raining**, and **zone**, since each of these was shown to have a
   measurable, independent effect on demand.