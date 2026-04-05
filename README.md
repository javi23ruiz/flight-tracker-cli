# Flight Tracker CLI

A command-line tool for tracking flights in real time using the [OpenSky Network](https://opensky-network.org) API. No API key required.

## Setup

```bash
pip install flight-tracker-cli
```

That's it — works out of the box.

## Commands

### Track an aircraft

```bash
flight-tracker aircraft EK203
flight-tracker aircraft BAW117 --format json
```

### Aircraft overhead

```bash
flight-tracker overhead --lat 25.2048 --lon 55.3657
flight-tracker overhead --lat 51.4775 --lon -0.4614 --radius 100
flight-tracker overhead --lat 40.6413 --lon -73.7781 --format json
```

## Try asking (AI agent use case)

If you have flight-tracker installed as an OpenClaw skill, try natural language:

- "Where is flight EK203 right now?"
- "Is QR42 in the air?"
- "What's flying over me?"
- "Show me aircraft near London Heathrow"

## OpenClaw / ClawHub

Install as a skill for any OpenClaw-compatible agent:

```
claw install flight-tracker
```

The skill auto-triggers on flight numbers, callsigns, and tracking phrases.

## Rate Limits

The OpenSky free tier allows one request every 10 seconds. The CLI handles this automatically with exponential backoff retries (configurable with `--retries`).

## Global Options

| Option      | Default | Description                  |
|-------------|---------|------------------------------|
| `--retries` | 3       | Number of retries on failure |
| `--timeout` | 20      | Request timeout in seconds   |

## License

MIT
