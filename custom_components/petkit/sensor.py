"""Sensor platform for PetKit integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from petkitaio.model import Feeder, LitterBox, Pet, W5Fountain

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
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

from .const import (
    DOMAIN,
    EVENT_DESCRIPTION,
    EVENT_TYPE_NAMED,
    FEEDERS,
    LITTER_BOXES,
    VALID_EVENT_TYPES,
    WATER_FOUNTAINS
)
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
            WFPurifiedWater(coordinator, wf_id),
        ))

    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # All Feeders
        sensors.extend((
            FeederStatus(coordinator, feeder_id),
            FeederDesiccant(coordinator, feeder_id),
            FeederBattStatus(coordinator, feeder_id),
            FeederRSSI(coordinator, feeder_id),
            FeederError(coordinator, feeder_id),
        ))

        # D3 & D4
        if feeder_data.type in ['d3', 'd4']:
            sensors.extend((
                TimesDispensed(coordinator, feeder_id),
                TotalPlanned(coordinator, feeder_id),
                PlannedDispensed(coordinator, feeder_id),
                TotalDispensed(coordinator, feeder_id),
            ))

        # D4 Feeder
        if feeder_data.type == 'd4':
            sensors.extend((
                ManualDispensed(coordinator, feeder_id),
            ))

        #D3 Feeder
        if feeder_data.type == 'd3':
            sensors.extend((
                AmountEaten(coordinator, feeder_id),
                TimesEaten(coordinator, feeder_id),
                FoodInBowl(coordinator, feeder_id),
            ))

    # Litter boxes
    for lb_id, lb_data in coordinator.data.litter_boxes.items():
        # Pura X
        sensors.extend((
            LBDeodorizerLevel(coordinator, lb_id),
            LBLitterLevel(coordinator, lb_id),
            LBLitterWeight(coordinator, lb_id),
            LBRSSI(coordinator, lb_id),
            LBError(coordinator, lb_id),
            LBTimesUsed(coordinator, lb_id),
            LBAverageUse(coordinator, lb_id),
            LBTotalUse(coordinator, lb_id),
            LBLastUsedBy(coordinator, lb_id),
            LBLastEvent(coordinator, lb_id),
        ))

    # Pets
    for pet_id, pet_data in coordinator.data.pets.items():
        # Only add sensor for cats that have litter box(s)
        if (pet_data.type == 'Cat') and coordinator.data.litter_boxes:
            sensors.extend((
                PetRecentWeight(coordinator, pet_id),
                PetLastUseDuration(coordinator, pet_id),
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

        todayPumpRunTime = self.wf_data.data['todayPumpRunTime']
        energy_usage = round(((0.75 * todayPumpRunTime) / 3600000), 4)
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

class WFPurifiedWater(CoordinatorEntity, SensorEntity):
    """Representation of amount of times water has been purified today"""

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

        return str(self.wf_data.id) + '_purified_water'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Purified water today"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return number of times water was purified today."""

        f = ((1.5 * self.wf_data.data['todayPumpRunTime'])/60)
        f2 = 2.0
        purified_today =  int((f/f2))
        return purified_today

    @property
    def icon(self) -> str | None:
        """Set icon."""

        return 'mdi:water-pump'

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

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

        if self.feeder_data.type == 'd3':
            return len(self.feeder_data.data['state']['feedState']['feedTimes'])
        else:
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


class AmountEaten(CoordinatorEntity, SensorEntity):
    """Representation of amount eaten by pet today."""

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

        return str(self.feeder_data.id) + '_amount_eaten'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Amount eaten"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return total amount eaten."""

        return self.feeder_data.data['state']['feedState']['eatAmountTotal']

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


class TimesEaten(CoordinatorEntity, SensorEntity):
    """Representation of amount of times pet ate today."""

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

        return str(self.feeder_data.id) + '_times_eaten'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Times eaten"
    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return total times eaten."""

        return len(self.feeder_data.data['state']['feedState']['eatTimes'])

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


class FoodInBowl(CoordinatorEntity, SensorEntity):
    """Representation of amount of food in D3 feeder bowl."""

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

        return str(self.feeder_data.id) + '_food_in_bowl'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Food in bowl"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current amount of food in bowl."""

        return self.feeder_data.data['state']['weight']

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


class FeederError(CoordinatorEntity, SensorEntity):
    """Representation of D3 feeder error."""

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

        return str(self.feeder_data.id) + '_feeder_error'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Error"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> str:
        """Return current error if there is one."""

        if 'errorMsg' in self.feeder_data.data['state']:
            return self.feeder_data.data['state']['errorMsg']
        else:
            return 'No Error'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:alert-circle'


class LBDeodorizerLevel(CoordinatorEntity, SensorEntity):
    """Representation of litter box deodorizer percentage left."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_deodorizer_level'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Deodorizer level"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:spray-bottle'

    @property
    def native_value(self) -> int:
        """Return current percentage."""

        return self.lb_data.device_detail['state']['liquid']

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return percent as the native unit."""

        return PERCENTAGE

class LBLitterLevel(CoordinatorEntity, SensorEntity):
    """Representation of litter box litter percentage left."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_litter_level'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Litter level"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:landslide'

    @property
    def native_value(self) -> int:
        """Return current percentage."""

        return self.lb_data.device_detail['state']['sandPercent']

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return percent as the native unit."""

        return PERCENTAGE


class LBLitterWeight(CoordinatorEntity, SensorEntity):
    """Representation of litter box litter weight."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_litter_weight'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Litter weight"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:landslide'

    @property
    def native_value(self) -> float:
        """Return current weight in Kg."""

        return round((self.lb_data.device_detail['state']['sandWeight'] / 1000), 1)

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return Kg as the native unit."""

        return UnitOfMass.KILOGRAMS

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.WEIGHT


class LBRSSI(CoordinatorEntity, SensorEntity):
    """Representation of litter box wifi strength."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_rssi'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "RSSI"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:wifi'

    @property
    def native_value(self) -> int:
        """Return current signal strength."""

        return self.lb_data.device_detail['state']['wifi']['rsq']

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return dBm as the native unit."""

        return SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.SIGNAL_STRENGTH


class LBError(CoordinatorEntity, SensorEntity):
    """Representation of litter box error."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_error'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Error"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> str:
        """Return current error if there is one."""

        if 'errorMsg' in self.lb_data.device_detail['state']:
            return self.lb_data.device_detail['state']['errorMsg']
        else:
            return 'No Error'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:alert-circle'


class LBTimesUsed(CoordinatorEntity, SensorEntity):
    """Representation of litter box usage count."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_times_used'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Times used"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current usage count."""

        return self.lb_data.statistics['times']

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.TOTAL

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:counter'


class LBAverageUse(CoordinatorEntity, SensorEntity):
    """Representation of litter box average usage."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_average_use'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Average use"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current usage time average in seconds."""

        return self.lb_data.statistics['avgTime']

    @property
    def native_unit_of_measurement(self) -> UnitOfTime:
        """Return seconds as the native unit."""

        return UnitOfTime.SECONDS

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:clock'


class LBTotalUse(CoordinatorEntity, SensorEntity):
    """Representation of litter box total usage."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_total_use'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Total use"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> int:
        """Return current usage time average in seconds."""

        return self.lb_data.statistics['totalTime']

    @property
    def native_unit_of_measurement(self) -> UnitOfTime:
        """Return seconds as the native unit."""

        return UnitOfTime.SECONDS

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:clock'


class LBLastUsedBy(CoordinatorEntity, SensorEntity):
    """Representation of last pet to use the litter box."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_last_used_by'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Last used by"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> str:
        """Return last pet to use the litter box."""

        if self.lb_data.statistics['statisticInfo']:
            last_record = self.lb_data.statistics['statisticInfo'][-1]
            if last_record['petId'] == '0':
                return 'Unknown pet'
            else:
                return last_record['petName']
        else:
            return 'No record yet'

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:cat'


class LBLastEvent(CoordinatorEntity, SensorEntity):
    """Representation of last litter box event."""

    def __init__(self, coordinator, lb_id):
        super().__init__(coordinator)
        self.lb_id = lb_id
        self.sub_events = None

    @property
    def lb_data(self) -> LitterBox:
        """Handle coordinator litter box data."""

        return self.coordinator.data.litter_boxes[self.lb_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.lb_data.id)},
            "name": self.lb_data.device_detail['name'],
            "manufacturer": "PetKit",
            "model": LITTER_BOXES[self.lb_data.type],
            "sw_version": f'{self.lb_data.device_detail["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.lb_data.id) + '_last_event'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Last event"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def native_value(self) -> str:
        """Return last litter box event from device record."""

        if self.lb_data.device_record:
            last_record = self.lb_data.device_record[-1]
            if last_record['subContent']:
                self.sub_events = self.sub_events_to_description(last_record['subContent'])
            else:
                self.sub_events = None
            event = self.result_to_description(last_record['eventType'], last_record)
            return event
        else:
            return 'No events yet'

    @property
    def extra_state_attributes(self):
        """Return sub events associated with the main event."""

        return {
            'sub_events': self.sub_events
        }

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:calendar'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    def result_to_description(self, event_type: int, record: dict[str, Any]) -> str:
        """Return a description of the last event"""

        # Make sure event_type is valid
        if event_type not in VALID_EVENT_TYPES:
            return 'Event type unknown'

        # Pet out events don't have result or reason
        if event_type != 10:
            result = record['content']['result']
            if 'startReason' in record['content']:
                reason = record['content']['startReason']

        if event_type == 5:
            if result == 2:
                if 'error' in record['content']:
                    error = record['content']['error']
                else:
                    return EVENT_TYPE_NAMED[event_type]

                try:
                    description = EVENT_DESCRIPTION[event_type][result][reason][error]
                except KeyError:
                    return EVENT_TYPE_NAMED[event_type]
                return description

            else:
                try:
                    description = EVENT_DESCRIPTION[event_type][result][reason]
                except KeyError:
                    return EVENT_TYPE_NAMED[event_type]
                return description

        if event_type in [6, 7]:
            if result == 2:
                if 'error' in record['content']:
                    error = record['content']['error']
                else:
                    return EVENT_TYPE_NAMED[event_type]

                try:
                    description = EVENT_DESCRIPTION[event_type][result][error]
                except KeyError:
                    return EVENT_TYPE_NAMED[event_type]
                return description

            else:
                try:
                    description = EVENT_DESCRIPTION[event_type][result]
                except KeyError:
                    return EVENT_TYPE_NAMED[event_type]
                return description

        if event_type == 8:
            try:
                description = EVENT_DESCRIPTION[event_type][result][reason]
            except KeyError:
                return EVENT_TYPE_NAMED[event_type]
            return description

        if event_type == 10:
            if (record['petId'] == '-2') or (record['petId'] == '-1'):
                name = 'Unknown'
            else:
                name = record['petName']
            return f'{name} used the litter box'

    def sub_events_to_description(self, sub_events: list[dict[str, Any]]) -> list[str]:
        """Create a list containing all of the sub events associated with an event to be used as attribute"""

        event_list: list[str] = []
        for event in sub_events:
            description = self.result_to_description(event['eventType'], event)
            event_list.append(description)
        return event_list

class PetRecentWeight(CoordinatorEntity, SensorEntity):
    """Representation of most recent weight measured by litter box."""

    def __init__(self, coordinator, pet_id):
        super().__init__(coordinator)
        self.pet_id = pet_id

    @property
    def pet_data(self) -> Pet:
        """Handle coordinator Pet data."""

        return self.coordinator.data.pets[self.pet_id]

    @property
    def litter_boxes(self) -> dict[LitterBox, Any]:
        """Handle coordinator Litter Boxes data."""
        
        return self.coordinator.data.litter_boxes

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.pet_data.id)},
            "name": self.pet_data.data['name'],
            "manufacturer": "PetKit",
            "model": self.pet_data.type,
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return self.pet_data.id + '_recent_weight'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Latest weight"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_picture(self) -> str:
        """Grab associated pet picture."""

        if 'avatar' in self.pet_data.data:
            return self.pet_data.data['avatar']
        else:
            return None

    @property
    def icon(self) -> str:
        """Set icon if the pet doesn't have an avatar."""

        if 'avatar' in self.pet_data.data:
            return None
        else:
            return 'mdi:weight'

    @property
    def native_value(self) -> float:
        """Return most recent weight from today."""

        sorted_dict = self.grab_recent_weight()
        if sorted_dict:
            last_key = list(sorted_dict)[-1]
            latest_weight = sorted_dict[last_key]
            weight_calculation = round((latest_weight / 1000), 1)
            return weight_calculation
        else:
            return 0.0

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return kilograms as the native unit."""

        return UnitOfMass.KILOGRAMS

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""

        return SensorDeviceClass.WEIGHT

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    def grab_recent_weight(self) -> float:
        """Grab the most recent weight."""
        
        weight_dict: dict[int, int] = {}

        for lb_id, lb_data in self.litter_boxes.items():
            if lb_data.statistics['statisticInfo']:
                try:
                    final_idx = max(index for index, stat in enumerate(lb_data.statistics['statisticInfo']) if stat['petId'] == self.pet_data.id)
                except ValueError:
                    continue
                else:
                    last_stat = lb_data.statistics['statisticInfo'][final_idx]
                    weight = last_stat['petWeight']
                    time = last_stat['xTime']
                    weight_dict[time] = weight
        sorted_dict = dict(sorted(weight_dict.items()))
        return sorted_dict


class PetLastUseDuration(CoordinatorEntity, SensorEntity):
    """Representation of most recent litter box use duration."""

    def __init__(self, coordinator, pet_id):
        super().__init__(coordinator)
        self.pet_id = pet_id

    @property
    def pet_data(self) -> Pet:
        """Handle coordinator Pet data."""

        return self.coordinator.data.pets[self.pet_id]

    @property
    def litter_boxes(self) -> dict[LitterBox, Any]:
        """Handle coordinator Litter Boxes data."""
        
        return self.coordinator.data.litter_boxes

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""

        return {
            "identifiers": {(DOMAIN, self.pet_data.id)},
            "name": self.pet_data.data['name'],
            "manufacturer": "PetKit",
            "model": self.pet_data.type,
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return self.pet_data.id + '_last_use_duration'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Last use duration"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def entity_picture(self) -> str:
        """Grab associated pet picture."""

        if 'avatar' in self.pet_data.data:
            return self.pet_data.data['avatar']
        else:
            return None

    @property
    def icon(self) -> str:
        """Set icon if the pet doesn't have an avatar."""

        if 'avatar' in self.pet_data.data:
            return None
        else:
            return 'mdi:clock'

    @property
    def native_value(self) -> int:
        """Return most recent duration from today."""

        sorted_dict = self.grab_recent_duration()
        if sorted_dict:
            last_key = list(sorted_dict)[-1]
            latest_duration = sorted_dict[last_key]
            return latest_duration
        else:
            return 0

    @property
    def native_unit_of_measurement(self) -> UnitOfTime:
        """Return seconds as the native unit."""

        return UnitOfTime.SECONDS

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    def grab_recent_duration(self) -> float:
        """Grab the most recent duration."""
        
        duration_dict: dict[int, int] = {}

        for lb_id, lb_data in self.litter_boxes.items():
            if lb_data.statistics['statisticInfo']:
                try:
                    final_idx = max(index for index, stat in enumerate(lb_data.statistics['statisticInfo']) if stat['petId'] == self.pet_data.id)
                # Handle if the pet didn't use the litter box
                except ValueError:
                    continue
                else:
                    last_stat = lb_data.statistics['statisticInfo'][final_idx]
                    duration = last_stat['petTotalTime']
                    time = last_stat['xTime']
                    duration_dict[time] = duration
        sorted_dict = dict(sorted(duration_dict.items()))
        return sorted_dict
