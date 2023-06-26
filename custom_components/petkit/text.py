"""Text platform for PetKit integration."""
from __future__ import annotations

from petkitaio.model import Feeder

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FEEDERS,
    PETKIT_COORDINATOR
)
from .coordinator import PetKitDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Text Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][PETKIT_COORDINATOR]

    text_entities = []

    for feeder_id, feeder_data in coordinator.data.feeders.items():

        # D4s Feeder
        if feeder_data.type == 'd4s':
            text_entities.append(
                ManualFeed(coordinator, feeder_id)
            )
    async_add_entities(text_entities)

class ManualFeed(CoordinatorEntity, TextEntity):
    """Representation of manual feeding amount selector."""

    def __init__(self, coordinator, feeder_id):
        super().__init__(coordinator)
        self.feeder_id = feeder_id

    @property
    def feeder_data(self) -> Feeder:
        """Handle coordinator Feeder data."""

        return self.coordinator.data.feeders[self.feeder_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.feeder_data.id)},
            "name": self.feeder_data.data['name'],
            "manufacturer": "PetKit",
            "model": FEEDERS[self.feeder_data.type],
            "sw_version": f'{self.feeder_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.feeder_data.id) + '_manual_feed'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "manual_feed"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:bowl-mix'

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    @property
    def native_max(self) -> int:
        """Max number of characters."""

        return 5

    @property
    def native_min(self) -> int:
        """Min number of characters."""

        return 3

    @property
    def pattern(self) -> str:
        """Check validity with regex pattern."""

        return "^([0-9]|10),([0-9]|10)$"

    @property
    def native_value(self) -> str:
        """Always reset to 0,0"""

        return "0,0"

    async def async_set_value(self, value: str) -> None:
        """Set manual feeding amount."""

        portions = value.split(',')
        await self.coordinator.client.dual_hopper_manual_feeding(self.feeder_data, int(portions[0]), int(portions[1]))
        await self.coordinator.async_request_refresh()
