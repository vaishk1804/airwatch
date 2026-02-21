from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Location(Base):
  __tablename__="locations"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(120),unique=True, index=True)
  country: Mapped[str] = mapped_column(String(2),default="US")
  state: Mapped[str | None] = mapped_column(String(2),nullable=True)
  lat: Mapped[float] = mapped_column(Float)
  lon: Mapped[float] = mapped_column(Float)