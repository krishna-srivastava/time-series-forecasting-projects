from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import pandas as pd
import numpy as np
import joblib

model = None
feature_columns = None
historical_df = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    global feature_columns
    global historical_df

    print("Loading model...")
    model = joblib.load("Model/xgboost_model.pkl")
    feature_columns = joblib.load("Model/feature_columns.pkl")

    historical_df = pd.read_csv(
        "Data/uber_taxi_demand_5years.csv"
    )
    historical_df["datetime"] = pd.to_datetime(
        historical_df["datetime"]
    )
    historical_df = historical_df.sort_values(
        ["zone", "datetime"]
    )

    print("Model loaded!")
    print("Historical data loaded!")
    yield


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Taxi Demand Forecast API",
    description="24-hour Taxi Demand Forecasting API",
    version="1.0",
    lifespan=lifespan
)

class ForecastInput(BaseModel):
    zone: str = Field(description="Zone to forecast")
    start_datetime: str = Field(description="Forecast starting datetime")
    temperature: float = Field(description="Expected temperature")
    precipitation: float = Field(ge=0,description="Expected precipitation")

    is_raining: int = Field(ge=0,le=1)
    is_holiday: int = Field(ge=0,le=1)
    hours: int = Field(default=24,ge=1,le=24,description="Number of hours to forecast")


@app.get("/")
def home():
    return {
        "message": "Taxi Demand Forecast API is running!",
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.get("/zones")
def get_zones():
    zones = sorted(historical_df["zone"].unique().tolist())
    return {
        "zones": zones
    }

def create_forecast_features(timestamp,zone,zone_history,temperature,precipitation,is_raining,is_holiday):
    hour = timestamp.hour
    day_of_week = timestamp.dayofweek
    month = timestamp.month

    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    month_sin = np.sin(2 * np.pi * month / 12)
    month_cos = np.cos(2 * np.pi * month / 12)

    is_weekend = int(day_of_week >= 5)

    lag_1 = zone_history.iloc[-1]
    lag_2 = zone_history.iloc[-2]
    lag_3 = zone_history.iloc[-3]
    lag_24 = zone_history.iloc[-24]
    lag_168 = zone_history.iloc[-168]

    rolling_mean_24 = zone_history.iloc[-24:].mean()
    rolling_mean_168 = zone_history.iloc[-168:].mean()

    first_datetime = historical_df["datetime"].min()

    time_index = (
        timestamp - first_datetime
    ).total_seconds() / 3600

    features = {
        "time_index": time_index,

        "lag_1": lag_1,
        "lag_2": lag_2,
        "lag_3": lag_3,
        "lag_24": lag_24,
        "lag_168": lag_168,

        "rolling_mean_24": rolling_mean_24,
        "rolling_mean_168": rolling_mean_168,

        "hour_sin": hour_sin,
        "hour_cos": hour_cos,

        "day_of_week": day_of_week,
        "is_weekend": is_weekend,

        "month_sin": month_sin,
        "month_cos": month_cos,

        "temperature": temperature,
        "precipitation": precipitation,

        "is_raining": is_raining,
        "is_holiday": is_holiday
    }

    features["zone_Downtown"] = int(zone == "Downtown")
    features["zone_Midtown"] = int(zone == "Midtown")
    features["zone_Suburb"] = int(zone == "Suburb")
    features["zone_Uptown"] = int(zone == "Uptown")

    return pd.DataFrame([features])


@app.post("/forecast")
def forecast(data: ForecastInput):
    try:
        available_zones = historical_df["zone"].unique()

        if data.zone not in available_zones:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid zone. Available zones: {list(available_zones)}"
            )

        try:
            start_datetime = pd.to_datetime(data.start_datetime)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid start_datetime format."
            )

        zone_data = historical_df[
            historical_df["zone"] == data.zone
        ].copy()

        zone_data = zone_data.sort_values("datetime")
        pickup_history = zone_data["pickup_count"].tolist()

        if len(pickup_history) < 168:

            raise HTTPException(
                status_code=400,
                detail="Not enough historical data for lag_168."
            )

        predictions = []
        current_history = pickup_history.copy()

        for i in range(data.hours):
            forecast_datetime = (
                start_datetime +
                pd.Timedelta(hours=i)
            )

            zone_history = pd.Series(current_history)

            input_df = create_forecast_features(
                timestamp=forecast_datetime,
                zone=data.zone,
                zone_history=zone_history,
                temperature=data.temperature,
                precipitation=data.precipitation,
                is_raining=data.is_raining,
                is_holiday=data.is_holiday
            )

            input_df = input_df[feature_columns]
            prediction = model.predict(input_df)[0]
            prediction = max(0, float(prediction))

            predictions.append({
                "datetime": forecast_datetime,
                "predicted_pickups": round(prediction, 2)
            })

            current_history.append(prediction)

        forecast_df = pd.DataFrame(predictions)

        return {
            "status": "success",
            "zone": data.zone,
            "start_datetime": str(start_datetime),
            "hours": data.hours,
            "forecast": forecast_df.to_dict(orient="records")
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )