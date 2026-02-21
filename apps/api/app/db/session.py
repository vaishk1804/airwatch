from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings

engine: Engine = create_engine(settings.DATABASE_URL, pool_pre_ping = True)

def db_ping() -> bool:
  """Return True if DB is reachable"""
  try:
    with engine.connect() as conn:
      conn.execute(text("Select 1"))
    return True
  except Exception as e:
    print(f"DB ping failed: {e}")
    return False