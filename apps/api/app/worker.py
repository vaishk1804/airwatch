from celery import Celery

from app.core.config import settings

celery_app = Celery(
  "airwatch",
  broker=settings.REDIS_URL,
  backend=settings.REDIS_URL,
)

celery_app.conf.update(
  task_serializer="json",
  accept_content=["json"],
  result_serializer="json",
  timezone="UTC",
  enable_utc=True,
)

celery_app.conf.beat_schedule = {
"ingest-air-hourly":{
  "task":"app.tasks.ingest_air_task",
  "schedule": 60*60,
  "args":(24,),
},
"ingest_weather_hourly":{
  "task": "app.tasks.ingest_weather_task",
  "schedule": 60*60,
  "args": (24,),
},
"aggregate-daily-nightly":{
  "task": "app.tasks.aggregate_daily_task",
  "schedule": 60*60*6,
  "args":(30,35.0),
},
"send-alerts-daily":{
  "task":"app.tasks.send_alerts_task",
  "schedule": 60*60*24,
  "args":(35.0,),
},
}

celery_app.autodiscover_tasks(["app"])