"""Tests for overhead module."""

import responses

from flight_tracker_cli.overhead import _bounding_box, get_overhead

MOCK_STATES = {
    "time": 1700000000,
    "states": [
        [
            "a12345", "EK203   ", "United Arab Emirates", 1700000000,
            1700000000, 55.3, 25.2, 10973.0,
            False, 245.5, 128.0, 0.0,
            None, 11100.0, "1234", False, 0,
        ],
        [
            "ground1", "TAXI1   ", "United Arab Emirates", 1700000000,
            1700000000, 55.4, 25.3, 0.0,
            True, 5.0, 90.0, 0.0,
            None, 0.0, None, False, 0,
        ],
    ],
}


def test_bounding_box_known_values():
    bbox = _bounding_box(25.2048, 55.3657, 50.0)
    assert bbox["lamin"] < "25.2048"
    assert bbox["lamax"] > "25.2048"
    assert bbox["lomin"] < "55.3657"
    assert bbox["lomax"] > "55.3657"
    # Verify reasonable delta (~0.45 degrees for 50km)
    lat_delta = float(bbox["lamax"]) - float(bbox["lamin"])
    assert 0.8 < lat_delta < 1.0


@responses.activate
def test_get_overhead_filters_ground(monkeypatch):
    monkeypatch.setattr(
        "flight_tracker_cli.overhead.get_headers", lambda: {"Authorization": "Bearer fake"}
    )
    responses.add(
        responses.GET,
        "https://opensky-network.org/api/states/all",
        json=MOCK_STATES,
        status=200,
    )
    states = get_overhead(25.2, 55.3, 50.0, retries=1, timeout=5)
    # Only the airborne aircraft should be returned
    assert len(states) == 1
    assert states[0]["callsign"].strip() == "EK203"
