from fastapi import APIRouter
from app.jobs.ingest_air import ingest_pm25_for_all

router = APIRouter(prefix="/admin",tags=["admin"])

@router.post("/ingest/air")
async def ingest_air(hours:int=24):
  return await ingest_pm25_for_all(hours=hours)