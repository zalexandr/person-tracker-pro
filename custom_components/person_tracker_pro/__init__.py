"""Person Tracker PRO integration."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_PRIVACY_MODE,
    DOMAIN,
    PLATFORMS,
    SERVICE_RECALCULATE,
    SERVICE_REQUEST_LOCATION,
    SERVICE_SET_PRIVACY,
    PrivacyMode,
)
from .coordinator import PersonTrackerCoordinator


type PersonTrackerConfigEntry = ConfigEntry[PersonTrackerCoordinator]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
SERVICE_SCHEMA = vol.Schema({vol.Optional("entry_id"): cv.string})
PRIVACY_SCHEMA = vol.Schema(
    {
        vol.Required("mode"): vol.In([mode.value for mode in PrivacyMode]),
        vol.Optional("entry_id"): cv.string,
    }
)
CARD_VERSION = "0.4.4"
CARD_URL = f"/api/person_tracker_pro/person-tracker-pro-card-loader.js?v={CARD_VERSION}"
WWW_PATH = Path(__file__).parent / "www"
CARD_PATH = WWW_PATH / "person-tracker-pro-card-loader.js"


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up domain services and frontend resources."""
    if CARD_PATH.is_file():
        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARD_URL.split("?", 1)[0], str(CARD_PATH), cache_headers=False)]
        )
        add_extra_js_url(hass, CARD_URL)

    async def _targets(call: ServiceCall) -> AsyncIterator[tuple[str, PersonTrackerCoordinator]]:
        entry_id = call.data.get("entry_id")
        for current_id, coordinator in hass.data.get(DOMAIN, {}).items():
            if not entry_id or current_id == entry_id:
                yield current_id, coordinator

    async def request_location(call: ServiceCall) -> None:
        async for _, coordinator in _targets(call):
            await coordinator.async_request_location()

    async def recalculate(call: ServiceCall) -> None:
        async for _, coordinator in _targets(call):
            await coordinator.async_recalculate()

    async def set_privacy(call: ServiceCall) -> None:
        mode = call.data["mode"]
        async for entry_id, coordinator in _targets(call):
            coordinator.config[CONF_PRIVACY_MODE] = mode
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry is not None:
                hass.config_entries.async_update_entry(
                    entry, options={**entry.options, CONF_PRIVACY_MODE: mode}
                )
            await coordinator.async_refresh()

    hass.services.async_register(DOMAIN, SERVICE_REQUEST_LOCATION, request_location, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_RECALCULATE, recalculate, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_PRIVACY, set_privacy, schema=PRIVACY_SCHEMA)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: PersonTrackerConfigEntry) -> bool:
    coordinator = PersonTrackerCoordinator(hass, {**entry.data, **entry.options})
    entry.runtime_data = coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PersonTrackerConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded
