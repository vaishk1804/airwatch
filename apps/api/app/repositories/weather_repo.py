"""
Weather repository — reads weather hourly readings from the DB.

The `weather_hourly` table is populated by the `ingest_weather_for_all`
job (run hourly by Celery beat). Dashboard reads here instead of calling
Open-Meteo synchronously, which keeps p95 stable under load.
"""
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.weather_hourly import WeatherHourly


def get_weather_series(session: Session, location_id: int, hours: int = 24):
    since = datetime.now(UTC) - timedelta(hours=hours)
    stmt = (
        select(
            WeatherHourly.timestamp_utc,
            WeatherHourly.temp_c,
            WeatherHourly.rh,
            WeatherHourly.wind_kmh,
        )
        .where(WeatherHourly.location_id == location_id)
        .where(WeatherHourly.timestamp_utc >= since)
        .order_by(WeatherHourly.timestamp_utc.asc())
    )
    rows = session.execute(stmt).all()
    return [
        {
            "t": ts.isoformat(),
            "temp_c": float(temp_c) if temp_c is not None else None,
            "rh": float(rh) if rh is not None else None,
            "wind_kmh": float(wind_kmh) if wind_kmh is not None else None,
        }
        for ts, temp_c, rh, wind_kmh in rows
    ]
