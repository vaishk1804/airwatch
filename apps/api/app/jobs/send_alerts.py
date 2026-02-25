from sqlalchemy.orm import Session
from sqlalchemy import select,func

from app.db.session import engine
from app.models.subscription import Subscription
from app.models.daily_metrics import DailyMetrics
from app.models.location import Location
from app.utils.emailer import send_email

def send_alerts(threshold:float = 35.0):
  """
  Sends a daily digest if the latest day is a bad day or pm25>=threshold
  """
  with Session(engine) as session:
    latest_day = session.execute(select(func.max(DailyMetrics.day))).scalar_one_or_none()
    if not latest_day:
      return {"sent":0,"reason":"no daily metrics yet"}
    
    subs = session.query(Subscription).filter(Subscription.is_active==1).all()
    sent = 0

    for s in subs:
      dm = session.query(DailyMetrics).filter(
        DailyMetrics.location_id==s.location_id,
        DailyMetrics.day==latest_day
      ).first()

      if not dm:
        continue

      th = s.threshold or threshold
      is_bad = (dm.pm25_max is not None and dm.pm25_max>=th) or dm.bad_day == 1

      if not is_bad:
        continue

      loc = session.query(Location).filter(Location.id == s.location_id).first()
      loc_name = f"{loc.name},{loc.state}" if loc and loc.state else (loc.name if loc else f"Location {s.location_id}")

      subject = f"AirWatch Alert: Bad air risk for {loc_name}"
      body = (
        f"Location: {loc_name}\n"
        f"Date: {latest_day}\n"
        f"PM2.5 max: {dm.pm25_max}\n"
        f"PM2.5 avg: {dm.pm25_avg}\n"
        f"Threshold: {th}\n"
        f"Bad hours: {dm.bad_hours}\n"
      )

      send_email(s.email,subject,body)
      sent+=1

  return {"sent":sent,"day":str(latest_day)}