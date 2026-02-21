from fastapi import APIRouter,HTTPException
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.location import Location

router = APIRouter(prefix="/locations",tags=["locations"])

@router.get("")
def list_locations():
  with Session(engine) as session:
    rows=session.query(Location).order_by(Location.name.asc()).all()
  
  return [
    {"id":r.id,"name":r.name,"state":r.state,"country":r.country,"lat":r.lat,"lon":r.lon}
    for r in rows
  ]

@router.get("/{location_id}")
def get_location(location_id:int):
  with Session(engine) as session:
    r=session.query(Location).filter(Location.id==location_id).first()
    if not r:
      raise HTTPException(status_code=404,detail="Location not found")
  return {"id":r.id,"name":r.name,"state":r.state,"country":r.country,"lat":r.lat,"lon":r.lon}