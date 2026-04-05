"""Tests for aircraft module."""

import json

import responses

from flight_tracker_cli.aircraft import find_aircraft, format_aircraft, STATE_FIELDS

MOCK_STATES = {
    "time": 1700000000,
    "states": [
        [
            "a12345", "EK203   ", "United Arab Emirates", 1700000000,
            1700000000, 55.3657, 25.2048, 10973.0,
            False, 245.5, 128.0, 0.0,
            None, 11100.0, "1234", False, 0,
        ],
        [
            "b67890", "QR42    ", "Qatar", 1700000000,
            1700000000, 51.1, 25.3, 9000.0,
            False, 220.0, 90.0, -5.0,
            None, 9100.0, None, False, 0,
        ],
    ],
}


@responses.activate
def test_find_aircraft_finds_callsign(monkeypatch):
    monkeypatch.setattr(
        "flight_tracker_cli.aircraft.get_headers", lambda: {"Authorization": "Bearer fake"}
    )
    responses.add(
        responses.GET,
        "https://opensky-network.org/api/states/all",
        json=MOCK_STATES,
        status=200,
    )
    result = find_aircraft("EK203", retries=1, timeout=5)
    assert result is not None
    assert result["callsign"].strip() == "EK203"
    assert result["origin_country"] == "United Arab Emirates"


@responses.activate
def test_find_aircraft_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr(
        "flight_tracker_cli.aircraft.get_headers", lambda: {"Authorization": "Bearer fake"}
    )
    responses.add(
        responses.GET,
        "https://opensky-network.org/api/states/all",
        json=MOCK_STATES,
        status=200,
    )
    result = find_aircraft("NOPE99", retries=1, timeout=5)
    assert result is None


def test_format_aircraft_altitude_in_feet():
    state = dict(zip(STATE_FIELDS, [
        "a12345", "EK203   ", "United Arab Emirates", 1700000000,
        1700000000, 55.3657, 25.2048, 10973.0,
        False, 245.5, 128.0, 0.0,
        None, 11100.0, "1234", False, 0,
    ]))
    output = format_aircraft(state)
    # 10973 meters ~ 36,001 feet
    assert "36,001 ft" in output or "36,00" in output
    assert "EK203" in output
    assert "United Arab Emirates" in output
