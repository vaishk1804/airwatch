import httpx

AIR_BASE = "https://air-quality-api.open-meteo.com/v1"

async def fetch_pm25_hourly(lat:float,lon:float,hours:int = 24):
  past_days = 1 if hours<=24 else 2 if hours<=48 else 7

  params = {
    "latitude":lat,
    "longitude": lon,
    "hourly":"pm2_5",
    "past_days":past_days,
    "timezone":"UTC",
  }

  async with httpx.AsyncClient(timeout=30) as client:
    r = await client.get(f"{AIR_BASE}/air-quality",params=params)
    r.raise_for_status()
    return r.json()