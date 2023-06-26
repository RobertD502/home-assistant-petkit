"""Select platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import FeederSetting, LitterBoxSetting, W5Command
from petkitaio.exceptions import BluetoothError
from petkitaio.model import Feeder, LitterBox, W5Fountain

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import(
    CLEANING_INTERVAL_NAMED,
    DOMAIN,
    FEEDERS,
    FEEDER_MANUAL_FEED_OPTIONS,
    LIGHT_BRIGHTNESS_COMMAND,
    LIGHT_BRIGHTNESS_NAMED,
    LIGHT_BRIGHTNESS_OPTIONS,
    LITTER_BOXES,
    LITTER_TYPE_NAMED,
    MANUAL_FEED_NAMED,
    MINI_FEEDER_MANUAL_FEED_OPTIONS,
    PETKIT_COORDINATOR,
    WATER_FOUNTAINS,
    WF_MODE_COMMAND,
    WF_MODE_NAMED,
    WF_MODE_OPTIONS,
)
from .coordinator import PetKitDataUpdateCoordinator
from .exceptions import PetKitBluetoothError

LIGHT_BRIGHTNESS_TO_PETKIT = {v: k for (k, v) in LIGHT_BRIGHTNESS_COMMAND.items()}
LIGHT_BRIGHTNESS_TO_PETKIT_NUMBERED = {v: k for (k, v) in LIGHT_BRIGHTNESS_NAMED.items()}
WF_MODE_TO_PETKIT = {v: k for (k, v) in WF_MODE_COMMAND.items()}
WF_MODE_TO_PETKIT_NUMBERED = {v: k for (k, v) in WF_MODE_NAMED.items()}
MANUAL_FEED_TO_PETKIT = {v: k for (k, v) in MANUAL_FEED_NAMED.items()}
CLEANING_INTERVAL_TO_PETKIT = {v: k for (k, v) in CLEANING_INTERVAL_NAMED.items()}
LITTER_TYPE_TO_PETKIT = {v: k for (k, v) in LITTER_TYPE_NAMED.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Select Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][PETKIT_COORDINATOR]

    selects = []

    for wf_id, wf_data in coordinator.data.water_fountains.items():
        # Water Fountains (W5)
        if wf_data.ble_relay:
            selects.extend((
                WFLightBrightness(coordinator, wf_id),
                WFMode(coordinator, wf_id),
            ))
    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # D4 and Mini Feeders
        if feeder_data.type in ['d4', 'feedermini']:
            selects.append(
                ManualFeed(coordinator, feeder_id)
            )
        # D3 Feeder
        if feeder_data.type == 'd3':
            selects.append(
                Sound(coordinator, feeder_id)
            )

    # Litter boxes
    for lb_id, lb_data in coordinator.data.litter_boxes.items():
        # Pura X & Pura MAX
        selects.extend((
            LBCleaningInterval(coordinator, lb_id),
            LBLitterType(coordinator, lb_id),
        ))

    async_add_entities(selects)

class WFLightBrightness(CoordinatorEntity, SelectEntity):
    """Representation of Water Fountain Light Brightness level."""

    def __init__(self, coordinator, wf_id):
        super().__init__(coordinator)
        self.wf_id = wf_id

    @property
    def wf_data(self) -> W5Fountain:
        """Handle coordinator Water Fountain data."""

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

        return str(self.wf_data.id) + '_light_brightness'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "light_brightness"

    @property
    def icon(self) -> str:
        """Set icon."""

        brightness = self.wf_data.data['settings']['lampRingBrightness']

        if brightness == 1:
            return 'mdi:lightbulb-on-30'
        if brightness == 2:
            return 'mdi:lightbulb-on-50'
        else:
            return 'mdi:lightbulb-on'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def available(self) -> bool:
        """Determine if device is available.

        Return true if there is a valid relay
        and the main relay device is online.
        """

        if self.wf_data.ble_relay and (self.wf_data.data['settings']['lampRingSwitch'] == 1):
            return True
        else:
            return False

    @property
    def current_option(self) -> str:
        """Returns currently active brightness setting."""

        current_brightness = self.wf_data.data['settings']['lampRingBrightness']
        return LIGHT_BRIGHTNESS_NAMED[current_brightness]

    @property
    def options(self) -> list[str]:
        """Return list of all available brightness levels."""

        return LIGHT_BRIGHTNESS_OPTIONS

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_petkit = LIGHT_BRIGHTNESS_TO_PETKIT.get(option)
        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, ha_to_petkit)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try setting light brightness again.')
        else:
            self.wf_data.data['settings']['lampRingBrightness'] = LIGHT_BRIGHTNESS_TO_PETKIT_NUMBERED.get(option)
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

class WFMode(CoordinatorEntity, SelectEntity):
    """Representation of Water Fountain mode."""

    def __init__(self, coordinator, wf_id):
        super().__init__(coordinator)
        self.wf_id = wf_id

    @property
    def wf_data(self) -> W5Fountain:
        """Handle coordinator Water Fountain data."""

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

        return str(self.wf_data.id) + '_mode'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "mode"

    @property
    def icon(self) -> str:
        """Set icon."""

        mode = self.wf_data.data['mode']

        if mode == 1:
            return 'mdi:waves'
        if mode == 2:
            return 'mdi:brain'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def available(self) -> bool:
        """Determine if device is available.

        Return true if there is a valid relay
        and the main relay device is online.
        """

        if self.wf_data.ble_relay:
            return True
        else:
            return False

    @property
    def current_option(self) -> str:
        """Returns currently active mode."""

        mode = self.wf_data.data['mode']
        return WF_MODE_NAMED[mode]

    @property
    def options(self) -> list[str]:
        """Return list of all available modes."""

        return WF_MODE_OPTIONS

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_petkit = WF_MODE_TO_PETKIT.get(option)
        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, ha_to_petkit)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try setting mode again.')
        else:
            self.wf_data.data['mode'] = WF_MODE_TO_PETKIT_NUMBERED.get(option)
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

class ManualFeed(CoordinatorEntity, SelectEntity):
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
    def current_option(self) -> str:
        """Returns blank option by default."""

        return MANUAL_FEED_NAMED[0]

    @property
    def options(self) -> list[str]:
        """Return list of all available manual feed amounts."""

        if self.feeder_data.type == 'feedermini':
            return MINI_FEEDER_MANUAL_FEED_OPTIONS
        else:
            return FEEDER_MANUAL_FEED_OPTIONS

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_petkit = MANUAL_FEED_TO_PETKIT.get(option)

        await self.coordinator.client.manual_feeding(self.feeder_data, ha_to_petkit)
        await self.coordinator.async_request_refresh()


class Sound(CoordinatorEntity, SelectEntity):
    """Representation of D3 Sound selection."""

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

        return str(self.feeder_data.id) + '_sound'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "sound"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:surround-sound'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    @property
    def current_option(self) -> str:
        """Return currently selected sound."""

        available_sounds = self.feeder_data.sound_list
        current_sound_id = self.feeder_data.data['settings']['selectedSound']
        return available_sounds[current_sound_id]

    @property
    def options(self) -> list[str]:
        """Return list of all available sound names."""

        available_sounds = self.feeder_data.sound_list
        sound_names = list(available_sounds.values())
        return sound_names

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        available_sounds = self.feeder_data.sound_list
        NAME_TO_SOUND_ID = {v: k for (k, v) in available_sounds.items()}
        ha_to_petkit = NAME_TO_SOUND_ID.get(option)

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SELECTED_SOUND, ha_to_petkit)
        self.feeder_data.data['settings']['selectedSound'] = ha_to_petkit
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBCleaningInterval(CoordinatorEntity, SelectEntity):
    """Representation of litter box cleaning interval."""

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

        return str(self.lb_data.id) + '_cleaning_interval'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "cleaning_interval"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.lb_data.device_detail['settings']['autoIntervalMin'] == 0:
            return 'mdi:timer-off'
        else:
            return 'mdi:timer'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        kitten_mode_off = self.lb_data.device_detail['settings']['kitten'] == 0
        auto_clean = self.lb_data.device_detail['settings']['autoWork'] == 1
        avoid_repeat = self.lb_data.device_detail['settings']['avoidRepeat'] == 1

        if self.lb_data.device_detail['state']['pim'] != 0:
            # Only available if kitten mode is off and auto clean and avoid repeat are on
            if (kitten_mode_off and auto_clean and avoid_repeat):
                return True
            else:
                return False
        else:
            return False

    @property
    def current_option(self) -> str:
        """Return currently selected interval."""

        return CLEANING_INTERVAL_NAMED[self.lb_data.device_detail['settings']['autoIntervalMin']]

    @property
    def options(self) -> list[str]:
        """Return list of all available intervals."""

        intervals = list(CLEANING_INTERVAL_NAMED.values())
        return intervals

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_petkit = CLEANING_INTERVAL_TO_PETKIT.get(option)

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.CLEAN_INTERVAL, ha_to_petkit)
        self.lb_data.device_detail['settings']['autoIntervalMin'] = ha_to_petkit
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBLitterType(CoordinatorEntity, SelectEntity):
    """Representation of litter box litter type."""

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

        return str(self.lb_data.id) + '_litter_type'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "litter_type"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:grain'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    @property
    def current_option(self) -> str:
        """Return currently selected type."""

        return LITTER_TYPE_NAMED[self.lb_data.device_detail['settings']['sandType']]

    @property
    def options(self) -> list[str]:
        """Return list of all available litter types."""

        litter_types = list(LITTER_TYPE_NAMED.values())
        return litter_types

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        ha_to_petkit = LITTER_TYPE_TO_PETKIT.get(option)

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.SAND_TYPE, ha_to_petkit)
        self.lb_data.device_detail['settings']['sandType'] = ha_to_petkit
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
