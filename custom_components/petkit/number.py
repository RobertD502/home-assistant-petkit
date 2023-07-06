"""Number platform for PetKit integration."""
from __future__ import annotations

from typing import Any

from petkitaio.constants import FeederSetting, LitterBoxSetting, PetSetting
from petkitaio.exceptions import PetKitError
from petkitaio.model import Feeder, LitterBox, Pet

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import DOMAIN, FEEDERS, LITTER_BOXES, PETKIT_COORDINATOR
from .coordinator import PetKitDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Number Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][PETKIT_COORDINATOR]

    numbers = []

    # Pets
    for pet_id, pet_data in coordinator.data.pets.items():
        numbers.append(
            PetWeight(coordinator, pet_id)
        )

    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # Only D3 Feeder
        if feeder_data.type == 'd3':
            numbers.extend((
                Surplus(coordinator, feeder_id),
                Volume(coordinator, feeder_id),
                ManualFeed(coordinator, feeder_id),
            ))

        # Only D4s Feeder
        if feeder_data.type == 'd4s':
            numbers.append(
                MinEatingDuration(coordinator, feeder_id)
            )

        # Fresh Element Feeder
        if feeder_data.type == 'feeder':
            numbers.append(
                FreshElementManualFeed(coordinator, feeder_id)
            )

    for lb_id, lb_data in coordinator.data.litter_boxes.items():
        # Pura X & Pura MAX
        numbers.append(
            LBCleaningDelay(coordinator, lb_id)
        )

    async_add_entities(numbers)


class PetWeight(CoordinatorEntity, NumberEntity):
    """Representation of Pet Weight."""

    def __init__(self, coordinator, pet_id):
        super().__init__(coordinator)
        self.pet_id = pet_id

    @property
    def pet_data(self) -> Pet:
        """Handle coordinator Pet data."""

        return self.coordinator.data.pets[self.pet_id]

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

        return self.pet_data.id + '_set_weight'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "set_weight"

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
        """Returns current weight."""

        pet_weight = self.pet_data.data['weight']
        if self.hass.config.units is METRIC_SYSTEM:
            return pet_weight
        else:
            return round((pet_weight * 2.2046226), 1)

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return kilograms or pounds."""

        if self.hass.config.units is METRIC_SYSTEM:
            return UnitOfMass.KILOGRAMS
        else:
            return UnitOfMass.POUNDS

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return weight device class."""

        return NumberDeviceClass.WEIGHT

    @property
    def mode(self) -> NumberMode:
        """Return box mode."""

        return NumberMode.BOX

    @property
    def native_min_value(self) -> float:
        """Return minimum allowed value."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 1.0
        else:
            return 2.2

    @property
    def native_max_value(self) -> float:
        """Return max value allowed."""

        if self.hass.config.units is METRIC_SYSTEM:
            return 150.0
        else:
            return 330.0

    @property
    def native_step(self) -> int:
        """Return stepping by 10 grams."""

        return 0.1

    async def async_set_native_value(self, value: int) -> None:
        """Update the current value."""

        if self.hass.config.units is METRIC_SYSTEM:
            # Always send value with one decimal point in case user sends more decimal points or none
            converted_value = round(value, 1)
        else:
            converted_value = round((value * 0.4535924), 1)
        await self.coordinator.client.update_pet_settings(self.pet_data, PetSetting.WEIGHT, converted_value)
        await self.coordinator.async_request_refresh()


class Surplus(CoordinatorEntity, NumberEntity):
    """Representation of D3 Feeder surplus amount."""

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

        return str(self.feeder_data.id) + '_surplus'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "surplus"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:food-drumstick'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def native_value(self) -> int:
        """Returns current surplus setting."""

        return self.feeder_data.data['settings']['surplus']

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return grams."""

        return UnitOfMass.GRAMS

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return weight device class."""

        return NumberDeviceClass.WEIGHT

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> int:
        """Return minimum allowed value."""

        return 20

    @property
    def native_max_value(self) -> int:
        """Return max value allowed."""

        return 100

    @property
    def native_step(self) -> int:
        """Return stepping by 10 grams."""

        return 10

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_set_native_value(self, value: int) -> None:
        """Update the current value."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SURPLUS, int(value))
        self.feeder_data.data['settings']['surplus'] = value
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class Volume(CoordinatorEntity, NumberEntity):
    """Representation of D3 Feeder speaker volume."""

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

        return str(self.feeder_data.id) + '_volume'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "volume"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:volume-high'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def native_value(self) -> int:
        """Returns current volume setting."""

        return self.feeder_data.data['settings']['volume']

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> int:
        """Return minimum allowed value."""

        return 1

    @property
    def native_max_value(self) -> int:
        """Return max value allowed."""

        return 9

    @property
    def native_step(self) -> int:
        """Return stepping by 1."""

        return 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_set_native_value(self, value: int) -> None:
        """Update the current value."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.VOLUME, int(value))
        self.feeder_data.data['settings']['volume'] = value
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class ManualFeed(CoordinatorEntity, NumberEntity):
    """Representation of D3 Feeder manual feeding."""

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
    def native_value(self) -> int:
        """Returns lowest amount allowed."""

        return 4

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return grams."""

        return UnitOfMass.GRAMS

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return weight device class."""

        return NumberDeviceClass.WEIGHT

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> int:
        """Return minimum allowed value."""

        return 4

    @property
    def native_max_value(self) -> int:
        """Return max value allowed."""

        return 200

    @property
    def native_step(self) -> int:
        """Return stepping by 1."""

        return 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_set_native_value(self, value: int) -> None:
        """Update the current value."""

        if (value < 5) or (value > 200):
            raise PetKitError(f'{self.feeder_data.data["name"]} can only accept manual feeding amounts between 5 to 200 grams')
        else:
            await self.coordinator.client.manual_feeding(self.feeder_data, int(value))
            await self.coordinator.async_request_refresh()


class LBCleaningDelay(CoordinatorEntity, NumberEntity):
    """Representation of litter box cleaning delay."""

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

        return str(self.lb_data.id) + '_cleaning_delay'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "cleaning_delay"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:motion-pause'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def native_value(self) -> int:
        """Returns currently set delay in minutes."""

        return (self.lb_data.device_detail['settings']['stillTime'] / 60)

    @property
    def native_unit_of_measurement(self) -> UnitOfTime:
        """Return minutes."""

        return UnitOfTime.MINUTES

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> int:
        """Return minimum allowed value."""

        return 0

    @property
    def native_max_value(self) -> int:
        """Return max value allowed."""

        return 60

    @property
    def native_step(self) -> int:
        """Return stepping by 1."""

        return 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        kitten_mode_off = self.lb_data.device_detail['settings']['kitten'] == 0
        auto_clean = self.lb_data.device_detail['settings']['autoWork'] == 1

        if self.lb_data.device_detail['state']['pim'] != 0:
            # Only available if kitten mode off and auto cleaning on
            if (kitten_mode_off and auto_clean):
                return True
            else:
                return False
        else:
            return False

    async def async_set_native_value(self, value: int) -> None:
        """Update the current value."""

        seconds = int(value * 60)
        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DELAY_CLEAN_TIME, seconds)
        self.lb_data.device_detail['settings']['stillTime'] = seconds
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class MinEatingDuration(CoordinatorEntity, NumberEntity):
    """Representation of D4s shortest eating duration."""

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

        return str(self.feeder_data.id) + '_min_eating_duration'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "min_eating_duration"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:clock-digital'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def native_value(self) -> int:
        """Returns current timer setting."""

        return self.feeder_data.data['settings']['shortest']

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return seconds."""

        return UnitOfTime.SECONDS

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> int:
        """Return minimum allowed value."""

        return 3

    @property
    def native_max_value(self) -> int:
        """Return max value allowed."""

        return 60

    @property
    def native_step(self) -> int:
        """Return stepping by 1 second."""

        return 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_set_native_value(self, value: int) -> None:
        """Update the current value."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MIN_EAT_DURATION, int(value))
        self.feeder_data.data['settings']['shortest'] = value
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class FreshElementManualFeed(CoordinatorEntity, NumberEntity):
    """Representation of Fresh Element feeder manual feeding."""

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
    def native_value(self) -> int:
        """Returns lowest amount allowed."""

        return 0

    @property
    def native_unit_of_measurement(self) -> UnitOfMass:
        """Return grams."""

        return UnitOfMass.GRAMS

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return weight device class."""

        return NumberDeviceClass.WEIGHT

    @property
    def mode(self) -> NumberMode:
        """Return slider mode."""

        return NumberMode.SLIDER

    @property
    def native_min_value(self) -> int:
        """Return minimum allowed value."""

        return 0

    @property
    def native_max_value(self) -> int:
        """Return max value allowed."""

        return 400

    @property
    def native_step(self) -> int:
        """Return stepping by 1."""

        return 20

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_set_native_value(self, value: int) -> None:
        """Update the current value."""

        if (value < 20) or (value > 400):
            raise PetKitError(f'{self.feeder_data.data["name"]} can only accept manual feeding amounts between 20 to 400 grams')
        else:
            await self.coordinator.client.manual_feeding(self.feeder_data, int(value))
            await self.coordinator.async_request_refresh()
