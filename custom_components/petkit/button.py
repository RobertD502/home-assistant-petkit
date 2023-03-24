"""Button platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import LitterBoxCommand, W5Command
from petkitaio.exceptions import BluetoothError
from petkitaio.model import Feeder, LitterBox, W5Fountain

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FEEDERS, LITTER_BOXES, WATER_FOUNTAINS
from .coordinator import PetKitDataUpdateCoordinator
from .exceptions import PetKitBluetoothError


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

        # D3 and D4
        if feeder_data.type in ['d3', 'd4']:
            buttons.extend((
                CancelManualFeed(coordinator, feeder_id),
            ))

        # D3
        if feeder_data.type == 'd3':
            buttons.extend((
                CallPet(coordinator, feeder_id),
            ))

    # Litter boxes
    for lb_id, lb_data in coordinator.data.litter_boxes.items():
        # Pura X
        buttons.extend((
            LBStartCleaning(coordinator, lb_id),
            LBPauseCleaning(coordinator, lb_id),
            LBOdorRemoval(coordinator, lb_id),
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

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.cancel_manual_feed(self.feeder_data)
        await self.coordinator.async_request_refresh()


class CallPet(CoordinatorEntity, ButtonEntity):
    """Representation of calling pet button for d3 feeder."""

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

        return str(self.feeder_data.id) + '_call_pet'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Call pet"

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

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.call_pet(self.feeder_data)
        await self.coordinator.async_request_refresh()


class LBStartCleaning(CoordinatorEntity, ButtonEntity):
    """Representation of litter box start/resume cleaning."""

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

        return str(self.lb_data.id) + '_start_cleaning'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Start/Resume cleaning"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:vacuum'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1

        if (lb_online and lb_power_on):
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.STARTCLEAN)
        await self.coordinator.async_request_refresh()


class LBPauseCleaning(CoordinatorEntity, ButtonEntity):
    """Representation of litter box pause cleaning."""

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

        return str(self.lb_data.id) + '_pause_cleaning'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Pause cleaning"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:pause'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1

        if (lb_online and lb_power_on):
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.PAUSECLEAN)
        await self.coordinator.async_request_refresh()


class LBOdorRemoval(CoordinatorEntity, ButtonEntity):
    """Representation of litter box odor removal."""

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

        return str(self.lb_data.id) + '_odor_removal'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Odor removal"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:scent'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1

        if (lb_online and lb_power_on):
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.ODORREMOVAL)
        await self.coordinator.async_request_refresh()


class LBResetDeodorizer(CoordinatorEntity, ButtonEntity):
    """Representation of litter box deodorizer reset."""

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

        return str(self.lb_data.id) + '_reset_deodorizer'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Reset deodorizer"

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:scent'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1

        if (lb_online and lb_power_on):
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.RESETDEODOR)
        await self.coordinator.async_request_refresh()
