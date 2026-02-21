from sqlalchemy import ForeignKey, DateTime, Float, String, UniqueConstraint,Index
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime

from app.db.base import Base

class AQMeasurement(Base):
  __tablename__="aq_measurements"

  id: Mapped[int]=mapped_column(primary_key=True)
  location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), index=True)

  timestamp_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True),index=True)

  parameter: Mapped[str] = mapped_column(String(16))
  value: Mapped[float] = mapped_column(Float)
  unit: Mapped[str] = mapped_column(String(16),default="µg/m³")
  source: Mapped[str] = mapped_column(String(32), default="openaq")

  __table_args__ = (
    UniqueConstraint("location_id","timestamp_utc","parameter","source",name="uq_aq"),
    Index("ix_aq_loc_time","location_id","timestamp_utc"),
  )

