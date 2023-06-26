"""Fan platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import PurifierCommand
from petkitaio.model import Purifier

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    PETKIT_COORDINATOR,
    PURIFIERS,
    PURIFIER_MODES,
    PURIFIER_MODE_NAMED,
    PURIFIER_MODE_TO_COMMAND
)

from .coordinator import PetKitDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Fan Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][PETKIT_COORDINATOR]

    fans = []

    for purifier_id, purifier_data in coordinator.data.purifiers.items():
        fans.append(
            Purifier(coordinator, purifier_id)
        )

    async_add_entities(fans)


class Purifier(CoordinatorEntity, FanEntity):
    """Representation of a PetKit air purifier."""

    def __init__(self, coordinator, purifier_id):
        super().__init__(coordinator)
        self.purifier_id = purifier_id

    @property
    def purifier_data(self) -> Purifier:
        """Handle coordinator Purifier data."""

        return self.coordinator.data.purifiers[self.purifier_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.purifier_data.id)},
            "name": self.purifier_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": PURIFIERS[self.purifier_data.type],
            "sw_version": f'{self.purifier_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.purifier_data.id) + '_purifier'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "purifier"

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.purifier_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    @property
    def is_on(self) -> bool:
        """Determine if the purifier is On."""

        if self.purifier_data.device_detail['state']['power'] in [1,2]:
            return True
        else:
            return False

    @property
    def preset_modes(self) -> list:
        """Return the available preset modes."""

        return PURIFIER_MODES

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""

        mode = self.purifier_data.device_detail['state']['mode']
        return PURIFIER_MODE_NAMED[mode]

    @property
    def supported_features(self) -> int:
        """Return supported features."""

        return FanEntityFeature.PRESET_MODE

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the air purifier on."""

        await self.coordinator.client.control_purifier(self.purifier_data, PurifierCommand.POWER)
        self.purifier_data.device_detail['state']['power'] = 1
        self.async_write_ha_state()
        # Have to wait before refreshing or PetKit will return wrong power state
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the air purifier off."""

        await self.coordinator.client.control_purifier(self.purifier_data, PurifierCommand.POWER)
        self.purifier_data.device_detail['state']['power'] = 0
        self.async_write_ha_state()
        # Have to wait before refreshing or PetKit will return wrong power state
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set a preset mode for the purifier."""

        command = PURIFIER_MODE_TO_COMMAND[preset_mode]
        await self.coordinator.client.control_purifier(self.purifier_data, command)
        MODE_TO_VALUE = {v: k for (k, v) in PURIFIER_MODE_NAMED.items()}
        value = MODE_TO_VALUE.get(preset_mode)
        self.purifier_data.device_detail['state']['mode'] = value
        # Have to wait before refreshing or PetKit will return wrong mode state
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()
