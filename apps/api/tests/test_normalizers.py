"""
Unit tests for the Open-Meteo response normalizers.

These regression-test the bug fix where datetime.utc (which doesn't exist)
was being used instead of timezone.utc.
"""
from app.services.openmeteo_air_service import normalize_pm25_hourly
from app.services.weather_service import normalize_weather_hourly


def test_normalize_weather_hourly_attaches_utc_tz():
    payload = {
        "hourly": {
            "time": ["2026-05-25T10:00", "2026-05-25T11:00"],
            "temperature_2m": [22.5, 23.0],
            "relative_humidity_2m": [60, 58],
            "wind_speed_10m": [10, 12],
        }
    }
    out = normalize_weather_hourly(payload)
    assert len(out) == 2
    # Critical assertion: timestamps are tz-aware UTC ISO strings
    assert out[0]["t"].endswith("+00:00")
    assert out[0]["temp_c"] == 22.5
    assert out[0]["rh"] == 60
    assert out[0]["wind_kmh"] == 10


def test_normalize_weather_hourly_empty_payload():
    assert normalize_weather_hourly({}) == []
    assert normalize_weather_hourly({"hourly": None}) == []


def test_normalize_weather_hourly_mismatched_array_lengths():
    """If hums runs out before times, downstream values should be None — not crash."""
    payload = {
        "hourly": {
            "time": ["2026-05-25T10:00", "2026-05-25T11:00", "2026-05-25T12:00"],
            "temperature_2m": [22.5, 23.0],
            "relative_humidity_2m": [60],
            "wind_speed_10m": [],
        }
    }
    out = normalize_weather_hourly(payload)
    assert len(out) == 3
    assert out[2]["temp_c"] is None
    assert out[2]["rh"] is None
    assert out[2]["wind_kmh"] is None


def test_normalize_pm25_hourly_filters_nulls():
    payload = {
        "hourly": {
            "time": ["2026-05-25T10:00", "2026-05-25T11:00", "2026-05-25T12:00"],
            "pm2_5": [12.3, None, 18.5],
        }
    }
    out = normalize_pm25_hourly(payload)
    # Null filtered out -> 2 points
    assert len(out) == 2
    assert out[0]["v"] == 12.3
    assert out[1]["v"] == 18.5
    assert out[0]["unit"] == "µg/m³"
    assert out[0]["t"].endswith("+00:00")


def test_normalize_pm25_hourly_empty():
    assert normalize_pm25_hourly({}) == []
    assert normalize_pm25_hourly({"hourly": {"time": [], "pm2_5": []}}) == []
