from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.db.session import engine
from app.models.location import Location
from app.models.weather_hourly import WeatherHourly
from app.clients.openmeteo_client import fetch_weather_hourly
from app.services.weather_service import normalize_weather_hourly

async def ingest_weather_for_all(hours:int=24):
  with Session(engine) as session:
    locations=session.query(Location).all()

  total=0
  by_city=[]

  for loc in locations:
    raw = await fetch_weather_hourly(loc.lat,loc.lon,hours=hours)
    points = normalize_weather_hourly(raw)

    rows=[]
    for p in points:
      ts_dt=datetime.fromisoformat(p["t"]).astimezone(timezone.utc)
      rows.append({
        "location_id":loc.id,
        "timestamp_utc":ts_dt,
        "temp_c":p.get("temp_c"),
        "rh":p.get("rh"),
        "wind_kmh":p.get("wind_kmh"),
      })
    
    if not rows:
      by_city.append({"location_id":loc.id,"name":loc.name,"inserted_attempted":0})
      continue

    with Session(engine) as session:
      stmt=insert(WeatherHourly).values(rows)
      stmt=stmt.on_conflict_do_nothing(constraint="uq_weather_loc_time")
      session.execute(stmt)
      session.commit()

    total+=len(rows)
    by_city.append({"location_id":loc.id,"name":loc.name,"inserted_attemped":len(rows)})
  
  return {"inserted_attempted":total,"by_city":by_city}