"""Sensor platform for PetKit integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from petkitaio.model import Feeder, W5Fountain

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import(
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfEnergy,
    UnitOfMass,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FEEDERS, WATER_FOUNTAINS
from .coordinator import PetKitDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Sensor Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []

    for wf_id, wf_data in coordinator.data.water_fountains.items():
        # Water Fountains (W5)
        sensors.extend((
            WFEnergyUse(coordinator, wf_id),
            WFLastUpdate(coordinator, wf_id),
            WFFilter(coordinator, wf_id),
        ))

    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # All Feeders
        sensors.extend((
            FeederStatus(coordinator, feeder_id),
            FeederDesiccant(coordinator, feeder_id),
            FeederBattStatus(coordinator, feeder_id),
            FeederRSSI(coordinator, feeder_id),
        ))

        # D4 Feeder
        if feeder_data.type == 'd4':
            sensors.extend((
                TotalDispensed(coordinator, feeder_id),
                TotalPlanned(coordinator, feeder_id),
                PlannedDispensed(coordinator, feeder_id),
                ManualDispensed(coordinator, feeder_id),
                TimesDispensed(coordinator, feeder_id),
            ))

    async_add_entities(sensors)


class WFEnergyUse(CoordinatorEntity, SensorEntity):
    """Representation of energy used by water fountain today."""

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

        return str(self.wf_data.id) + '_energy_usage'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Energy usage"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> float:
        """Return total energy usage in kWh."""

        waterPumpRunTime = self.wf_data.data['waterPumpRunTime']
        todayPumpRunTime = self.wf_data.data['todayPumpRunTime']
        energy_usage = round((waterPumpRunTime/todayPumpRunTime) * 0.002, 3)
        return energy_usage

    @property
    def native_unit_of_measurement(self) -> UnitOfEnergy:
        """Return kWh as the native unit."""

        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.TOTAL

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

class WFLastUpdate(CoordinatorEntity, SensorEntity):
    """Representation of time water fountain data was last updated."""

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

        return str(self.wf_data.id) + '_last_update'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Last data update"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> datetime:
        """Return date/time of last water fountain data update.

        This is only expected to change if the user has a valid relay.
        Those without a relay will need to connect to the water fountain
        via bluetooth to get the data to update.
        """

        last_update = self.wf_data.data['updateAt']
        return datetime.fromisoformat(last_update.replace('.000Z', '+00:00'))

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.TIMESTAMP

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Determine if device is available.

        Return true if a date/time is specified
        in the updateAt key.
        """

        if self.wf_data.data['updateAt']:
            return True
        else:
            return False

class WFFilter(CoordinatorEntity, SensorEntity):
    """Representation of water fountain filter percentage left."""

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

        return str(self.wf_data.id) + '_filter_percent'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Filter"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current filter percent left."""

        return self.wf_data.data['filterPercent']

    @property
    def native_unit_of_measurement(self) -> str:
        """Return percent as the native unit."""

        return PERCENTAGE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self) -> str:
        """Set filter icon."""

        if self.wf_data.data['filterPercent'] == 0:
            return 'mdi:filter-off'
        else:
            return 'mdi:filter'

class FeederStatus(CoordinatorEntity, SensorEntity):
    """Representation of feeder status."""

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

        return str(self.feeder_data.id) + '_status'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Status"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> str | None:
        """Return status of the feeder."""

        pim = self.feeder_data.data['state']['pim']
        if pim == 0:
            return 'Offline'
        elif pim == 1:
            return 'Normal'
        elif pim == 2:
            return 'On Batteries'
        else:
            return None

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str | None:
        """Set status icon."""

        pim = self.feeder_data.data['state']['pim']
        if pim == 0:
            return 'mdi:cloud-off'
        elif pim == 1:
            return 'mdi:cloud'
        elif pim == 2:
            return 'mdi:battery'
        else:
            return None

class FeederDesiccant(CoordinatorEntity, SensorEntity):
    """Representation of feeder desiccant days remaining."""

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

        return str(self.feeder_data.id) + '_desiccant_days'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Desiccant days remaining"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return days remaining."""

        return self.feeder_data.data['state']['desiccantLeftDays']

    @property
    def native_unit_of_measurement(self) -> UnitOfTime:
        """Return days as the native unit."""

        return UnitOfTime.DAYS

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str | None:
        """Set icon."""

        return 'mdi:air-filter'

class FeederBattStatus(CoordinatorEntity, SensorEntity):
    """Representation of feeder battery status."""

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

        return str(self.feeder_data.id) + '_battery_status'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Battery status"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> str:
        """Return status of the feeder."""

        battery_level = self.feeder_data.data['state']['batteryStatus']
        if battery_level == 1:
            return "Normal"
        else:
            return "Low"

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set battery status icon."""

        battery_level = self.feeder_data.data['state']['batteryStatus']
        if battery_level == 1:
            return "mdi:battery"
        else:
            return "mdi:battery-alert-variant"

    @property
    def available(self) -> bool:
        """Set to True only if battery is being used.

        When Battery isn't being used the level is always 0
        """

        if self.feeder_data.data['state']['pim'] == 2:
            return True
        else:
            return False

class TotalDispensed(CoordinatorEntity, SensorEntity):
    """Representation of feeder total food dispensed."""

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

        return str(self.feeder_data.id) + '_total_dispensed'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Dispensed"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return total dispensed."""

        return self.feeder_data.data['state']['feedState']['realAmountTotal']

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return grams as the native unit."""

        return UnitOfMass.GRAMS

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.TOTAL_INCREASING

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:food-drumstick'

class TotalPlanned(CoordinatorEntity, SensorEntity):
    """Representation of feeder total planned to be dispensed."""

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

        return str(self.feeder_data.id) + '_total_planned'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Planned"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return total planned."""

        return self.feeder_data.data['state']['feedState']['planAmountTotal']

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return grams as the native unit."""

        return UnitOfMass.GRAMS

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:food-drumstick'

class PlannedDispensed(CoordinatorEntity, SensorEntity):
    """Representation of feeder planned that has been dispensed."""

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

        return str(self.feeder_data.id) + '_planned_dispensed'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Planned dispensed"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return total planned dispensed."""

        return self.feeder_data.data['state']['feedState']['planRealAmountTotal']

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return grams as the native unit."""

        return UnitOfMass.GRAMS

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.TOTAL_INCREASING

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:food-drumstick'

class ManualDispensed(CoordinatorEntity, SensorEntity):
    """Representation of feeder amount that has been manually dispensed."""

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

        return str(self.feeder_data.id) + '_manual_dispensed'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Manually dispensed"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return total manually dispensed."""

        return self.feeder_data.data['state']['feedState']['addAmountTotal']

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return grams as the native unit."""

        return UnitOfMass.GRAMS

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:food-drumstick'

class TimesDispensed(CoordinatorEntity, SensorEntity):
    """Representation of feeder amount of times food has been dispensed."""

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

        return str(self.feeder_data.id) + '_times_dispensed'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Times dispensed"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return total times dispensed."""

        return self.feeder_data.data['state']['feedState']['times']

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:food-drumstick'

class FeederRSSI(CoordinatorEntity, SensorEntity):
    """Representation of feeder WiFi connection strength."""

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

        return str(self.feeder_data.id) + '_feeder_rssi'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "RSSI"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return RSSI measurement."""

        return self.feeder_data.data['state']['wifi']['rsq']

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def native_unit_of_measurement(self) -> str:
        """Return dBm as the native unit."""

        return SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.SIGNAL_STRENGTH

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:wifi'
