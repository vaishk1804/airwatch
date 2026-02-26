from datetime import datetime,timezone

from typing import Any

def normalize_pm25_hourly(payload:dict[str,Any]):
  h=payload.get("hourly") or []
  times=h.get("time") or []
  vals = h.get("pm2_5") or []

  out = []
  for i,t in enumerate(times):
    if i>= len(vals):
      break
    v=vals[i]
    if v is None:
      continue
    dt=datetime.fromisoformat(t).replace(tzinfo=datetime.utc)
    out.append({"t":dt.isoformat(),"v":float(v),"unit":"µg/m³"})
  return out
