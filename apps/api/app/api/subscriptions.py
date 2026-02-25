from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.db.session import engine
from app.models.subscription import Subscription

router = APIRouter(prefix="/subscriptions",tags=["subscriptions"])

class SubscribeIn(BaseModel):
  email: EmailStr
  location_id: int
  threshold: float = 35.0

@router.post("")
def subscribe(payload:SubscribeIn):
  with Session(engine) as session:
    stmt = insert(Subscription).values(
      email=str(payload.email).lower(),
      location_id=payload.location_id,
      threshold=payload.threshold,
      is_active=1,
    ).on_conflict_do_update(
      constraint="uq_sub_email_location",
      set_={"threshold":payload.threshold,"is_active":1},
    )
    session.execute(stmt)
    session.commit()
  return {"status":"ok"}

@router.get("")
def list_subscriptions(email:str):
  with Session(engine) as session:
    rows = session.query(Subscription).filter(Subscription.email == email.lower()).all()
  return[{"id":r.id,"email":r.email,"location_id":r.location_id,"threshold":r.threshold,"is_active":bool(r.is_active)} for r in rows]