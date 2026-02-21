from datetime import datetime,timedelta,timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.aq_measurement import AQMeasurement

def get_pm25_series(session:Session,location_id:int,hours:int=24):
  since = datetime.now(timezone.utc)-timedelta(hours=hours)

  stmt = (
    select(AQMeasurement.timestamp_utc,AQMeasurement.value,AQMeasurement.unit)
    .where(AQMeasurement.location_id==location_id)
    .where(AQMeasurement.parameter=="pm25")
    .where(AQMeasurement.timestamp_utc>=since)
    .order_by(AQMeasurement.timestamp_utc.asc())
  )
  rows = session.execute(stmt).all()
  return[{"t":ts.isoformat(),"v":float(val),"unit":unit} for (ts,val,unit) in rows]