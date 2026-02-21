import httpx
from datetime import datetime, timedelta, timezone

from app.core.config import settings


def _headers():
    h = {}
    if settings.OPENAQ_API_KEY:
        h["X-API-Key"] = settings.OPENAQ_API_KEY
    return h


async def find_pm25_sensor_id(lat: float, lon: float, radius_km: int = 50) -> int | None:
    """
    1) Find nearby OpenAQ locations
    2) Pick the first location that has a pm25 sensor
    3) Return that pm25 sensor_id
    """
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_km,
        "limit": 10,
        "page": 1,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{settings.OPENAQ_API_BASE}/locations", params=params, headers=_headers())
        r.raise_for_status()
        data = r.json()

    for loc in data.get("results", []):
        for s in loc.get("sensors", []):
            p = s.get("parameter", {})
            if p.get("name") == "pm25":
                return s.get("id")

    return None


async def fetch_pm25_hourly(lat: float, lon: float, hours: int = 24, radius_km: int = 50):
    """
    Uses v3 hourly aggregated endpoint:
    /v3/sensors/{sensors_id}/measurements/hourly
    """
    sensor_id = await find_pm25_sensor_id(lat, lon, radius_km=radius_km)
    if not sensor_id:
        return {"results": []}

    dt_from = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    params = {
        "datetime_from": dt_from,
        "limit": 500,
        "page": 1,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"{settings.OPENAQ_API_BASE}/sensors/{sensor_id}/measurements/hourly",
            params=params,
            headers=_headers(),
        )
        r.raise_for_status()
        return r.json()
