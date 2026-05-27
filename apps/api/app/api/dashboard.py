"""
Dashboard endpoint.

Reads PM2.5 from `aq_measurements` and weather from `weather_hourly`, both
populated by the Celery worker. If the weather table is empty (no ingest
has run yet), we fall back to a one-shot Open-Meteo fetch so the endpoint
is never empty on a fresh deploy — but the steady-state path stays
DB-only and is what gets measured under load.
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.clients.openmeteo_client import fetch_weather_hourly
from app.db.session import engine
from app.models.location import Location
from app.repositories.aq_repo import get_pm25_series
from app.repositories.weather_repo import get_weather_series
from app.services.aqi_service import pm25_to_aqi
from app.services.insights_service import (
    align_series_by_time,
    correlation_insights,
    summarize_pm25,
)
from app.services.weather_service import normalize_weather_hourly

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/location/{location_id}")
async def dashboard_location(
    location_id: int,
    hours: int = 24,
    bad_threshold: float = 25.0,
):
    with Session(engine) as session:
        loc = session.query(Location).filter(Location.id == location_id).first()
        if not loc:
            raise HTTPException(status_code=404, detail="Location not found")

        pm25 = get_pm25_series(session, location_id=location_id, hours=hours)
        weather = get_weather_series(session, location_id=location_id, hours=hours)

    # Cold-start fallback: if Celery hasn't ingested weather yet, do a
    # one-shot live fetch so the first dashboard view isn't blank.
    if not weather:
        try:
            raw = await fetch_weather_hourly(loc.lat, loc.lon, hours=hours)
            weather = normalize_weather_hourly(raw)
        except Exception:
            weather = []

    metrics = summarize_pm25(pm25, bad_threshold=bad_threshold)
    aligned = align_series_by_time(pm25, weather)
    corr = correlation_insights(aligned)

    # AQI enrichment: latest reading + per-point band for chart shading
    aqi_latest = pm25_to_aqi(metrics.get("latest"))
    aqi_avg = pm25_to_aqi(metrics.get("avg"))
    aqi_max = pm25_to_aqi(metrics.get("max"))

    pm25_with_aqi = [
        {**row, "aqi": (pm25_to_aqi(row["v"]) or {}).get("aqi")}
        for row in pm25
    ]

    return {
        "location": {
            "id": loc.id,
            "name": loc.name,
            "state": loc.state,
            "country": loc.country,
            "lat": loc.lat,
            "lon": loc.lon,
        },
        "hours": hours,
        "pm25": pm25_with_aqi,
        "weather": weather,
        "metrics": metrics,
        "aqi": {
            "latest": aqi_latest,
            "avg": aqi_avg,
            "max": aqi_max,
        },
        "aligned": aligned,
        "correlation": corr,
    }