from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.location import Location

SEED = [
     {"name": "Boston", "state": "MA", "country": "US", "lat": 42.3601, "lon": -71.0589},
    {"name": "New York", "state": "NY", "country": "US", "lat": 40.7128, "lon": -74.0060},
    {"name": "Chicago", "state": "IL", "country": "US", "lat": 41.8781, "lon": -87.6298},
    {"name": "San Francisco", "state": "CA", "country": "US", "lat": 37.7749, "lon": -122.4194},
]

with Session(engine) as session:
  for row in SEED:
    exists=session.query(Location).filter(Location.name == row["name"]).first()
    if not exists:
      session.add(Location(**row))
  session.commit()

print("Seeded locations.")