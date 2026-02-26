from app.worker import celery_app

import asyncio

@celery_app.task(name="app.tasks.ingest_air_task",autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def ingest_air_task(hours:int = 24):
  from app.jobs.ingest_air import ingest_pm25_for_all
  return asyncio.run(ingest_pm25_for_all(hours=hours))

@celery_app.task(name="app.tasks.ingest_weather_task",autoretry_for=(Exception,),retry_backoff=True,max_retries=3)
def ingest_weather_task(hours: int = 24):
  from app.jobs.ingest_weather import ingest_weather_for_all
  return asyncio.run(ingest_weather_for_all(hours=hours))

@celery_app.task(name="app.tasks.aggregate_daily_task")
def aggregate_daily_task(days:int = 30,threshold:float=35.0):
  from app.jobs.aggregate_daily import aggregate_daily_for_all
  return aggregate_daily_for_all(days=days,threshold=threshold)

@celery_app.task(name="app.tasks.send_alerts_task")
def send_alerts_task(threshold:float = 35.0):
  from app.jobs.send_alerts import send_alerts
  return send_alerts(threshold=threshold)
