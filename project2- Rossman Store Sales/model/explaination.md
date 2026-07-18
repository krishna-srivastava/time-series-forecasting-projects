# Model Comparison

To evaluate the forecasting performance, three different models were trained and compared:

- **Random Forest**
- **XGBoost**
- **SARIMA**

> **Note:** Due to the computational cost of SARIMA, it was trained and evaluated only on **Store 1**, whereas Random Forest and XGBoost were trained using the complete feature-engineered dataset.

---

## Model Performance

| Model | MAE ↓ | RMSE ↓ | R² ↑ |
|-------|-------:|--------:|------:|
| Random Forest | 1032 | 1546 | **0.735** ✅ |
| SARIMA *(Store 1 Only)* | **929** | **1368** | 0.602 |
| XGBoost | 1586 | 2142 | 0.490 |

---

# Model Interpretation

## 🌲 Random Forest

Random Forest achieved the **highest R² score (0.735)**, indicating that it explained the largest proportion of variance in the sales data.

The model successfully captured complex nonlinear relationships using:

- Lag Features
- Rolling Statistics
- Calendar Features
- Promotion Information
- Holiday Information

Overall, Random Forest provided the best balance between prediction accuracy and generalization.

---

## 📈 SARIMA

SARIMA was evaluated **only on Store 1** because classical forecasting models are typically designed for a **single time series**.

Despite using only historical sales values and seasonal patterns, SARIMA achieved the **lowest MAE and RMSE**, showing strong forecasting capability for a single store.

However, its R² score was lower than Random Forest because it cannot utilize additional business information such as:

- Promotions
- Holidays
- Calendar Features
- Store-specific attributes

---

## ⚡ XGBoost

XGBoost produced the lowest overall performance in this experiment.

Although XGBoost is generally considered a powerful forecasting algorithm, the current model configuration did not outperform Random Forest.

Possible reasons include:

- Hyperparameters were not fully optimized.
- Additional feature engineering may be required.
- Further tuning using Grid Search or Random Search could significantly improve performance.

---

# Final Conclusion

Among all evaluated models, **Random Forest** delivered the best overall forecasting performance with an **R² score of 0.735**.

Although **SARIMA** achieved lower forecasting errors (MAE and RMSE), it was trained only on **Store 1** and relied solely on historical sales and seasonal patterns. Therefore, its results are not directly comparable with the machine learning models trained on the complete feature-engineered dataset.

**XGBoost** underperformed in this experiment, suggesting that additional hyperparameter tuning would be necessary before drawing final conclusions about its forecasting capability.

---

# Key Takeaways

- ✅ Random Forest was the best-performing overall model.
- ✅ SARIMA performed well for single-store seasonal forecasting.
- ✅ XGBoost requires further hyperparameter tuning.
- ✅ Feature engineering (Lag Features, Rolling Features, Calendar Features, and Promotions) significantly improved machine learning performance.
- ✅ Classical statistical models are suitable for individual time series, while machine learning models are better suited for multi-feature business forecasting problems.