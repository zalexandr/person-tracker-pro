# Person Tracker PRO

Advanced local-first presence and location intelligence for Home Assistant.

## What it does

Person Tracker PRO fuses one or more existing Home Assistant `device_tracker.*` entities into a single presence/location intelligence layer for a `person.*` entity. It does not replace Home Assistant's native `person` integration and does not require a cloud service.

Features:

- Multi-source location fusion.
- GPS accuracy filtering and impossible-jump rejection.
- Freshness-first source selection with accuracy tie-breaking.
- Zone/state propagation from the selected tracker.
- Presence confidence score.
- Movement classification.
- Stale/offline detection.
- Runtime privacy modes: `full`, `zone_only`, `private`.
- Separate battery sensor support.
- Diagnostics.
- Config-entry migration and UI reconfiguration.
- Fully visual setup/options selectors in Home Assistant.
- Built-in Person Tracker PRO Lovelace card with graphical card editor.
- RU / UK / PL / EN localization.
- Services for immediate location refresh, recalculation and privacy changes.

## Requirements

- Home Assistant with Config Entries and the `person` integration.
- At least one existing `device_tracker.*` entity containing latitude/longitude attributes.
- Optional battery `sensor.*` entity with device class `battery`.

The integration is a local helper: the source trackers are responsible for obtaining GPS data.

## Installation

### HACS

Add this repository as a custom HACS repository and select **Integration**, or install it after the repository is published in the HACS default store.

### Manual

Copy `custom_components/person_tracker_pro` into:

```text
/config/custom_components/person_tracker_pro
```

Restart Home Assistant, then open:

**Settings → Devices & services → Add integration → Person Tracker PRO**

## Initial setup

Choose:

1. The target Home Assistant person, for example `person.olek`.
2. One or more location sources, for example `device_tracker.olek_phone` and `device_tracker.olek_watch`.
3. Optionally, a battery sensor.

All three choices use Home Assistant's visual entity selectors. A person can only be configured once. Required setup data can later be changed through **Reconfigure** without removing the integration.

## Options

The Options flow is now fully visual. Numeric limits use number controls, Home zone uses a zone selector, and Privacy mode uses a dropdown.

| Option | Purpose |
|---|---|
| Maximum GPS accuracy | Reject fixes worse than the configured accuracy. |
| Maximum GPS jump | Reject implausible movement between samples. |
| Maximum plausible speed | Reject movement that would require an impossible speed. |
| Zone entry/exit confirmation | Delay transitions to avoid GPS jitter. |
| Stale timeout | Mark the location stale after this age. |
| Offline timeout | Mark the source offline after this age. |
| Minimum dwell time | Reserved for confirmed zone dwell logic. |
| Home zone | Zone entity used for distance calculations. |
| Privacy mode | Controls exposure of precise location data. |

## Built-in Lovelace card

Person Tracker PRO 0.2.2 includes its own Lovelace card. The card is automatically registered by the integration, so no manual JavaScript resource or external frontend dependency is required.

In **Dashboard → Edit dashboard → Add card**, select **Person Tracker PRO**. The card has a graphical editor where you can select:

- fused location entity;
- confidence, GPS accuracy and speed sensors;
- active sources and rejected-samples sensors;
- moving, stale and offline binary sensors;
- map visibility, map history and zoom;
- history display.

The card uses Home Assistant's native map implementation and follows the active HA theme.

A standard-card dashboard example remains available at:

`docs/lovelace/person_tracker_pro.yaml`

## Privacy modes

- **full** — coordinates and selected source are available.
- **zone_only** — precise coordinates are hidden; zone-level information remains available.
- **private** — precise location and zone/distance details are hidden.

The privacy service also persists the selected mode in the config entry options.

## Entities

The integration creates a device containing:

- `device_tracker` — fused location.
- Presence confidence sensor.
- GPS accuracy sensor.
- Speed sensor.
- Active-source sensor.
- Rejected-GPS-samples sensor.
- Location-stale binary sensor.
- Location-offline binary sensor.
- Moving binary sensor.

Entity names are translated in English, Polish, Russian and Ukrainian.

## Services

### `person_tracker_pro.request_location`

Immediately refresh the fused location.

Optional field:

```yaml
entry_id: "CONFIG_ENTRY_ID"
```

### `person_tracker_pro.recalculate_presence`

Recalculate the fused state immediately. It accepts the same optional `entry_id` field.

### `person_tracker_pro.set_privacy_mode`

Change and persist the privacy mode.

```yaml
mode: zone_only
entry_id: "CONFIG_ENTRY_ID"
```

Supported modes: `full`, `zone_only`, `private`.

## Data flow

```text
Home Assistant device_trackers
          |
          v
      GPS filtering
          |
          v
   Multi-source fusion
          |
     +----+----+
     |    |    |
   zone movement confidence
     |    |    |
     +----+----+
          |
          v
     Person Tracker PRO
          |
          +----> device_tracker
          +----> sensors
          +----> binary sensors
          +----> diagnostics/services
```

## Troubleshooting

If the fused tracker has no location:

1. Confirm every configured source exists.
2. Confirm the source exposes `latitude` and `longitude` attributes.
3. Check `gps_accuracy` and the configured maximum accuracy.
4. Check the stale/offline binary sensors.
5. Review the integration diagnostics before opening an issue.

If a valid fix is rejected, inspect the configured maximum jump and maximum plausible speed. GPS glitches are deliberately rejected instead of being propagated to the fused tracker.

## Diagnostics and privacy

Diagnostics are designed to avoid exposing raw coordinates. Precise location is kept in runtime state and is not written to the integration's own persistent storage. Home Assistant Recorder controls long-term history according to the user's Recorder configuration.

## Development

Install the Home Assistant test dependencies and run:

```bash
pytest -q
python -m script.hassfest
```

GitHub Actions runs both Hassfest validation and the pytest suite on pushes and pull requests.

For custom integrations, user-facing localization is stored under `custom_components/person_tracker_pro/translations/`.

## Project status

The current release is `v0.2.2`, adding a built-in graphical Lovelace card and fully visual configuration/options controls. The remaining roadmap focuses on advanced route/ETA functionality, adaptive tracking commands and richer Home Assistant automation triggers.
