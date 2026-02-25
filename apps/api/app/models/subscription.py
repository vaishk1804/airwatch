from sqlalchemy import ForeignKey,String,Float,Integer,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Subscription(Base):
  __tablename__ = "subscriptions"

  id:Mapped[int] = mapped_column(primary_key=True)
  email:Mapped[str] = mapped_column(String(255),index=True)
  location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"),index=True)
  threshold: Mapped[float] = mapped_column(Float,default=35.0)
  is_active: Mapped[int] = mapped_column(Integer,default=1)

  __table_args__ = (
    UniqueConstraint("email","location_id",name="uq_sub_email_location"),
  )