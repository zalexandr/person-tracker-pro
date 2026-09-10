"""Config flow for Person Tracker PRO."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_ENTITY,
    CONF_DWELL_TIME,
    CONF_ENTER_CONFIRMATION,
    CONF_EXIT_CONFIRMATION,
    CONF_HOME_ZONE,
    CONF_MAX_ACCURACY,
    CONF_MAX_JUMP_METERS,
    CONF_MAX_SPEED_KMH,
    CONF_OFFLINE_TIMEOUT,
    CONF_PERSON_ENTITY,
    CONF_PRIVACY_MODE,
    CONF_SOURCE_ENTITIES,
    CONF_SOURCE_ENTITY,
    CONF_STALE_TIMEOUT,
    DEFAULT_DWELL_TIME,
    DEFAULT_ENTER_CONFIRMATION,
    DEFAULT_EXIT_CONFIRMATION,
    DEFAULT_HOME_ZONE,
    DEFAULT_MAX_ACCURACY,
    DEFAULT_MAX_JUMP_METERS,
    DEFAULT_MAX_SPEED_KMH,
    DEFAULT_OFFLINE_TIMEOUT,
    DEFAULT_STALE_TIMEOUT,
    DOMAIN,
    PrivacyMode,
)


def _source_selector() -> selector.EntitySelector:
    """Build the device tracker selector used by setup and reconfigure."""
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain="device_tracker", multiple=True)
    )


def _setup_schema() -> vol.Schema:
    """Return the schema for required setup data."""
    return vol.Schema(
        {
            vol.Required(CONF_PERSON_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="person")
            ),
            vol.Required(CONF_SOURCE_ENTITIES): _source_selector(),
            vol.Optional(CONF_BATTERY_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="battery")
            ),
        }
    )


class PersonTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle integration setup and reconfiguration."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle initial setup."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_PERSON_ENTITY])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_PERSON_ENTITY], data=user_input
            )
        return self.async_show_form(step_id="user", data_schema=_setup_schema())

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle changes to required source configuration."""
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_PERSON_ENTITY])
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                entry,
                data_updates=user_input,
            )
        current = {**entry.data, **entry.options}
        schema = self.add_suggested_values_to_schema(_setup_schema(), current)
        return self.async_show_form(step_id="reconfigure", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow."""
        return PersonTrackerOptionsFlow()


class PersonTrackerOptionsFlow(config_entries.OptionsFlow):
    """Handle integration options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_MAX_ACCURACY): vol.Coerce(float),
                vol.Required(CONF_MAX_JUMP_METERS): vol.Coerce(float),
                vol.Required(CONF_MAX_SPEED_KMH): vol.Coerce(float),
                vol.Required(CONF_ENTER_CONFIRMATION): vol.Coerce(int),
                vol.Required(CONF_EXIT_CONFIRMATION): vol.Coerce(int),
                vol.Required(CONF_STALE_TIMEOUT): vol.Coerce(int),
                vol.Required(CONF_OFFLINE_TIMEOUT): vol.Coerce(int),
                vol.Required(CONF_DWELL_TIME): vol.Coerce(int),
                vol.Required(CONF_HOME_ZONE): str,
                vol.Required(CONF_PRIVACY_MODE): vol.In(
                    [mode.value for mode in PrivacyMode]
                ),
            }
        )
        defaults = {
            CONF_MAX_ACCURACY: DEFAULT_MAX_ACCURACY,
            CONF_MAX_JUMP_METERS: DEFAULT_MAX_JUMP_METERS,
            CONF_MAX_SPEED_KMH: DEFAULT_MAX_SPEED_KMH,
            CONF_ENTER_CONFIRMATION: DEFAULT_ENTER_CONFIRMATION,
            CONF_EXIT_CONFIRMATION: DEFAULT_EXIT_CONFIRMATION,
            CONF_STALE_TIMEOUT: DEFAULT_STALE_TIMEOUT,
            CONF_OFFLINE_TIMEOUT: DEFAULT_OFFLINE_TIMEOUT,
            CONF_DWELL_TIME: DEFAULT_DWELL_TIME,
            CONF_HOME_ZONE: DEFAULT_HOME_ZONE,
            CONF_PRIVACY_MODE: PrivacyMode.FULL.value,
        }
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, defaults | self.config_entry.options),
        )


async def async_migrate_entry(
    hass, config_entry: config_entries.ConfigEntry
) -> bool:
    """Migrate v1 single-source entries to the v2 multi-source format."""
    if config_entry.version < 2:
        data = dict(config_entry.data)
        source = data.pop(CONF_SOURCE_ENTITY, None)
        if source:
            data[CONF_SOURCE_ENTITIES] = [source]
        hass.config_entries.async_update_entry(config_entry, data=data, version=2)
    return True
