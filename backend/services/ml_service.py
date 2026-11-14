"""
ML prediction service -- now using the REAL model from Member 2.

Model: XGBoost classifier (tuned) inside an sklearn Pipeline
        (ColumnTransformer preprocessing + classifier)
Files:  saferoute_risk_model.pkl, risk_label_encoder.pkl
        (both must sit in this services/ folder)

IMPORTANT: the model expects an EXACT set of 46 columns, matching
cleaned_accidents.csv minus the target/leakage columns
(accident_id, risk_score, risk_level, persons_injured, persons_died, severity).
The predict_risk() function below builds a one-row DataFrame with exactly
those columns, in a form the pipeline's ColumnTransformer can consume
(order doesn't matter to ColumnTransformer since it selects by name, but
every expected column MUST be present or it will raise an error).
"""
import os
import warnings
import joblib
import pandas as pd
from typing import Optional

warnings.filterwarnings("ignore", category=UserWarning)  # sklearn version-mismatch warnings

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "saferoute_risk_model.pkl")
_ENCODER_PATH = os.path.join(os.path.dirname(__file__), "risk_label_encoder.pkl")

model = joblib.load(_MODEL_PATH)
label_encoder = joblib.load(_ENCODER_PATH)

# The exact columns the model's ColumnTransformer expects (from the pipeline).
NUMERIC_FEATURES = [
    "weekend", "peak_hour", "night", "latitude", "longitude", "lanes",
    "speed_limit_kmph", "rainfall_mm", "temperature_c", "humidity_pct",
    "visibility_km", "wind_speed_kmph", "traffic_volume_vehicles_per_hour",
    "average_speed_kmph", "vehicles_involved", "accidents_last_30_days",
    "accidents_last_90_days", "accidents_last_365_days", "blackspot_distance_km",
    "hour", "minute", "is_weekend", "is_peak_hour", "is_night", "weather_risk",
    "grid_lat", "grid_lon", "cluster_id",
]
CATEGORICAL_FEATURES = [
    "date", "time", "day_of_week", "location", "road_name", "road_type",
    "road_surface", "potholes", "street_lighting", "traffic_signal",
    "junction_type", "weather_condition", "traffic_density", "vehicle_type",
    "overspeeding", "drunk_driving", "driver_distraction", "blackspot_nearby",
    "zone_id",
]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def predict_risk(input_row: dict) -> dict:
    """
    input_row must contain (or be filled in with defaults/lookups for)
    every column in ALL_FEATURES. Missing numeric values are imputed by
    the pipeline itself (SimpleImputer), so partial input is tolerated,
    but categorical columns should be real category strings, not None,
    where possible for best accuracy.
    """
    row = {feat: input_row.get(feat) for feat in ALL_FEATURES}
    X = pd.DataFrame([row])

    pred_encoded = model.predict(X)[0]
    risk_level = label_encoder.inverse_transform([pred_encoded])[0]

    # Probability/confidence per class, if the classifier supports it
    contributing_factors = []
    try:
        proba = model.predict_proba(X)[0]
        classes = label_encoder.inverse_transform(range(len(proba)))
        proba_map = {cls: round(float(p), 3) for cls, p in zip(classes, proba)}
        confidence = proba_map.get(risk_level, None)
    except Exception:
        proba_map = {}
        confidence = None

    if row.get("drunk_driving") == "Yes":
        contributing_factors.append("Drunk driving reported")
    if row.get("overspeeding") == "Yes":
        contributing_factors.append("Overspeeding reported")
    if row.get("is_night") or row.get("night"):
        contributing_factors.append("Night-time driving")
    if row.get("weather_condition") not in (None, "Clear"):
        contributing_factors.append(f"Weather condition: {row.get('weather_condition')}")
    if row.get("blackspot_nearby") == "Yes":
        contributing_factors.append("Near a known accident blackspot")
    if not contributing_factors:
        contributing_factors.append("No major risk factors detected")

    return {
        "location": row.get("location"),
        "risk_level": str(risk_level),
        "risk_score": confidence if confidence is not None else 0.0,
        "class_probabilities": proba_map,
        "contributing_factors": contributing_factors,
    }
