from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select,func

from app.db.session import engine
from app.models.daily_metrics import DailyMetrics
from app.models.location import Location

router = APIRouter(prefix="/summary", tags=["summary"])

@router.get("/bad-days")
def bad_days(days:int=30):
  """
  Returns bad_day count per location
  """

  with Session(engine) as session:
    latest_day = session.execute(select(func.max(DailyMetrics.day))).scalar_one_or_none()
    if not latest_day:
      return []
    from datetime import timedelta
    start_day = latest_day - timedelta(days=days)

    stmt = (
      select(
        Location.id,
        Location.name,
        Location.state,
        func.sum(DailyMetrics.bad_day).label("bad_days"),
        func.max(DailyMetrics.pm25_max).label("max_pm25"),
      )
    .join(Location,Location.id==DailyMetrics.location_id)
    .where(DailyMetrics.day>=start_day)
    .group_by(Location.id,Location.name,Location.state)
    .order_by(func.sum(DailyMetrics.bad_day).desc())
    )

    rows = session.execute(stmt).all()
  
  return [
    {
      "location_id": rid,
      "name":name,
      "state":state,
      "bad_days":int(bad_days or 0),
      "max_pm25":float(max_pm25) if max_pm25 is not None else None,
      "window_days":days,
    }
    for rid,name,state,bad_days,max_pm25 in rows
  ]

@router.get("/bad-days-trend")
def bad_days_trend(location_id:int, days:int =90):
  """
  Trend of bad_day over time
  """
  from datetime import timedelta
  with Session(engine) as session:
    latest_day = session.execute(select(func.max(DailyMetrics.day))).scalar_one_or_none()
    if not latest_day:
      return []
    
    start_day = latest_day - timedelta(days=days)

    stmt = (
      select(DailyMetrics.day,DailyMetrics.bad_day,DailyMetrics.pm25_max)
      .where(DailyMetrics.location_id == location_id)
      .where(DailyMetrics.day>=start_day)
      .order_by(DailyMetrics.day.asc())
    )
    rows = session.execute(stmt).all()

  return [{"day":d.isoformat(),"bad_day":int(b),"pm25_max":float(mx) if mx is not None else None} for d,b,mx in rows]