"""Select platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import W5Command
from petkitaio.exceptions import BluetoothError
from petkitaio.model import Feeder, W5Fountain

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import(
    DOMAIN,
    FEEDERS,
    FEEDER_MANUAL_FEED_OPTIONS,
    LIGHT_BRIGHTNESS_COMMAND,
    LIGHT_BRIGHTNESS_NAMED,
    LIGHT_BRIGHTNESS_OPTIONS,
    MANUAL_FEED_NAMED,
    MINI_FEEDER_MANUAL_FEED_OPTIONS,
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


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Select Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    selects = []

    for wf_id, wf_data in coordinator.data.water_fountains.items():
        # Water Fountains (W5)
        if wf_data.ble_relay:
            selects.extend((
                WFLightBrightness(coordinator, wf_id),
                WFMode(coordinator, wf_id),
            ))
    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # All Feeders
        selects.extend((
            ManualFeed(coordinator, feeder_id),
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
            "model": WATER_FOUNTAINS[self.wf_data.type],
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_light_brightness'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Light brightness"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

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

        if self.wf_data.ble_relay:
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
            "model": WATER_FOUNTAINS[self.wf_data.type],
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_mode'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Mode"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Manual feed"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

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
