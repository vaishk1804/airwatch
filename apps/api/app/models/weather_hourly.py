from sqlalchemy import ForeignKey, DateTime, Float, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base

class WeatherHourly(Base):
  __tablename__= "weather_hourly"

  id: Mapped[int] = mapped_column(primary_key=True)
  location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"),index=True)

  timestamp_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True),index = True)

  temp_c:Mapped[float | None] = mapped_column(Float,nullable=True)
  rh: Mapped[float | None] = mapped_column(Float,nullable = True)
  wind_kmh:Mapped[float | None] = mapped_column(Float,nullable=True)

  __table_args__ = (
    UniqueConstraint("location_id","timestamp_utc",name="uq_weather_loc_time"),
    Index("ix_weather_loc_time","location_id","timestamp_utc"),
  )