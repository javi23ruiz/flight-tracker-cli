"""Track a single aircraft by callsign."""

import json
from datetime import datetime, timezone

import click

from .auth import _request_with_retry, get_headers

STATE_FIELDS = (
    "icao24", "callsign", "origin_country", "time_position",
    "last_contact", "longitude", "latitude", "baro_altitude",
    "on_ground", "velocity", "true_track", "vertical_rate",
    "sensors", "geo_altitude", "squawk", "spi", "position_source",
)

API_URL = "https://opensky-network.org/api/states/all"


def find_aircraft(callsign: str, retries: int, timeout: int) -> dict | None:
    try:
        data = _request_with_retry(API_URL, get_headers(), retries, timeout)
    except click.ClickException:
        raise
    except Exception as exc:
        raise click.ClickException(f"Failed to fetch aircraft data: {exc}") from exc

    states = data.get("states") or []
    target = callsign.strip().upper()
    for state in states:
        if state[1] and state[1].strip().upper() == target:
            return dict(zip(STATE_FIELDS, state))
    return None


def _heading_label(degrees: float | None) -> str:
    if degrees is None:
        return "N/A"
    buckets = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((degrees + 22.5) % 360 / 45)
    return buckets[idx]


def format_aircraft(state: dict) -> str:
    callsign = (state["callsign"] or "").strip() or "N/A"
    country = state["origin_country"] or "Unknown"
    lat = state["latitude"]
    lon = state["longitude"]
    alt_m = state["baro_altitude"]
    vel_ms = state["velocity"]
    track = state["true_track"]
    vrate = state["vertical_rate"]
    on_ground = state["on_ground"]
    last_contact = state["last_contact"]

    alt_ft = f"{alt_m * 3.28084:,.0f} ft" if alt_m is not None else "N/A"
    speed_kts = f"{vel_ms * 1.94384:,.0f} kts" if vel_ms is not None else "N/A"
    heading_str = f"{track:.0f}° ({_heading_label(track)})" if track is not None else "N/A"

    if vrate is not None:
        vrate_fpm = vrate * 196.85
        if abs(vrate_fpm) < 100:
            vs_label = f"{vrate_fpm:,.0f} fpm  (cruising)"
        elif vrate_fpm > 0:
            vs_label = f"{vrate_fpm:+,.0f} fpm  (climbing)"
        else:
            vs_label = f"{vrate_fpm:+,.0f} fpm  (descending)"
    else:
        vs_label = "N/A"

    if lat is not None and lon is not None:
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        pos_str = f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"
    else:
        pos_str = "N/A"

    if last_contact is not None:
        age = int(datetime.now(timezone.utc).timestamp()) - int(last_contact)
        updated = f"{age}s ago"
    else:
        updated = "N/A"

    ground_str = "Yes" if on_ground else "No"

    lines = [
        f"\u2708  {callsign}  ({country})",
        f"   Position : {pos_str}",
        f"   Altitude : {alt_ft}",
        f"   Speed    : {speed_kts}",
        f"   Heading  : {heading_str}",
        f"   V/S      : {vs_label}",
        f"   On ground: {ground_str}",
        f"   Updated  : {updated}",
    ]
    return "\n".join(lines)
