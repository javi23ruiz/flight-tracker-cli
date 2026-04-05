"""Find aircraft overhead a given location."""

import json
from math import cos, radians

import click

from .auth import _request_with_retry, get_headers
from .aircraft import STATE_FIELDS, format_aircraft

API_URL = "https://opensky-network.org/api/states/all"


def _bounding_box(lat: float, lon: float, radius_km: float) -> dict:
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * cos(radians(lat)))
    return {
        "lamin": str(lat - lat_delta),
        "lamax": str(lat + lat_delta),
        "lomin": str(lon - lon_delta),
        "lomax": str(lon + lon_delta),
    }


def get_overhead(
    lat: float, lon: float, radius_km: float, retries: int, timeout: int
) -> list[dict]:
    bbox = _bounding_box(lat, lon, radius_km)
    data = _request_with_retry(API_URL, get_headers(), retries, timeout, params=bbox)

    states = data.get("states") or []
    airborne = []
    for s in states:
        parsed = dict(zip(STATE_FIELDS, s))
        if not parsed["on_ground"]:
            airborne.append(parsed)

    airborne.sort(key=lambda x: x["baro_altitude"] or 0, reverse=True)
    return airborne


def format_overhead(states: list[dict], lat: float, lon: float, radius_km: float) -> str:
    if not states:
        return "No aircraft detected overhead"

    header = f"{len(states)} aircraft overhead (within {radius_km:.0f} km)\n"
    sep = "-" * 62 + "\n"
    col_header = (
        f"{'Callsign':<12}{'Country':<20}{'Alt (ft)':<12}{'Speed (kts)':<14}{'Heading'}\n"
    )

    rows = []
    for s in states:
        cs = (s["callsign"] or "").strip() or "N/A"
        country = (s["origin_country"] or "")[:18]
        alt_m = s["baro_altitude"]
        vel_ms = s["velocity"]
        track = s["true_track"]

        alt_ft = f"{alt_m * 3.28084:,.0f}" if alt_m is not None else "N/A"
        speed = f"{vel_ms * 1.94384:,.0f}" if vel_ms is not None else "N/A"
        hdg = f"{track:.0f}°" if track is not None else "N/A"

        rows.append(f"{cs:<12}{country:<20}{alt_ft:<12}{speed:<14}{hdg}")

    return header + sep + col_header + sep + "\n".join(rows)
