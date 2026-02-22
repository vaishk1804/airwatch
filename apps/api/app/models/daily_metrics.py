from sqlalchemy import ForeignKey,Date, Float, Integer, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date

from app.db.base import Base

class DailyMetrics(Base):
  __tablename__ = "daily_metrics"

  id: Mapped[int] = mapped_column(primary_key=True)
  location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"),index= True)

  day: Mapped[date] = mapped_column(Date,index=True)

  pm25_avg: Mapped[float | None] = mapped_column(Float,nullable = True)
  pm25_max:Mapped[float | None] = mapped_column(Float,nullable=True)
  bad_hours:Mapped[int] = mapped_column(Integer,default= 0 )
  bad_day: Mapped[int] = mapped_column(Integer,default=0)

  threshold: Mapped[float] = mapped_column(Float,default=35.0)

  __table_args__ = (
    UniqueConstraint("location_id","day",name="uq_daily_loc_day"),
    Index("ix_daily_loc_day","location_id","day"),
  )