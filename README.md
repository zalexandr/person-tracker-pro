# Person Tracker PRO

Advanced local-first presence and location intelligence for Home Assistant.

## Goals

- Modern ConfigEntry-based Home Assistant integration.
- Multi-source location fusion.
- GPS quality filtering and impossible-jump rejection.
- Zone hysteresis and dwell-time confirmation.
- Presence confidence score.
- Movement classification.
- Stale/offline detection.
- Separate battery sensors.
- RU / UK / PL / EN localization.
- Diagnostics, repairs, services and tests.
- No cloud service is required by the core engine.

> This repository is an initial production-oriented implementation. It is intentionally source-first: the actual phone/location sources remain Home Assistant entities such as `device_tracker.*`. Person Tracker PRO processes those entities instead of replacing Home Assistant's `person` integration.

## Installation

### HACS
This project can be added as a custom HACS repository once published to GitHub.

### Manual
Copy `custom_components/person_tracker_pro` into:

```text
/config/custom_components/person_tracker_pro
```

Restart Home Assistant.

Then:

**Settings → Devices & services → Add integration → Person Tracker PRO**

## Recommended source

Use Home Assistant Companion App `device_tracker` entities as the primary GPS source. OwnTracks and other compatible trackers can also be used when exposed as Home Assistant entities.

## Architecture

```text
Home Assistant device_trackers
          |
          v
     Source adapters
          |
          v
      GPS filter
          |
          v
     Location fusion
          |
          +----> zone engine
          +----> movement engine
          +----> confidence engine
          +----> stale/offline engine
          |
          v
     Person Tracker PRO
          |
          +----> device_tracker
          +----> sensors
          +----> binary sensors
          +----> events
          +----> services
```

## Important design decisions

1. The integration does not store battery on `TrackerEntity`; battery is exposed as a separate sensor.
2. The integration uses the modern ConfigEntry/device-tracker architecture.
3. The engine rejects impossible GPS jumps rather than blindly accepting the newest coordinate.
4. Zone transitions use hysteresis and confirmation time.
5. Raw GPS is kept in runtime memory only by default. Long-term history is left to Home Assistant Recorder.
6. All user-facing text is localized.
7. The core calculation code is pure Python where practical, making it easy to unit-test.

## Initial configuration

A first version uses a source entity and a target Home Assistant person. Multiple source entities can later be attached to the same person.

Example:

- Person: `person.olek`
- GPS source: `device_tracker.olek_phone`
- Battery source: `sensor.olek_phone_battery`
- Home zone: `zone.home`

## Development

Install Home Assistant test dependencies in a development environment, then run:

```bash
pytest -q
python -m script.hassfest
```

For a custom integration, localization files live in `translations/`.

## Roadmap

- [x] Config flow
- [x] Options flow
- [x] GPS filtering
- [x] Confidence engine
- [x] Zone hysteresis
- [x] Movement classification
- [x] Stale/offline state
- [x] RU / UK / PL / EN translations
- [x] Diagnostics
- [x] Repairs
- [x] Services
- [x] Unit tests for pure engines
- [ ] Multi-source UI management
- [ ] Advanced route/ETA provider
- [ ] Companion App adaptive tracking commands
- [ ] HA device automation triggers
- [ ] HACS metadata/brand assets
