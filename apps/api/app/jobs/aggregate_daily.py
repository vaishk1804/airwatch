from datetime import datetime,timedelta,timezone,date
from sqlalchemy.orm import Session
from sqlalchemy import select,func, case
from sqlalchemy.dialects.postgresql import insert

from app.db.session import engine
from app.models.location import Location
from app.models.aq_measurement import AQMeasurement
from app.models.daily_metrics import DailyMetrics

def _to_day(dt):
  return dt.date()

def aggregate_daily_for_all(days:int = 7,threshold:float = 35.0):
  """
  Computing daily avg/max PM2.5 and bad_hours for last N days
  """
  with Session(engine) as session:
    locations = session.query(Location).all()

  total_days=0
  by_city=[]

  for loc in locations:
    with Session(engine) as session:
      latest = session.execute(
        select(func.max(AQMeasurement.timestamp_utc))
        .where(AQMeasurement.location_id==loc.id)
        .where(AQMeasurement.parameter=="pm25")
      ).scalar_one_or_none()

      if not latest:
        by_city.append({"location_id":loc.id,"name":loc.name,"days_upserted":0})
        continue

      start = latest - timedelta(days=days)


      stmt=(
        select(
          func.date_trunc("day",AQMeasurement.timestamp_utc).label("day_ts"),
          func.avg(AQMeasurement.value).label("pm25_avg"),
          func.max(AQMeasurement.value).label("pm25_max"),
          func.sum(case((AQMeasurement.value>=threshold,1),else_=0)).label("bad_hours"),
        )
        .where(AQMeasurement.location_id==loc.id)
        .where(AQMeasurement.parameter=="pm25")
        .where(AQMeasurement.timestamp_utc>=start)
        .group_by("day_ts")
        .order_by("day_ts")
      )

      rows = session.execute(stmt).all()
    
    upserts = []
    for day_ts, avg_v,max_v,bad_hours in rows:
      day = day_ts.date()
      bad_day = 1 if (bad_hours or 0) > 0 else 0
      upserts.append({
        "location_id":loc.id,
        "day": day,
        "pm25_avg": float(avg_v) if avg_v is not None else None,
        "pm25_max": float(max_v) if max_v is not None else None,
        "bad_hours": int(bad_hours or 0),
        "bad_day": int(bad_day),
        "threshold": float(threshold),
      })
    
    if not upserts:
      by_city.append({"location_id":loc.id,"name":loc.name,"days_upserted":0})
      continue

    with Session(engine) as session:
      ins = insert(DailyMetrics).values(upserts)
      ins = ins.on_conflict_do_update(
        constraint="uq_daily_loc_day",
        set_={
          "pm25_avg": ins.excluded.pm25_avg,
          "pm25_max": ins.excluded.pm25_max,
          "bad_hours": ins.excluded.bad_hours,
          "bad_day": ins.excluded.bad_day,
          "threshold": ins.excluded.threshold,
        },
      )
      session.execute(ins)
      session.commit()
    
    total_days+=len(upserts)
    by_city.append({"location_id":loc.id,"name":loc.name,"days_upserted":len(upserts)})

  return {"days_upserted": total_days,"by_city":by_city}