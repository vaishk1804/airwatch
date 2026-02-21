from datetime import datetime,timezone
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.db.session import engine
from app.models.location import Location
from app.models.aq_measurement import AQMeasurement

from app.clients.openaq_client import fetch_pm25_hourly as fetch_openaq_pm25_hourly

from app.clients.openmeteo_air_client import fetch_pm25_hourly as fetch_openmeteo_pm25_hourly
from app.services.openmeteo_air_service import normalize_pm25_hourly


async def ingest_pm25_for_all(hours:int =24):
  with Session(engine) as session:
    locations = session.query(Location).all()

  total=0
  by_city=[]

  for loc in locations:
    rows = []
    source_used="openaq"

    try:
      data = await fetch_openaq_pm25_hourly(loc.lat,loc.lon,hours=hours)
      for item in data.get("results", []):
        period = item.get("period") or {}
        dt_from = (period.get("datetimeFrom") or {}).get("utc")
        if not dt_from:
          continue

        ts_dt = datetime.fromisoformat(dt_from.replace("Z", "+00:00")).astimezone(timezone.utc)
        rows.append({
        "location_id": loc.id,
        "timestamp_utc": ts_dt,
        "parameter": "pm25",
        "value": float(item["value"]),
        "unit": (item.get("parameter") or {}).get("units", "µg/m³"),
        "source": "openaq",
        })
    except Exception:
      rows = []

    if not rows:
      source_used="openmeteo"
      payload =await fetch_openmeteo_pm25_hourly(loc.lat,loc.lon,hours=hours)
      points = normalize_pm25_hourly(payload)

      for p in points:
        ts_dt = datetime.fromisoformat(p["t"])
        rows.append({
          "location_id":loc.id,
          "timestamp_utc":ts_dt,
          "parameter":"pm25",
          "value":float(p["v"]),
          "unit":p.get("unit","µg/m³"),
          "source":"openmeteo",
        })
    
    if not rows:
      by_city.append({"location_id": loc.id, "name": loc.name, "inserted_attempted": 0, "source": source_used})
      continue

    with Session(engine) as session:
      stmt = insert(AQMeasurement).values(rows)
      stmt=stmt.on_conflict_do_nothing(constraint="uq_aq")
      result=session.execute(stmt)
      session.commit()
    total+=len(rows)
    by_city.append({"location_id": loc.id, "name": loc.name, "inserted_attempted": len(rows), "source": source_used})
  
  return {"inserted_attempted":total}