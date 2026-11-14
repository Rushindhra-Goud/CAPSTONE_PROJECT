from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.accident import Accident
from schemas.schemas import AlertResponse

router = APIRouter()


@router.get("/alerts", response_model=AlertResponse)
def get_alert(location: str, db: Session = Depends(get_db)):
    """
    Returns a simple alert if the queried location has a high historical
    risk profile. Keeps it simple -- lookup against real historical data,
    no push-notification infrastructure needed for a mini project demo.
    """
    avg_risk = (
        db.query(func.avg(Accident.risk_score))
        .filter(Accident.location == location)
        .scalar()
    )
    blackspot_count = (
        db.query(func.count(Accident.accident_id))
        .filter(Accident.location == location, Accident.blackspot_nearby == "Yes")
        .scalar()
    )

    if avg_risk is None:
        return AlertResponse(
            location=location,
            alert=False,
            message="No historical data available for this location.",
        )

    if avg_risk >= 0.5 or (blackspot_count or 0) > 5:
        return AlertResponse(
            location=location,
            alert=True,
            message=f"Caution: {location} has a history of high-risk accidents. Drive carefully.",
        )

    return AlertResponse(
        location=location,
        alert=False,
        message=f"{location} currently shows a lower accident risk profile.",
    )
