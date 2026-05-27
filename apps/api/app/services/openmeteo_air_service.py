from datetime import UTC, datetime
from typing import Any


def normalize_pm25_hourly(payload: dict[str, Any]):
    """
    Open-Meteo air-quality returns hourly arrays in `payload["hourly"]`
    with parallel `time` and `pm2_5` lists.
    """
    h = payload.get("hourly") or {}
    times = h.get("time") or []
    vals = h.get("pm2_5") or []

    out = []
    for i, t in enumerate(times):
        if i >= len(vals):
            break
        v = vals[i]
        if v is None:
            continue
        dt = datetime.fromisoformat(t).replace(tzinfo=UTC)
        out.append({"t": dt.isoformat(), "v": float(v), "unit": "µg/m³"})
    return out
