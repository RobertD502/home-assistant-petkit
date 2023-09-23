"""PetKit Component."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LOGGER, PETKIT_COORDINATOR, PLATFORMS, POLLING_INTERVAL, REGION, TIMEZONE, UPDATE_LISTENER
from .coordinator import PetKitDataUpdateCoordinator
from .util import async_validate_api, NoDevicesError


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PetKit from a config entry."""

    coordinator = PetKitDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        PETKIT_COORDINATOR: coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    update_listener = entry.add_update_listener(async_update_options)
    hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER] = update_listener

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload PetKit config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    return unload_ok

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""

    if entry.version == 1:
        email = entry.data[CONF_EMAIL]
        password = entry.data[CONF_PASSWORD]

        LOGGER.debug('Migrating PetKit config entry')
        entry.version = 5

        hass.config_entries.async_update_entry(
            entry,
            data={
                CONF_EMAIL: email,
                CONF_PASSWORD: password,
            },
            options={
                REGION: None,
                TIMEZONE: "Set Automatically",
                POLLING_INTERVAL: 120,
            },
        )
        LOGGER.error("PetKit API has changed. Please reauthenticate and select your country.")

    if entry.version in [2,3]:
        email = entry.data[CONF_EMAIL]
        password = entry.data[CONF_PASSWORD]
        polling_interval = entry.options[POLLING_INTERVAL]

        LOGGER.debug('Migrating PetKit config entry')
        entry.version = 5

        hass.config_entries.async_update_entry(
            entry,
            data={
                CONF_EMAIL: email,
                CONF_PASSWORD: password,
            },
            options={
                REGION: None,
                TIMEZONE: "Set Automatically",
                POLLING_INTERVAL: polling_interval,
            },
        )
        LOGGER.error("PetKit API has changed. Please reauthenticate and select your country.")

    if entry.version == 4:
        email = entry.data[CONF_EMAIL]
        password = entry.data[CONF_PASSWORD]
        region = entry.options[REGION]
        polling_interval = entry.options[POLLING_INTERVAL]

        LOGGER.debug('Migrating PetKit config entry')
        entry.version = 5

        hass.config_entries.async_update_entry(
            entry,
            data={
                CONF_EMAIL: email,
                CONF_PASSWORD: password,
            },
            options={
                REGION: region,
                TIMEZONE: "Set Automatically",
                POLLING_INTERVAL: polling_interval,
            },
        )

    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """ Update options. """

    await hass.config_entries.async_reload(entry.entry_id)
