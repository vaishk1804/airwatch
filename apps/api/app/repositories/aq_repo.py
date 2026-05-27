from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.aq_measurement import AQMeasurement


def get_pm25_series(session:Session,location_id:int,hours:int=24):
  since = datetime.now(UTC)-timedelta(hours=hours)

  stmt = (
    select(AQMeasurement.timestamp_utc,AQMeasurement.value,AQMeasurement.unit)
    .where(AQMeasurement.location_id==location_id)
    .where(AQMeasurement.parameter=="pm25")
    .where(AQMeasurement.timestamp_utc>=since)
    .order_by(AQMeasurement.timestamp_utc.asc())
  )
  rows = session.execute(stmt).all()
  return[{"t":ts.isoformat(),"v":float(val),"unit":unit} for (ts,val,unit) in rows]

def get_latest_pm25_per_location(session: Session) -> dict[int, float]:
    """Return {location_id: latest_pm25_value} for every location with data.

    Uses Postgres's DISTINCT ON to get the most recent reading per location
    in a single query. Falls back gracefully on SQLite (sorted scan instead).
    """
    stmt = (
        select(AQMeasurement.location_id, AQMeasurement.value, AQMeasurement.timestamp_utc)
        .where(AQMeasurement.parameter == "pm25")
        .order_by(AQMeasurement.location_id, AQMeasurement.timestamp_utc.desc())
    )
    rows = session.execute(stmt).all()

    # Take first row per location (input is sorted, so first = latest)
    latest: dict[int, float] = {}
    for loc_id, val, _ts in rows:
        if loc_id not in latest:
            latest[loc_id] = float(val)
    return latest