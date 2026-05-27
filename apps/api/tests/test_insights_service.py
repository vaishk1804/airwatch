"""
Unit tests for insights_service.

Covers: summarize_pm25, _pearson, align_series_by_time, correlation_insights.
These are pure functions, so no DB or HTTP fixtures needed.
"""

import pytest

from app.services.insights_service import (
    _pearson,
    align_series_by_time,
    correlation_insights,
    summarize_pm25,
)

# ----- summarize_pm25 --------------------------------------------------------


def test_summarize_pm25_empty_returns_nulls():
    out = summarize_pm25([], bad_threshold=35.0)
    assert out["latest"] is None
    assert out["avg"] is None
    assert out["max"] is None
    assert out["bad_hours"] == 0
    assert out["count"] == 0
    assert out["threshold"] == 35.0


def test_summarize_pm25_skips_none_values():
    pm = [{"t": "a", "v": None}, {"t": "b", "v": 20.0}, {"t": "c", "v": 50.0}]
    out = summarize_pm25(pm, bad_threshold=35.0)
    # Only the two non-None values count
    assert out["count"] == 2
    assert out["latest"] == 50.0
    assert out["max"] == 50.0
    assert out["avg"] == pytest.approx(35.0)
    assert out["bad_hours"] == 1  # only 50.0 >= 35


def test_summarize_pm25_bad_hours_threshold_inclusive():
    # Exactly-at-threshold counts as bad
    pm = [{"t": "a", "v": 35.0}, {"t": "b", "v": 34.99}]
    out = summarize_pm25(pm, bad_threshold=35.0)
    assert out["bad_hours"] == 1


def test_summarize_pm25_latest_is_last_in_list():
    pm = [{"t": "a", "v": 100.0}, {"t": "b", "v": 5.0}]
    out = summarize_pm25(pm)
    # `latest` is positional, not max — caller is expected to pass sorted data
    assert out["latest"] == 5.0


# ----- _pearson --------------------------------------------------------------


def test_pearson_perfect_positive():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [2.0, 4.0, 6.0, 8.0]
    assert _pearson(xs, ys) == pytest.approx(1.0)


def test_pearson_perfect_negative():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [4.0, 3.0, 2.0, 1.0]
    assert _pearson(xs, ys) == pytest.approx(-1.0)


def test_pearson_insufficient_sample_returns_none():
    assert _pearson([1.0], [2.0]) is None
    assert _pearson([1.0, 2.0], [2.0, 3.0]) is None  # n=2 below floor of 3


def test_pearson_constant_series_returns_none():
    # zero variance -> undefined correlation
    assert _pearson([1.0, 1.0, 1.0, 1.0], [2.0, 3.0, 4.0, 5.0]) is None


# ----- align_series_by_time --------------------------------------------------


def test_align_inner_join_on_timestamp():
    pm = [
        {"t": "2026-05-25T10:00:00+00:00", "v": 12.0},
        {"t": "2026-05-25T11:00:00+00:00", "v": 18.0},
        {"t": "2026-05-25T12:00:00+00:00", "v": 25.0},  # no weather match
    ]
    weather = [
        {"t": "2026-05-25T10:00:00+00:00", "temp_c": 22.0, "rh": 60.0, "wind_kmh": 10.0},
        {"t": "2026-05-25T11:00:00+00:00", "temp_c": 23.0, "rh": 55.0, "wind_kmh": 12.0},
        {"t": "2026-05-25T13:00:00+00:00", "temp_c": 25.0, "rh": 50.0, "wind_kmh": 15.0},  # no pm match
    ]
    aligned = align_series_by_time(pm, weather)
    assert len(aligned) == 2
    assert aligned[0]["t"] == "2026-05-25T10:00:00+00:00"
    assert aligned[0]["pm25"] == 12.0
    assert aligned[0]["temp_c"] == 22.0


def test_align_skips_entries_with_no_timestamp():
    pm = [{"v": 12.0}, {"t": "2026-05-25T10:00:00+00:00", "v": 18.0}]
    weather = [{"t": "2026-05-25T10:00:00+00:00", "temp_c": 22.0, "rh": 60.0, "wind_kmh": 10.0}]
    aligned = align_series_by_time(pm, weather)
    assert len(aligned) == 1


# ----- correlation_insights --------------------------------------------------


def test_correlation_insights_shape():
    rows = [
        {"t": "1", "pm25": 10, "temp_c": 20, "rh": 50, "wind_kmh": 5},
        {"t": "2", "pm25": 20, "temp_c": 21, "rh": 60, "wind_kmh": 4},
        {"t": "3", "pm25": 30, "temp_c": 22, "rh": 70, "wind_kmh": 3},
        {"t": "4", "pm25": 40, "temp_c": 23, "rh": 80, "wind_kmh": 2},
    ]
    out = correlation_insights(rows)
    assert set(out.keys()) == {"temp_c", "rh", "wind_kmh"}
    for stat in out.values():
        assert "n" in stat and "pearson_r" in stat
    # temp_c and rh perfectly co-vary with pm25 -> r ~ 1; wind perfectly anti-covaries -> r ~ -1
    assert out["temp_c"]["pearson_r"] == pytest.approx(1.0)
    assert out["rh"]["pearson_r"] == pytest.approx(1.0)
    assert out["wind_kmh"]["pearson_r"] == pytest.approx(-1.0)


def test_correlation_insights_skips_nulls():
    rows = [
        {"t": "1", "pm25": 10, "temp_c": None, "rh": 50, "wind_kmh": 5},
        {"t": "2", "pm25": 20, "temp_c": 21, "rh": 60, "wind_kmh": 4},
        {"t": "3", "pm25": None, "temp_c": 22, "rh": 70, "wind_kmh": 3},
    ]
    out = correlation_insights(rows)
    # temp_c has 2 valid pairs (rows 2,3 only — row 1 missing temp_c, row 3 missing pm25)
    # rh has 2 valid pairs (rows 1,2 — row 3 missing pm25)
    assert out["temp_c"]["n"] <= 2
    assert out["rh"]["n"] == 2
