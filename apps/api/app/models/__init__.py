"""
Re-export every ORM model so SQLAlchemy's `Base.metadata` knows about all
tables when Alembic runs `--autogenerate`. Each import has a side effect
of registering its mapped class with the shared `Base.metadata`, which is
why these "unused" imports must stay.
"""
from .aq_measurement import AQMeasurement
from .daily_metrics import DailyMetrics
from .location import Location
from .subscription import Subscription
from .weather_hourly import WeatherHourly

__all__ = [
    "AQMeasurement",
    "DailyMetrics",
    "Location",
    "Subscription",
    "WeatherHourly",
]
