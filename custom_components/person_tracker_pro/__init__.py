"""Person Tracker PRO integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    PLATFORMS,
    SERVICE_RECALCULATE,
    SERVICE_REQUEST_LOCATION,
    SERVICE_SET_PRIVACY,
)
from .coordinator import PersonTrackerCoordinator

type PersonTrackerConfigEntry = ConfigEntry[PersonTrackerCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: PersonTrackerConfigEntry) -> bool:
    """Set up Person Tracker PRO from a config entry."""
    coordinator = PersonTrackerCoordinator(hass, {**entry.data, **entry.options})
    entry.runtime_data = coordinator

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def request_location(call: ServiceCall) -> None:
        await coordinator.async_request_location()

    async def recalculate(call: ServiceCall) -> None:
        await coordinator.async_request_location()

    async def set_privacy(call: ServiceCall) -> None:
        # Privacy changes are persisted through the options flow in the first
        # release; this service is reserved for runtime extensions.
        return

    hass.services.async_register("person_tracker_pro", SERVICE_REQUEST_LOCATION, request_location)
    hass.services.async_register("person_tracker_pro", SERVICE_RECALCULATE, recalculate)
    hass.services.async_register("person_tracker_pro", SERVICE_SET_PRIVACY, set_privacy)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: PersonTrackerConfigEntry
) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        for service in (
            SERVICE_REQUEST_LOCATION,
            SERVICE_RECALCULATE,
            SERVICE_SET_PRIVACY,
        ):
            if hass.services.has_service("person_tracker_pro", service):
                hass.services.async_remove("person_tracker_pro", service)
    return unloaded
