from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.location import Location
from app.repositories.aq_repo import get_pm25_series
from app.clients.openmeteo_client import fetch_weather_hourly
from app.services.weather_service import normalize_weather_hourly
from app.services.insights_service import summarize_pm25,align_series_by_time,correlation_insights

router = APIRouter(prefix="/dashboard",tags=["dashboard"])

@router.get("/location/{location_id}")
async def dashboard_location(
  location_id:int,
  hours:int=24,
  bad_threshold:float = 25.0,
  ):
  with Session(engine) as session:
    loc = session.query(Location).filter(Location.id ==location_id).first()
    if not loc:
      raise HTTPException(status_code=404, detail="Location not found")
    
    pm25 = get_pm25_series(session,location_id=location_id,hours=hours)
  
  weather_raw = await fetch_weather_hourly(loc.lat,loc.lon,hours=hours)
  weather = normalize_weather_hourly(weather_raw)

  metrics=summarize_pm25(pm25,bad_threshold=bad_threshold)
  aligned=align_series_by_time(pm25,weather)
  corr=correlation_insights(aligned)

  return{
    "location": {"id":loc.id,"name":loc.name,"state":loc.state,"country":loc.country,"lat":loc.lat,"lon":loc.lon},
    "hours":hours,
    "pm25":pm25,
    "weather":weather,
    "metrics":metrics,
    "aligned":aligned,
    "correlation":corr,
  }
