"""Config flow."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_ENTITY,
    CONF_ENTER_CONFIRMATION,
    CONF_EXIT_CONFIRMATION,
    CONF_MAX_ACCURACY,
    CONF_MAX_JUMP_METERS,
    CONF_MAX_SPEED_KMH,
    CONF_OFFLINE_TIMEOUT,
    CONF_PERSON_ENTITY,
    CONF_SOURCE_ENTITY,
    CONF_STALE_TIMEOUT,
    CONF_DWELL_TIME,
    DEFAULT_DWELL_TIME,
    DEFAULT_ENTER_CONFIRMATION,
    DEFAULT_EXIT_CONFIRMATION,
    DEFAULT_MAX_ACCURACY,
    DEFAULT_MAX_JUMP_METERS,
    DEFAULT_MAX_SPEED_KMH,
    DEFAULT_OFFLINE_TIMEOUT,
    DEFAULT_STALE_TIMEOUT,
    DOMAIN,
)


class PersonTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle setup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            unique = f"{user_input[CONF_PERSON_ENTITY]}::{user_input[CONF_SOURCE_ENTITY]}"
            await self.async_set_unique_id(unique)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_PERSON_ENTITY],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_PERSON_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="person")
                ),
                vol.Required(CONF_SOURCE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="device_tracker")
                ),
                vol.Optional(CONF_BATTERY_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="battery")
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return PersonTrackerOptionsFlow()


class PersonTrackerOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_MAX_ACCURACY,
                    default=current.get(CONF_MAX_ACCURACY, DEFAULT_MAX_ACCURACY),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_MAX_JUMP_METERS,
                    default=current.get(CONF_MAX_JUMP_METERS, DEFAULT_MAX_JUMP_METERS),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_MAX_SPEED_KMH,
                    default=current.get(CONF_MAX_SPEED_KMH, DEFAULT_MAX_SPEED_KMH),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_ENTER_CONFIRMATION,
                    default=current.get(
                        CONF_ENTER_CONFIRMATION, DEFAULT_ENTER_CONFIRMATION
                    ),
                ): vol.Coerce(int),
                vol.Required(
                    CONF_EXIT_CONFIRMATION,
                    default=current.get(
                        CONF_EXIT_CONFIRMATION, DEFAULT_EXIT_CONFIRMATION
                    ),
                ): vol.Coerce(int),
                vol.Required(
                    CONF_STALE_TIMEOUT,
                    default=current.get(CONF_STALE_TIMEOUT, DEFAULT_STALE_TIMEOUT),
                ): vol.Coerce(int),
                vol.Required(
                    CONF_OFFLINE_TIMEOUT,
                    default=current.get(CONF_OFFLINE_TIMEOUT, DEFAULT_OFFLINE_TIMEOUT),
                ): vol.Coerce(int),
                vol.Required(
                    CONF_DWELL_TIME,
                    default=current.get(CONF_DWELL_TIME, DEFAULT_DWELL_TIME),
                ): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
