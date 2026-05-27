"""
AQI conversion for PM2.5, per the US EPA's piecewise-linear formula.

Reference:
    https://www.airnow.gov/aqi/aqi-basics/

The EPA defines AQI by interpolating linearly between published breakpoints
that map concentration ranges to AQI ranges. Each band has its own color,
used in every official AirNow map and in our dashboard.
"""
from typing import TypedDict


class AQIResult(TypedDict):
    aqi: int
    band: str
    color: str
    advice: str


# (conc_low, conc_high, aqi_low, aqi_high, band, color, advice)
# Concentrations in µg/m³; AQI integer scale.
_PM25_BREAKPOINTS = [
    (0.0,   12.0,    0,  50,  "Good",                            "#00e400", "Air quality is satisfactory."),
    (12.1,  35.4,   51, 100,  "Moderate",                        "#ffff00", "Unusually sensitive people should consider limiting prolonged outdoor exertion."),
    (35.5,  55.4,  101, 150,  "Unhealthy for Sensitive Groups",  "#ff7e00", "Sensitive groups should limit prolonged outdoor exertion."),
    (55.5, 150.4,  151, 200,  "Unhealthy",                       "#ff0000", "Everyone may begin to experience health effects."),
    (150.5, 250.4, 201, 300,  "Very Unhealthy",                  "#8f3f97", "Health alert: serious health effects for everyone."),
    (250.5, 500.4, 301, 500,  "Hazardous",                       "#7e0023", "Health warning of emergency conditions."),
]


def pm25_to_aqi(concentration_ugm3: float | None) -> AQIResult | None:
    """Convert a PM2.5 concentration (µg/m³) into EPA AQI + band metadata.

    Returns None for null input. Concentrations above the maximum table
    value are clamped to the Hazardous band ceiling (AQI 500).
    """
    if concentration_ugm3 is None:
        return None

    c = max(0.0, float(concentration_ugm3))

    for c_lo, c_hi, i_lo, i_hi, band, color, advice in _PM25_BREAKPOINTS:
        if c <= c_hi:
            # Linear interpolation: I = (I_hi - I_lo) / (C_hi - C_lo) * (C - C_lo) + I_lo
            aqi = round((i_hi - i_lo) / (c_hi - c_lo) * (c - c_lo) + i_lo)
            return AQIResult(aqi=aqi, band=band, color=color, advice=advice)

    # Above the hazardous ceiling — clamp.
    _, _, _, i_hi, band, color, advice = _PM25_BREAKPOINTS[-1]
    return AQIResult(aqi=i_hi, band=band, color=color, advice=advice)