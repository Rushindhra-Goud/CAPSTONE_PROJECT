import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func

from database import Base, SessionLocal, engine
from models.accident import Accident
from routes import predict, hotspots, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Make sure the DB exists and is populated (Render's disk is ephemeral)."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(func.count(Accident.accident_id)).scalar() or 0
    finally:
        db.close()
    if count == 0:
        from load_data import load
        load()
    yield


app = FastAPI(
    title="SafeRoute API",
    description="Road accident risk prediction & traffic safety API for Warangal.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS_ORIGINS = comma-separated list of allowed frontend URLs, e.g.
# "https://saferoute-web.onrender.com". Defaults to "*" if unset.
_origins = [o.strip().rstrip("/") for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, tags=["Prediction"])
app.include_router(hotspots.router, tags=["Hotspots"])
app.include_router(alerts.router, tags=["Alerts"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "SafeRoute API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
