"""
Summary endpoints — leaderboards, trends, and the locations map.
"""
from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.daily_metrics import DailyMetrics
from app.models.location import Location
from app.repositories.aq_repo import get_latest_pm25_per_location
from app.services.aqi_service import pm25_to_aqi

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/bad-days")
def bad_days_leaderboard(days: int = 30):
    """Locations ranked by how many bad-air days they've had in the window."""
    since = date.today() - timedelta(days=days)

    with Session(engine) as session:
        stmt = (
            select(
                Location.id.label("location_id"),
                Location.name,
                Location.state,
                func.coalesce(func.sum(DailyMetrics.bad_day), 0).label("bad_days"),
                func.max(DailyMetrics.pm25_max).label("max_pm25"),
            )
            .join(DailyMetrics, DailyMetrics.location_id == Location.id, isouter=True)
            .where((DailyMetrics.day >= since) | (DailyMetrics.day.is_(None)))
            .group_by(Location.id, Location.name, Location.state)
            .order_by(func.coalesce(func.sum(DailyMetrics.bad_day), 0).desc())
        )
        rows = session.execute(stmt).all()

    return [
        {
            "location_id": r.location_id,
            "name": r.name,
            "state": r.state,
            "bad_days": int(r.bad_days or 0),
            "max_pm25": float(r.max_pm25) if r.max_pm25 is not None else None,
        }
        for r in rows
    ]


@router.get("/bad-days-trend")
def bad_days_trend(location_id: int, days: int = 90):
    """Per-day pm25_max trend for one location."""
    since = date.today() - timedelta(days=days)

    with Session(engine) as session:
        loc = session.query(Location).filter(Location.id == location_id).first()
        if not loc:
            raise HTTPException(status_code=404, detail="Location not found")

        stmt = (
            select(DailyMetrics.day, DailyMetrics.pm25_max, DailyMetrics.bad_day)
            .where(DailyMetrics.location_id == location_id)
            .where(DailyMetrics.day >= since)
            .order_by(DailyMetrics.day.asc())
        )
        rows = session.execute(stmt).all()

    return [
        {
            "day": d.isoformat(),
            "pm25_max": float(pm) if pm is not None else None,
            "bad_day": int(bd or 0),
        }
        for d, pm, bd in rows
    ]


@router.get("/map")
def locations_map():
    """All monitored locations with lat/lon and current AQI band for map display."""
    with Session(engine) as session:
        locations = session.query(Location).order_by(Location.name).all()
        latest_by_loc = get_latest_pm25_per_location(session)

    out = []
    for loc in locations:
        latest_pm25 = latest_by_loc.get(loc.id)
        aqi_info = pm25_to_aqi(latest_pm25)
        out.append({
            "id": loc.id,
            "name": loc.name,
            "state": loc.state,
            "country": loc.country,
            "lat": loc.lat,
            "lon": loc.lon,
            "pm25": latest_pm25,
            "aqi": aqi_info["aqi"] if aqi_info else None,
            "band": aqi_info["band"] if aqi_info else "No data",
            "color": aqi_info["color"] if aqi_info else "#888888",
        })
    return out