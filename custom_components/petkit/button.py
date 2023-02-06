"""Button platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import W5Command
from petkitaio.model import Feeder, W5Fountain

from homeassistant.components.button import ButtonEntity
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
    """Set Up PetKit Button Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    buttons = []

    for wf_id, wf_data in coordinator.data.water_fountains.items():
        # Water Fountains (W5)
        if wf_data.ble_relay:
            buttons.extend((
                WFResetFilter(coordinator, wf_id),
            ))

    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # All Feeders
        buttons.extend((
            ResetDesiccant(coordinator, feeder_id),
        ))

        if feeder_data.type == 'd4':
            buttons.extend((
                CancelManualFeed(coordinator, feeder_id),
            ))

    async_add_entities(buttons)


class WFResetFilter(CoordinatorEntity, ButtonEntity):
    """Representation of Water Fountain filter reset button."""

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

        return str(self.wf_data.id) + '_reset_filter'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Reset filter"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

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

    async def async_press(self) -> None:
        """Handle the button press."""

        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.RESETFILTER)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try resetting filter again.')
        else:
            self.wf_data.data['filterPercent'] = 100
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

class ResetDesiccant(CoordinatorEntity, ButtonEntity):
    """Representation of feeder desiccant reset button."""

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

        return str(self.feeder_data.id) + '_reset_desiccant'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Reset desiccant"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.reset_feeder_desiccant(self.feeder_data)

        self.feeder_data.data['state']['desiccantLeftDays'] = 30
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

class CancelManualFeed(CoordinatorEntity, ButtonEntity):
    """Representation of manual feed cancelation button."""

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

        return str(self.feeder_data.id) + '_cancel_manual_feed'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Cancel manual feed"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.cancel_manual_feed(self.feeder_data)
        await self.coordinator.async_request_refresh()
