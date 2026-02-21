import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings

_CACHE = {}
_TTL_SECONDS= 600

async def fetch_weather_hourly(lat:float,lon:float,hours:int=24):
  key=(round(lat,4),round(lon,4),hours)
  now=datetime.utcnow().timestamp()

  cached=_CACHE.get(key)
  if cached:
    ts,payload=cached
    if now-ts<_TTL_SECONDS:
      return payload

  past_days = 1 if hours<=24 else 2 if hours <=48 else 7

  params = {
    "latitude":lat,
    "longitude":lon,
    "hourly":"temperature_2m,relative_humidity_2m,wind_speed_10m",
    "past_days":past_days,
    "timezone":"UTC",
  }

  async with httpx.AsyncClient(timeout=30) as client:
    r = await client.get(f"{settings.OPENMETEO_BASE}/forecast",params=params)
    r.raise_for_status()
    payload = r.json()

  _CACHE[key]=(now,payload)
  return payload
   