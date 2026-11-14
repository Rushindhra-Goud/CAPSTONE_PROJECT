from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models.accident import Accident
from schemas.schemas import HotspotItem

router = APIRouter()


@router.get("/hotspots", response_model=List[HotspotItem])
def get_hotspots(db: Session = Depends(get_db)):
    """
    Groups accidents by location, returning counts + avg risk, for the
    frontend's map heatmap (Member 4).
    """
    rows = (
        db.query(
            Accident.location,
            func.count(Accident.accident_id).label("accident_count"),
            func.sum(func.coalesce(Accident.persons_died, 0)).label("fatal_count"),
            func.avg(Accident.risk_score).label("avg_risk_score"),
            func.avg(Accident.latitude).label("latitude"),
            func.avg(Accident.longitude).label("longitude"),
        )
        .group_by(Accident.location)
        .order_by(func.count(Accident.accident_id).desc())
        .all()
    )

    hotspots = []
    for r in rows:
        avg_risk = round(r.avg_risk_score or 0, 3)
        if avg_risk >= 0.6:
            risk_level = "Critical"
        elif avg_risk >= 0.4:
            risk_level = "High"
        elif avg_risk >= 0.2:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        hotspots.append(
            HotspotItem(
                location=r.location,
                accident_count=r.accident_count,
                fatal_count=int(r.fatal_count or 0),
                avg_risk_score=avg_risk,
                risk_level=risk_level,
                latitude=r.latitude,
                longitude=r.longitude,
            )
        )

    return hotspots
