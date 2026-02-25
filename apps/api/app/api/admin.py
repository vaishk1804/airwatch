from fastapi import APIRouter
from app.jobs.ingest_air import ingest_pm25_for_all
from app.jobs.ingest_weather import ingest_weather_for_all
from app.jobs.aggregate_daily import aggregate_daily_for_all
from app.tasks import send_alerts_task

router = APIRouter(prefix="/admin",tags=["admin"])

@router.post("/ingest/air")
async def ingest_air(hours:int=24):
  return await ingest_pm25_for_all(hours=hours)

@router.post("/ingest/weather")
async def ingest_weather(hours:int =24):
  return await ingest_weather_for_all(hours=hours)

@router.post("/aggregate/daily")
def aggregate_daily(days: int = 7, threshold: float = 35.0):
  return aggregate_daily_for_all(days=days,threshold=threshold)

@router.post("/alerts/send")
def alerts_send(threshold:float = 35.0):
  job = send_alerts_task.delay(threshold)
  return {"task_id":job.id}