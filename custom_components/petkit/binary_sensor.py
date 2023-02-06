"""Binary Sensor platform for PetKit integration."""
from __future__ import annotations

from typing import Any

from petkitaio.model import Feeder, W5Fountain

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FEEDERS, WATER_FOUNTAINS
from .coordinator import PetKitDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Binary Sensor Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    binary_sensors = []

    for wf_id, wf_data in coordinator.data.water_fountains.items():
        # Water Fountains (W5)
        binary_sensors.extend((
            WFWater(coordinator, wf_id),
        ))

    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # All Feeders
        binary_sensors.extend((
            FoodLevel(coordinator, feeder_id),
        ))

        # D4 Feeder
        if feeder_data.type == 'd4':
            binary_sensors.extend((
                BatteryInstalled(coordinator, feeder_id),
            ))

    async_add_entities(binary_sensors)


class WFWater(CoordinatorEntity, BinarySensorEntity):
    """Representation of Water Fountain lack of water warning."""

    def __init__(self, coordinator, wf_id):
        super().__init__(coordinator)
        self.wf_id = wf_id

    @property
    def wf_data(self) -> W5Fountain:
        """Handle coordinator Water Fountain data"""

        return self.coordinator.data.water_fountains[self.wf_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.wf_data.id)},
            "name": self.wf_data.data['name'],
            "manufacturer": "PetKit",
            "model": WATER_FOUNTAINS[self.wf_data.type],
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_water_level'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Water level"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return entity device class."""

        return BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        """Return True if water needs to be added."""

        if self.wf_data.data['lackWarning'] == 1:
            return True
        else:
            return False

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.wf_data.data['lackWarning'] == 1:
            return 'mdi:water-alert'
        else:
            return 'mdi:water'

class FoodLevel(CoordinatorEntity, BinarySensorEntity):
    """Representation of Feeder lack of food warning."""

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

        return str(self.feeder_data.id) + '_food_level'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Food level"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return entity device class."""

        return BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        """Return True if food needs to be added."""

        if self.feeder_data.data['state']['food'] == 0:
            return True
        else:
            return False

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.feeder_data.data['state']['food'] == 0:
            return 'mdi:food-drumstick-off'
        else:
            return 'mdi:food-drumstick'

class BatteryInstalled(CoordinatorEntity, BinarySensorEntity):
    """Representation of if Feeder has batteries installed."""

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

        return str(self.feeder_data.id) + '_battery_installed'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Battery installed"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool:
        """Return True if food needs to be added."""

        if self.feeder_data.data['state']['batteryPower'] == 1:
            return True
        else:
            return False

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:battery'
