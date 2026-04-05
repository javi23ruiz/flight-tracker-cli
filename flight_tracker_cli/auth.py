"""Request helpers for the OpenSky API (anonymous access)."""

import time

import click
import requests


def get_headers() -> dict:
    """Return empty headers — anonymous access, no auth required."""
    return {}


def _request_with_retry(
    url: str,
    headers: dict,
    retries: int,
    timeout: int,
    params: dict | None = None,
) -> dict:
    """GET request with exponential backoff on 429/5xx."""
    last_error: str | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=timeout)
            if resp.status_code == 429:
                last_error = "rate limited (HTTP 429)"
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as exc:
            last_error = str(exc)
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise click.ClickException(f"Request failed after {retries} retries: {last_error}")
