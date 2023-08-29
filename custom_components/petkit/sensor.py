"""Sensor platform for PetKit integration."""
from __future__ import annotations

from datetime import datetime
from math import floor as floor
from typing import Any

from petkitaio.model import Feeder, LitterBox, Pet, Purifier, W5Fountain

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
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

from .const import (
    DOMAIN,
    FEEDERS,
    LITTER_BOXES,
    PETKIT_COORDINATOR,
    PURIFIERS,
    WATER_FOUNTAINS
)
from .coordinator import PetKitDataUpdateCoordinator
from .litter_events import (
    EVENT_DESCRIPTION,
    EVENT_TYPE_NAMED,
    MAX_EVENT_DESCRIPTION,
    MAX_EVENT_TYPES,
    MAX_EVENT_TYPE_NAMED,
    VALID_EVENT_TYPES
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Sensor Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][PETKIT_COORDINATOR]

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
            sensors.append(
                ManualDispensed(coordinator, feeder_id)
            )

        #D3 Feeder
        if feeder_data.type == 'd3':
            sensors.extend((
                AmountEaten(coordinator, feeder_id),
                TimesEaten(coordinator, feeder_id),
                FoodInBowl(coordinator, feeder_id),
            ))

        # D4s Feeder
        if feeder_data.type == 'd4s':
            sensors.extend((
                TimesEaten(coordinator, feeder_id),
                TimesDispensed(coordinator, feeder_id),
                AvgEatingTime(coordinator, feeder_id),
                ManualDispensedHopper1(coordinator, feeder_id),
                ManualDispensedHopper2(coordinator, feeder_id),
                TotalPlannedHopper1(coordinator, feeder_id),
                TotalPlannedHopper2(coordinator, feeder_id),
                PlannedDispensedHopper1(coordinator, feeder_id),
                PlannedDispensedHopper2(coordinator, feeder_id),
                TotalDispensedHopper1(coordinator, feeder_id),
                TotalDispensedHopper2(coordinator, feeder_id)
            ))

        # Fresh Element Feeder
        if feeder_data.type == 'feeder':
            sensors.append(
                FoodLeft(coordinator, feeder_id)
            )

    # Litter boxes
    for lb_id, lb_data in coordinator.data.litter_boxes.items():
        #Pura Air device for MAX litter box
        if (lb_data.type == 't4') and ('k3Device' in lb_data.device_detail):
            sensors.extend((
                PuraAirBattery(coordinator, lb_id),
                PuraAirLiquid(coordinator, lb_id)
            ))
        # Pura X & MAX
        if lb_data.type in ['t3', 't4']:
            sensors.extend((
                LBDeodorizerLevel(coordinator, lb_id),
                LBLitterLevel(coordinator, lb_id),
                LBLitterWeight(coordinator, lb_id),
                LBRSSI(coordinator, lb_id),
                LBError(coordinator, lb_id),
                LBTimesUsed(coordinator, lb_id),
                LBAverageUse(coordinator, lb_id),
                LBTotalUse(coordinator, lb_id),
                LBLastUsedBy(coordinator, lb_id)
            ))
        # Pura X
        if lb_data.type == 't3':
            sensors.append(
                LBLastEvent(coordinator, lb_id)
            )
        # Pura MAX
        if lb_data.type == 't4':
            sensors.extend((
                MAXLastEvent(coordinator, lb_id),
                MAXWorkState(coordinator, lb_id)
            ))

    # Pets
    for pet_id, pet_data in coordinator.data.pets.items():
        # Only add sensor for cats that have litter box(s)
        if (pet_data.type == 'Cat') and coordinator.data.litter_boxes:
            sensors.extend((
                PetRecentWeight(coordinator, pet_id),
                PetLastUseDuration(coordinator, pet_id),
            ))

    #Purifiers
    for purifier_id, purifier_data in coordinator.data.purifiers.items():
        sensors.extend((
            PurifierError(coordinator, purifier_id),
            PurifierHumidity(coordinator, purifier_id),
            PurifierTemperature(coordinator, purifier_id),
            AirPurified(coordinator, purifier_id),
            PurifierRSSI(coordinator, purifier_id),
            PurifierLiquid(coordinator, purifier_id)
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
            "model": WATER_FOUNTAINS.get(self.wf_data.data["typeCode"], "Unidentified Water Fountain") if "typeCode" in self.wf_data.data else "Unidentified Water Fountain",
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_energy_usage'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "energy_usage"

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
            "model": WATER_FOUNTAINS.get(self.wf_data.data["typeCode"], "Unidentified Water Fountain") if "typeCode" in self.wf_data.data else "Unidentified Water Fountain",
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_last_update'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "last_data_update"

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
            "model": WATER_FOUNTAINS.get(self.wf_data.data["typeCode"], "Unidentified Water Fountain") if "typeCode" in self.wf_data.data else "Unidentified Water Fountain",
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_filter_percent'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "filter"

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
            "model": WATER_FOUNTAINS.get(self.wf_data.data["typeCode"], "Unidentified Water Fountain") if "typeCode" in self.wf_data.data else "Unidentified Water Fountain",
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_purified_water'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "purified_water_today"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "feeder_status"

    @property
    def native_value(self) -> str | None:
        """Return status of the feeder."""

        pim = self.feeder_data.data['state']['pim']
        if pim == 0:
            return 'offline'
        elif pim == 1:
            return 'normal'
        elif pim == 2:
            return 'on_batteries'
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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "desiccant_days_remaining"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "battery_status"

    @property
    def native_value(self) -> str:
        """Return status of the feeder battery."""

        battery_level = self.feeder_data.data['state']['batteryStatus']
        if battery_level == 1:
            return "normal"
        else:
            return "low"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "dispensed"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "planned"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "planned_dispensed"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "manually_dispensed"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "times_dispensed"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "rssi"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "amount_eaten"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "times_eaten"

    @property
    def native_value(self) -> int:
        """Return total times eaten."""

        if self.feeder_data.type == 'd4s':
            return self.feeder_data.data['state']['feedState']['eatCount']
        else:
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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "food_in_bowl"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "error"

    @property
    def native_value(self) -> str:
        """Return current error if there is one."""

        if 'errorMsg' in self.feeder_data.data['state']:
            return self.feeder_data.data['state']['errorMsg']
        else:
            return 'no_error'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:alert-circle'


class LBDeodorizerLevel(CoordinatorEntity, SensorEntity):
    """Representation of litter box deodorizer left."""

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        #Pura MAX uses N50 deodorizer and not liquid
        if self.lb_data.type == 't4':
            return "n50_odor_eliminator"
        else:
            return "deodorizer_level"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.lb_data.type == 't4':
            return 'mdi:air-filter'
        else:
            return 'mdi:spray-bottle'

    @property
    def native_value(self) -> int:
        """Return current percentage or days left."""

        #Pura MAX
        if self.lb_data.type == 't4':
            deodorant_days = self.lb_data.device_detail['state']['deodorantLeftDays']
            if deodorant_days < 1:
                return 0
            else:
                return deodorant_days
        #Pura X
        else:
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
    def native_unit_of_measurement(self) -> str | UnitOfTime:
        """Return percent or days as the native unit."""

        #Pura MAX
        if self.lb_data.type == 't4':
            return UnitOfTime.DAYS
        #Pura X
        else:
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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "litter_level"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "litter_weight"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "rssi"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "error"

    @property
    def native_value(self) -> str:
        """Return current error if there is one."""

        if 'errorMsg' in self.lb_data.device_detail['state']:
            return self.lb_data.device_detail['state']['errorMsg']
        else:
            return 'no_error'

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "times_used"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "average_use"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "total_use"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "last_used_by"

    @property
    def native_value(self) -> str:
        """Return last pet to use the litter box."""

        if self.lb_data.statistics['statisticInfo']:
            last_record = self.lb_data.statistics['statisticInfo'][-1]
            if last_record['petId'] == '0':
                return 'unknown_pet'
            else:
                return last_record['petName']
        else:
            return 'no_record_yet'

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:cat'


class LBLastEvent(CoordinatorEntity, SensorEntity):
    """Representation of Pura X last litter box event."""

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "last_event"

    @property
    def native_value(self) -> str:
        """Return last litter box event from device record."""

        if self.lb_data.device_record:
            last_record = self.lb_data.device_record[-1]
            if last_record['subContent']:
                self.sub_events = self.sub_events_to_description(last_record['subContent'])
            else:
                self.sub_events = 'no_sub_events'
            event = self.result_to_description(last_record['eventType'], last_record)
            return event
        else:
            return 'no_events_yet'

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
            return 'event_type_unknown'

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "latest_weight"

    @property
    def entity_picture(self) -> str | None:
        """Grab associated pet picture."""

        if 'avatar' in self.pet_data.data:
            return self.pet_data.data['avatar']
        else:
            return None

    @property
    def icon(self) -> str | None:
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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "last_use_duration"

    @property
    def entity_picture(self) -> str | None:
        """Grab associated pet picture."""

        if 'avatar' in self.pet_data.data:
            return self.pet_data.data['avatar']
        else:
            return None

    @property
    def icon(self) -> str | None:
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


class PuraAirBattery(CoordinatorEntity, SensorEntity):
    """Representation of Pura Air battery level."""

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

        return str(self.lb_data.id) + '_pura_air_battery'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "pura_air_battery"

    @property
    def native_value(self) -> int:
        """Return current battery percentage."""

        return self.lb_data.device_detail['k3Device']['battery']

    @property
    def native_unit_of_measurement(self) -> str:
        """Return % as the native unit."""

        return PERCENTAGE

    @property
    def device_class(self) -> SensorDeviceClass:
        """ Return entity device class """

        return SensorDeviceClass.BATTERY

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Determine if device is available.

        Return true if there is a pura air
        device associated.
        """

        if 'k3Device' in self.lb_data.device_detail:
            return True
        else:
            return False


class PuraAirLiquid(CoordinatorEntity, SensorEntity):
    """Representation of Pura Air liquid level."""

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

        return str(self.lb_data.id) + '_pura_air_liquid'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "pura_air_liquid"

    @property
    def native_value(self) -> int:
        """Return current liquid left."""

        return self.lb_data.device_detail['k3Device']['liquid']

    @property
    def native_unit_of_measurement(self) -> str:
        """Return % as the native unit."""

        return PERCENTAGE

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""

        return SensorStateClass.MEASUREMENT

    @property
    def icon(self) -> str:
        """Return icon for entity."""

        return 'mdi:cup'

    @property
    def available(self) -> bool:
        """Determine if device is available.

        Return true if there is a pura air
        device associated.
        """

        if 'k3Device' in self.lb_data.device_detail:
            return True
        else:
            return False


class MAXLastEvent(CoordinatorEntity, SensorEntity):
    """Representation of last Pura MAX litter box event."""

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

        return str(self.lb_data.id) + '_max_last_event'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "max_last_event"

    @property
    def native_value(self) -> str:
        """Return last litter box event from device record."""

        if self.lb_data.device_record:
            last_record = self.lb_data.device_record[-1]
            if last_record['subContent']:
                self.sub_events = self.sub_events_to_description(last_record['subContent'])
            else:
                self.sub_events = 'no_sub_events'
            event = self.result_to_description(last_record['eventType'], last_record)
            return event
        else:
            return 'no_events_yet'

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
        if event_type not in MAX_EVENT_TYPES:
            return 'event_type_unknown'

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
                        return MAX_EVENT_TYPE_NAMED[event_type]

                    try:
                        description = MAX_EVENT_DESCRIPTION[event_type][result][reason][error]
                    except KeyError:
                        if reason == 0:
                            return 'auto_cleaning_failed_other'
                        elif reason == 1:
                            return 'scheduled_cleaning_failed_other'
                        else:
                            return 'manual_cleaning_failed_other'
                    return description

                else:
                    try:
                        description = MAX_EVENT_DESCRIPTION[event_type][result][reason]
                    except KeyError:
                        return MAX_EVENT_TYPE_NAMED[event_type]
                    return description

            if event_type in [6, 7]:
                if result == 2:
                    if 'error' in record['content']:
                        error = record['content']['error']
                    else:
                        return MAX_EVENT_TYPE_NAMED[event_type]

                    try:
                        description = MAX_EVENT_DESCRIPTION[event_type][result][error]
                    except KeyError:
                        if event_type == 6:
                            return 'litter_empty_failed_other'
                        else:
                            return 'reset_failed_other'
                    return description

                else:
                    try:
                        description = MAX_EVENT_DESCRIPTION[event_type][result]
                    except KeyError:
                        return MAX_EVENT_TYPE_NAMED[event_type]
                    return description

            if event_type == 8:
                try:
                    if result == 9:
                        return 'cat_stopped_odor'
                    else:
                        description = MAX_EVENT_DESCRIPTION[event_type][result][reason]
                except KeyError:
                    return MAX_EVENT_TYPE_NAMED[event_type]
                return description

            if event_type == 17:
                try:
                    description = MAX_EVENT_DESCRIPTION[event_type][result]
                except KeyError:
                    return MAX_EVENT_TYPE_NAMED[event_type]
                return description

        if event_type == 10:
            if (record['petId'] == '-2') or (record['petId'] == '-1'):
                name = 'Unknown'
            else:
                name = record['petName']
            return f'{name} used the litter box'

    def sub_events_to_description(self, sub_events: list[dict[str, Any]]) -> list[str]:
        """Create a list containing all the sub-events associated with an event to be used as attribute"""

        event_list: list[str] = []
        for event in sub_events:
            description = self.result_to_description(event['eventType'], event)
            event_list.append(description)
        return event_list


class MAXWorkState(CoordinatorEntity, SensorEntity):
    """Representation of current Pura MAX litter box state."""

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

        return str(self.lb_data.id) + '_max_work_state'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "max_work_state"

    @property
    def native_value(self) -> str:
        """Return current litter box work state from device_detail."""

        if 'workState' in self.lb_data.device_detail['state']:
            work_state = self.lb_data.device_detail['state']['workState']

            if work_state['workMode'] == 0:
                work_process = work_state['workProcess']
                if work_process / 10 == 1:
                    return 'cleaning_litter_box'
                elif int(floor((work_process / 10))) == 2:
                    if work_process % 10 == 2:
                        if 'safeWarn' in work_state:
                            if work_state['safeWarn'] != 0:
                                if work_state['safeWarn'] == 1:
                                    return 'cleaning_paused_pet_entered'
                                else:
                                    return 'cleaning_paused_system_error'
                            if work_state['safeWarn'] == 0:
                                ### petInTime could be referring to key in state and not workState
                                if work_state['petInTime'] == 0:
                                    return 'cleaning_paused_pet_approach'
                                else:
                                    return 'cleaning_paused_pet_using'
                    else:
                        return 'cleaning_litter_box_paused'
                elif work_process / 10 == 3:
                    return 'resetting_device'
                elif int(floor((work_process / 10))) == 4:
                    if work_process % 10 == 2:
                        if 'safeWarn' in work_state:
                            if work_state['safeWarn'] != 0:
                                if work_state['safeWarn'] == 1:
                                    return 'paused_pet_entered'
                                else:
                                    return 'paused_system_error'
                            if work_state['safeWarn'] == 0:
                                ### petInTime could be referring to key in state and not workState
                                if work_state['petInTime'] == 0:
                                    return 'paused_pet_approach'
                                else:
                                    return 'paused_pet_using'
                    else:
                        return 'litter_box_paused'
                else:
                    return 'cleaning_litter_box'
            if work_state['workMode'] == 1:
                work_process = work_state['workProcess']
                if work_process / 10 == 1:
                    return 'dumping_litter'
                if int(floor((work_process / 10))) == 2:
                    if work_process % 10 == 2:
                        if 'safeWarn' in work_state:
                            if work_state['safeWarn'] != 0:
                                if work_state['safeWarn'] == 1:
                                    return 'dumping_paused_pet_entered'
                                else:
                                    return 'dumping_paused_system_error'
                            if work_state['safeWarn'] == 0:
                                ### petInTime could be referring to key in state and not workState
                                if work_state['petInTime'] == 0:
                                    return 'dumping_paused_pet_approach'
                                else:
                                    return 'dumping_paused_pet_using'
                    else:
                        return 'dumping_litter_paused'
                if work_process / 10 == 3:
                    return 'resetting_device'
                if int(floor((work_process / 10))) == 4:
                    if work_process % 10 == 2:
                        if 'safeWarn' in work_state:
                            if work_state['safeWarn'] != 0:
                                if work_state['safeWarn'] == 1:
                                    return 'paused_pet_entered'
                                else:
                                    return 'paused_system_error'
                            if work_state['safeWarn'] == 0:
                                ### petInTime could be referring to key in state and not workState
                                if work_state['petInTime'] == 0:
                                    return 'paused_pet_approach'
                                else:
                                    return 'paused_pet_using'
                    else:
                        return 'litter_box_paused'
            if work_state['workMode'] == 3:
                return 'resetting'
            if work_state['workMode'] == 4:
                return 'leveling'
            if work_state['workMode'] == 5:
                return 'calibrating'
            if work_state['workMode'] == 9:
                work_process = work_state['workProcess']
                if work_process / 10 == 1:
                    return 'maintenance_mode'
                if int(floor((work_process / 10))) == 2:
                    if work_process % 10 == 2:
                        if 'safeWarn' in work_state:
                            if work_state['safeWarn'] != 0:
                                if work_state['safeWarn'] == 1:
                                    return 'maintenance_paused_pet_entered'
                                elif work_state['safeWarn'] == 3:
                                    return 'maintenance_paused_cover'
                                else:
                                    return 'maintenance_paused_system_error'
                            if work_state['safeWarn'] == 0:
                                ### petInTime could be referring to key in state and not workState
                                if work_state['petInTime'] == 0:
                                    return 'maintenance_paused_pet_approach'
                                else:
                                    return 'maintenance_paused_pet_using'
                    else:
                        return 'maintenance_paused'
                if work_process / 10 == 3:
                    return 'exit_maintenance'
                if int(floor((work_process / 10))) == 4:
                    if work_process % 10 == 2:
                        if 'safeWarn' in work_state:
                            if work_state['safeWarn'] != 0:
                                if work_state['safeWarn'] == 1:
                                    return 'maintenance_exit_paused_pet_entered'
                                elif work_state['safeWarn'] == 3:
                                    return 'maintenance_exit_paused_cover'
                                else:
                                    return 'maintenance_exit_paused_system_error'
                            if work_state['safeWarn'] == 0:
                                ### petInTime could be referring to key in state and not workState
                                if work_state['petInTime'] == 0:
                                    return 'maintenance_exit_paused_pet_approach'
                                else:
                                    return 'maintenance_exit_paused_pet_using'
                    else:
                        return 'maintenance_exit_paused'
        else:
            return 'idle'

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:account-hard-hat'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC


class AvgEatingTime(CoordinatorEntity, SensorEntity):
    """Representation of average time pet spent eating."""

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

        return str(self.feeder_data.id) + '_avg_eating_time'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "avg_eating_time"

    @property
    def native_value(self) -> int:
        """Return average eating time."""

        return self.feeder_data.data['state']['feedState']['eatAvg']

    @property
    def native_unit_of_measurement(self) -> UnitOfTime:
        """Return seconds as the native unit."""

        return UnitOfTime.SECONDS

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

        return 'mdi:clock-digital'


class ManualDispensedHopper1(CoordinatorEntity, SensorEntity):
    """Representation of feeder amount that has been manually dispensed from hopper 1."""

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

        return str(self.feeder_data.id) + '_manual_dispensed_hopp_1'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "manually_dispensed_hopp_one"

    @property
    def native_value(self) -> int:
        """Return total manually dispensed."""

        return self.feeder_data.data['state']['feedState']['addAmountTotal1']

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


class ManualDispensedHopper2(CoordinatorEntity, SensorEntity):
    """Representation of feeder amount that has been manually dispensed from hopper 2."""

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

        return str(self.feeder_data.id) + '_manual_dispensed_hopp_2'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "manually_dispensed_hopp_two"

    @property
    def native_value(self) -> int:
        """Return total manually dispensed."""

        return self.feeder_data.data['state']['feedState']['addAmountTotal2']

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

class TotalPlannedHopper1(CoordinatorEntity, SensorEntity):
    """Representation of feeder total planned to be dispensed from hopper 1."""

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

        return str(self.feeder_data.id) + '_total_planned_hopp_1'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "planned_hopp_one"

    @property
    def native_value(self) -> int:
        """Return total planned."""

        return self.feeder_data.data['state']['feedState']['planAmountTotal1']

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


class TotalPlannedHopper2(CoordinatorEntity, SensorEntity):
    """Representation of feeder total planned to be dispensed from hopper 2."""

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

        return str(self.feeder_data.id) + '_total_planned_hopp_2'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "planned_hopp_two"

    @property
    def native_value(self) -> int:
        """Return total planned."""

        return self.feeder_data.data['state']['feedState']['planAmountTotal2']

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


class PlannedDispensedHopper1(CoordinatorEntity, SensorEntity):
    """Representation of feeder planned that has been dispensed from hopper 1."""

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

        return str(self.feeder_data.id) + '_planned_dispensed_hopp_1'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "planned_dispensed_hopp_one"

    @property
    def native_value(self) -> int:
        """Return total planned dispensed."""

        return self.feeder_data.data['state']['feedState']['planRealAmountTotal1']

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


class PlannedDispensedHopper2(CoordinatorEntity, SensorEntity):
    """Representation of feeder planned that has been dispensed from hopper 2."""

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

        return str(self.feeder_data.id) + '_planned_dispensed_hopp_2'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "planned_dispensed_hopp_two"

    @property
    def native_value(self) -> int:
        """Return total planned dispensed."""

        return self.feeder_data.data['state']['feedState']['planRealAmountTotal2']

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


class TotalDispensedHopper1(CoordinatorEntity, SensorEntity):
    """Representation of feeder total food dispensed from hopper 1."""

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

        return str(self.feeder_data.id) + '_total_dispensed_hopp_1'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "dispensed_hopp_one"

    @property
    def native_value(self) -> int:
        """Return total dispensed."""

        return self.feeder_data.data['state']['feedState']['realAmountTotal1']

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


class TotalDispensedHopper2(CoordinatorEntity, SensorEntity):
    """Representation of feeder total food dispensed from hopper 2."""

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

        return str(self.feeder_data.id) + '_total_dispensed_hopp_2'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "dispensed_hopp_two"

    @property
    def native_value(self) -> int:
        """Return total dispensed."""

        return self.feeder_data.data['state']['feedState']['realAmountTotal2']

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


class PurifierError(CoordinatorEntity, SensorEntity):
    """Representation of Purifier error."""

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

        return str(self.purifier_data.id) + '_purifier_error'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "error"

    @property
    def native_value(self) -> str:
        """Return current error if there is one."""

        if 'errorMsg' in self.purifier_data.device_detail['state']:
            return self.purifier_data.device_detail['state']['errorMsg']
        else:
            return 'no_error'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""

        return EntityCategory.DIAGNOSTIC

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:alert-circle'


class PurifierHumidity(CoordinatorEntity, SensorEntity):
    """ Representation of Purifier Humidity """

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

        return str(self.purifier_data.id) + '_purifier_humidity'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "humidity"

    @property
    def native_value(self) -> int:
        """ Return current humidity """

        return round((self.purifier_data.device_detail['state']['humidity'] / 10))

    @property
    def native_unit_of_measurement(self) -> str:
        """ Return percent as the native unit """

        return PERCENTAGE

    @property
    def device_class(self) -> SensorDeviceClass:
        """ Return entity device class """

        return SensorDeviceClass.HUMIDITY

    @property
    def state_class(self) -> SensorStateClass:
        """ Return the type of state class """

        return SensorStateClass.MEASUREMENT


class PurifierTemperature(CoordinatorEntity, SensorEntity):
    """ Representation of Purifier Temperature """

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

        return str(self.purifier_data.id) + '_purifier_temperature'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "temperature"

    @property
    def native_value(self) -> int:
        """ Return current temperature in Celsius """

        return round((self.purifier_data.device_detail['state']['temp'] / 10))

    @property
    def native_unit_of_measurement(self) -> UnitOfTemperature:
        """ Return Celsius as the native unit """

        return UnitOfTemperature.CELSIUS

    @property
    def device_class(self) -> SensorDeviceClass:
        """ Return entity device class """

        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self) -> SensorStateClass:
        """ Return the type of state class """

        return SensorStateClass.MEASUREMENT


class AirPurified(CoordinatorEntity, SensorEntity):
    """ Representation of amount of air purified."""

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

        return str(self.purifier_data.id) + '_air_purified'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "air_purified"

    @property
    def native_value(self) -> int:
        """Return amount of air purified in cubic meters."""

        return round(self.purifier_data.device_detail['state']['refresh'])

    @property
    def native_unit_of_measurement(self) -> UnitOfVolume:
        """ Return cubic meters as the native unit """

        return UnitOfVolume.CUBIC_METERS

    @property
    def device_class(self) -> SensorDeviceClass:
        """ Return entity device class """

        return SensorDeviceClass.VOLUME

    @property
    def state_class(self) -> SensorStateClass:
        """ Return the type of state class """

        return SensorStateClass.TOTAL


class PurifierRSSI(CoordinatorEntity, SensorEntity):
    """Representation of purifier WiFi connection strength."""

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

        return str(self.purifier_data.id) + '_rssi'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "rssi"

    @property
    def native_value(self) -> int:
        """Return RSSI measurement."""

        return self.purifier_data.device_detail['state']['wifi']['rsq']

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


class PurifierLiquid(CoordinatorEntity, SensorEntity):
    """Representation of purifier liquid left."""

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

        return str(self.purifier_data.id) + '_liquid'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "liquid"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:cup-water'

    @property
    def native_value(self) -> int:
        """Return current percentage left"""

        return self.purifier_data.device_detail['state']['liquid']

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


class FoodLeft(CoordinatorEntity, SensorEntity):
    """Representation of percent food left."""

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

        return str(self.feeder_data.id) + '_food_left'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "food_left"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:food-drumstick'

    @property
    def native_value(self) -> int:
        """Return current percentage left"""

        return self.feeder_data.data['state']['percent']

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
