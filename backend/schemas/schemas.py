from pydantic import BaseModel
from typing import Optional, List, Dict


class PredictRiskRequest(BaseModel):
    location: str
    weather_condition: Optional[str] = None   # if not given, fetched live
    night: Optional[bool] = None
    overspeeding: Optional[str] = None        # "Yes"/"No"
    drunk_driving: Optional[str] = None       # "Yes"/"No"


class PredictRiskResponse(BaseModel):
    location: str
    risk_level: str                 # Low, Moderate, High
    risk_score: float               # model's confidence in the predicted class
    class_probabilities: Dict[str, float]
    contributing_factors: List[str]


class HotspotItem(BaseModel):
    location: str
    accident_count: int
    fatal_count: int
    avg_risk_score: float
    risk_level: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RouteRiskRequest(BaseModel):
    start_location: str
    end_location: str


class AlertResponse(BaseModel):
    location: str
    alert: bool
    message: str
