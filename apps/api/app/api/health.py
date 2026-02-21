from fastapi import APIRouter

from app.db.session import db_ping

router = APIRouter(tags=["health"])

@router.get("/healthz")
def healthz():
  return {"status":"ok"}

@router.get("/readyz")
def readyz():
  ok=db_ping()
  return {"status":"ok" if ok else "error","db":ok}