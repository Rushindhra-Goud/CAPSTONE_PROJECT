from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.accident import Accident
from schemas.schemas import PredictRiskRequest, PredictRiskResponse
from services.ml_service import predict_risk, ALL_FEATURES
from services.weather_service import get_live_weather

router = APIRouter()


@router.post("/predict-risk", response_model=PredictRiskResponse)
def predict_risk_endpoint(payload: PredictRiskRequest, db: Session = Depends(get_db)):
    """
    Builds a full feature row for the model by taking a representative
    historical record for the requested location (which already has the
    correct grid_lat, grid_lon, cluster_id, zone_id, etc. computed by
    Member 1's pipeline) and overriding it with any live inputs the
    caller provided (weather, night, overspeeding, drunk_driving).
    """
    # Most recent record for this location acts as the feature template
    record = (
        db.query(Accident)
        .filter(Accident.location == payload.location)
        .order_by(Accident.date.desc())
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data found for location '{payload.location}'. "
                   f"Check /hotspots for valid location names.",
        )

    # Build the base row from the historical record
    row = {feat: getattr(record, feat, None) for feat in ALL_FEATURES}

    # Override with live inputs where provided
    if payload.weather_condition:
        row["weather_condition"] = payload.weather_condition
    else:
        row["weather_condition"] = get_live_weather("Warangal")

    if payload.night is not None:
        row["night"] = int(payload.night)
        row["is_night"] = int(payload.night)

    if payload.overspeeding:
        row["overspeeding"] = payload.overspeeding

    if payload.drunk_driving:
        row["drunk_driving"] = payload.drunk_driving

    row["location"] = payload.location

    result = predict_risk(row)
    return result
