"""CLI entrypoint for flight-tracker."""

import json

import click

from .aircraft import find_aircraft, format_aircraft
from .overhead import get_overhead, format_overhead


@click.group()
@click.option("--retries", default=3, type=int, help="Number of retries on failure.")
@click.option("--timeout", default=20, type=int, help="Request timeout in seconds.")
@click.pass_context
def cli(ctx: click.Context, retries: int, timeout: int) -> None:
    """Flight Tracker CLI — track flights using the OpenSky Network API."""
    ctx.ensure_object(dict)
    ctx.obj["retries"] = retries
    ctx.obj["timeout"] = timeout


# ── aircraft ──────────────────────────────────────────────────────────────

@cli.command()
@click.argument("callsign")
@click.option("--format", "fmt", type=click.Choice(["summary", "json"]), default="summary")
@click.pass_context
def aircraft(ctx: click.Context, callsign: str, fmt: str) -> None:
    """Track a single aircraft by callsign (e.g. EK203)."""
    try:
        state = find_aircraft(callsign, ctx.obj["retries"], ctx.obj["timeout"])
    except click.ClickException:
        raise
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if state is None:
        raise click.ClickException(
            f"Aircraft with callsign '{callsign.upper()}' not found. "
            "It may not be airborne or the callsign may differ from the flight number."
        )

    if fmt == "json":
        click.echo(json.dumps(state, indent=2))
    else:
        click.echo(format_aircraft(state))


# ── overhead ──────────────────────────────────────────────────────────────

@cli.command()
@click.option("--lat", required=True, type=float, help="Latitude.")
@click.option("--lon", required=True, type=float, help="Longitude.")
@click.option("--radius", default=50, type=float, help="Radius in km (default 50).")
@click.option("--format", "fmt", type=click.Choice(["summary", "json"]), default="summary")
@click.pass_context
def overhead(ctx: click.Context, lat: float, lon: float, radius: float, fmt: str) -> None:
    """Show aircraft currently overhead a location."""
    try:
        states = get_overhead(lat, lon, radius, ctx.obj["retries"], ctx.obj["timeout"])
    except click.ClickException:
        raise
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if fmt == "json":
        click.echo(json.dumps(states, indent=2))
    else:
        click.echo(format_overhead(states, lat, lon, radius))


if __name__ == "__main__":
    cli()
