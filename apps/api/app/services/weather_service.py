from datetime import datetime , timezone
from typing import Any

def normalize_weather_hourly(payload: dict[str,Any]):
  h=payload.get("hourly") or {}
  times = h.get("time") or []
  temps=h.get("temperature_2m") or []
  hums=h.get("relative_humidity_2m") or []
  winds = h.get("wind_speed_10m") or []

  out =[]
  for i,t in enumerate(times):
    dt = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
    out.append({
      "t":dt.isoformat(),
      "temp_c": temps[i] if i<len(temps) else None,
      "rh": hums[i] if i<len(hums) else None,
      "wind_kmh": winds[i] if i<len(winds) else None,
    })
  return out