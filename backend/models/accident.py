"""
SQLAlchemy model matching cleaned_accidents.csv (53 columns) --
this is the exact file Member 2 trained the model on.
"""
from sqlalchemy import Column, Integer, Float, String
from database import Base


class Accident(Base):
    __tablename__ = "accidents"

    accident_id = Column(String, primary_key=True, index=True)
    date = Column(String)
    time = Column(String)
    day_of_week = Column(String)
    weekend = Column(Integer)
    peak_hour = Column(Integer)
    night = Column(Integer)

    location = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    road_name = Column(String)
    road_type = Column(String)
    lanes = Column(Integer)
    speed_limit_kmph = Column(Integer)
    road_surface = Column(String)
    potholes = Column(String)
    street_lighting = Column(String)
    traffic_signal = Column(String)
    junction_type = Column(String)

    weather_condition = Column(String)
    rainfall_mm = Column(Float)
    temperature_c = Column(Float)
    humidity_pct = Column(Float)
    visibility_km = Column(Float)
    wind_speed_kmph = Column(Float)

    traffic_volume_vehicles_per_hour = Column(Integer)
    traffic_density = Column(String)
    average_speed_kmph = Column(Float)

    vehicle_type = Column(String)
    vehicles_involved = Column(Integer)
    overspeeding = Column(String)
    drunk_driving = Column(String)
    driver_distraction = Column(String)

    accidents_last_30_days = Column(Integer)
    accidents_last_90_days = Column(Integer)
    accidents_last_365_days = Column(Integer)
    blackspot_nearby = Column(String)
    blackspot_distance_km = Column(Float)

    persons_injured = Column(Integer)
    persons_died = Column(Integer)
    severity = Column(String)
    risk_score = Column(Float)
    risk_level = Column(String)

    # Engineered features the model was trained on -- must be stored so
    # /predict-risk can look up real historical values, and so re-training
    # or auditing later doesn't require re-deriving them.
    hour = Column(Integer)
    minute = Column(Integer)
    is_weekend = Column(Integer)
    is_peak_hour = Column(Integer)
    is_night = Column(Integer)
    weather_risk = Column(Float)
    grid_lat = Column(Float)
    grid_lon = Column(Float)
    zone_id = Column(String)
    cluster_id = Column(Integer)
