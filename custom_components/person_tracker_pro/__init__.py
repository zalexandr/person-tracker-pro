"""Person Tracker PRO integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN, PLATFORMS, SERVICE_RECALCULATE, SERVICE_REQUEST_LOCATION,
    SERVICE_SET_PRIVACY, PrivacyMode,
)
from .coordinator import PersonTrackerCoordinator

type PersonTrackerConfigEntry = ConfigEntry[PersonTrackerCoordinator]

SERVICE_SCHEMA = vol.Schema({vol.Optional("entry_id"): cv.string})
PRIVACY_SCHEMA = vol.Schema({
    vol.Required("mode"): vol.In([mode.value for mode in PrivacyMode]),
    vol.Optional("entry_id"): cv.string,
})

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the domain services once."""
    async def _targets(call: ServiceCall):
        entry_id = call.data.get("entry_id")
        for current_id, coordinator in hass.data.get(DOMAIN, {}).items():
            if entry_id and current_id != entry_id:
                continue
            yield coordinator

    async def request_location(call: ServiceCall) -> None:
        async for coordinator in _targets(call):
            await coordinator.async_request_location()

    async def recalculate(call: ServiceCall) -> None:
        async for coordinator in _targets(call):
            await coordinator.async_recalculate()

    async def set_privacy(call: ServiceCall) -> None:
        async for coordinator in _targets(call):
            coordinator.config["privacy_mode"] = call.data["mode"]
            await coordinator.async_refresh()

    hass.services.async_register(DOMAIN, SERVICE_REQUEST_LOCATION, request_location, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_RECALCULATE, recalculate, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_PRIVACY, set_privacy, schema=PRIVACY_SCHEMA)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: PersonTrackerConfigEntry) -> bool:
    """Set up an entry."""
    coordinator = PersonTrackerCoordinator(hass, {**entry.data, **entry.options})
    entry.runtime_data = coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: PersonTrackerConfigEntry) -> bool:
    """Unload an entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded
