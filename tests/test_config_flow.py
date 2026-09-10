from homeassistant import config_entries
from homeassistant.const import SOURCE_RECONFIGURE, SOURCE_USER
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.person_tracker_pro.config_flow import async_migrate_entry
from custom_components.person_tracker_pro.const import (
    CONF_PERSON_ENTITY,
    CONF_SOURCE_ENTITIES,
    CONF_SOURCE_ENTITY,
    DOMAIN,
)


async def test_user_flow_creates_entry(hass, enable_custom_integrations):
    """The user flow creates a unique multi-source config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] == config_entries.FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_PERSON_ENTITY: "person.alex",
            CONF_SOURCE_ENTITIES: ["device_tracker.phone", "device_tracker.watch"],
        },
    )

    assert result["type"] == config_entries.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_PERSON_ENTITY] == "person.alex"
    assert result["data"][CONF_SOURCE_ENTITIES] == [
        "device_tracker.phone",
        "device_tracker.watch",
    ]


async def test_reconfigure_updates_existing_entry(hass, enable_custom_integrations):
    """Reconfigure updates data instead of creating a second entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="person.alex",
        data={
            CONF_PERSON_ENTITY: "person.alex",
            CONF_SOURCE_ENTITIES: ["device_tracker.phone"],
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )
    assert result["type"] == config_entries.FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_PERSON_ENTITY: "person.alex",
            CONF_SOURCE_ENTITIES: ["device_tracker.phone", "device_tracker.tablet"],
        },
    )

    assert result["type"] == config_entries.FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_SOURCE_ENTITIES] == [
        "device_tracker.phone",
        "device_tracker.tablet",
    ]


async def test_migrate_v1_source_entity(hass):
    """A v1 single source is migrated to the v2 source list."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={
            CONF_PERSON_ENTITY: "person.alex",
            CONF_SOURCE_ENTITY: "device_tracker.phone",
        },
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 2
    assert entry.data[CONF_SOURCE_ENTITIES] == ["device_tracker.phone"]
    assert CONF_SOURCE_ENTITY not in entry.data
