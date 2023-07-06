"""Button platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import FeederCommand, LitterBoxCommand, W5Command
from petkitaio.exceptions import BluetoothError
from petkitaio.model import Feeder, LitterBox, W5Fountain

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FEEDERS, LITTER_BOXES, PETKIT_COORDINATOR, WATER_FOUNTAINS
from .coordinator import PetKitDataUpdateCoordinator
from .exceptions import PetKitBluetoothError


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Button Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][PETKIT_COORDINATOR]

    buttons = []

    for wf_id, wf_data in coordinator.data.water_fountains.items():
        # Water Fountains (W5)
        if wf_data.ble_relay:
            buttons.append(
                WFResetFilter(coordinator, wf_id)
            )

    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # All Feeders
        buttons.append(
            ResetDesiccant(coordinator, feeder_id)
        )

        # D3, D4, and D4s
        if feeder_data.type in ['d3', 'd4', 'd4s', 'feeder']:
            buttons.append(
                CancelManualFeed(coordinator, feeder_id)
            )

        # D3
        if feeder_data.type == 'd3':
            buttons.append(
                CallPet(coordinator, feeder_id)
            )

        # D4s
        if feeder_data.type == 'd4s':
            buttons.append(
                FoodReplenished(coordinator, feeder_id)
            )

        # Fresh Element
        if feeder_data.type == 'feeder':
            buttons.extend((
                StartFeederCal(coordinator, feeder_id),
                StopFeederCal(coordinator, feeder_id)
            ))

    # Litter boxes
    for lb_id, lb_data in coordinator.data.litter_boxes.items():
        # Pura X & Pura MAX
        if lb_data.type in ['t3', 't4']:
            buttons.extend((
                LBStartCleaning(coordinator, lb_id),
                LBPauseCleaning(coordinator, lb_id)
            ))
        # Pura X & Pura MAX with Pura Air
        if (lb_data.type == 't3') or ('k3Device' in lb_data.device_detail):
            buttons.extend((
                LBOdorRemoval(coordinator, lb_id),
                LBResetDeodorizer(coordinator, lb_id)
            ))
        # Pura MAX
        if lb_data.type == 't4':
            buttons.extend((
                N50Reset(coordinator, lb_id),
                MAXStartMaint(coordinator, lb_id),
                MAXExitMaint(coordinator, lb_id),
                MAXPauseExitMaint(coordinator, lb_id),
                MAXResumeExitMaint(coordinator, lb_id),
                MAXDumpLitter(coordinator, lb_id),
                MAXPauseDumping(coordinator, lb_id),
                MAXResumeDumping(coordinator, lb_id)
            ))
            # Pura MAX with Pura Air
            if 'k3Device' in lb_data.device_detail:
                buttons.append(
                    MAXLightOn(coordinator, lb_id)
                )

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
            "model": WATER_FOUNTAINS.get(self.wf_data.data["typeCode"], "Unidentified Water Fountain") if "typeCode" in self.wf_data.data else "Unidentified Water Fountain",
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_reset_filter'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "reset_filter"

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
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.RESET_FILTER)
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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "reset_desiccant"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "cancel_manual_feed"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "call_pet"

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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "start_cleaning"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:vacuum'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1

        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.START_CLEAN)
        await asyncio.sleep(1.5)
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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "pause_cleaning"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:pause'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1

        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.PAUSE_CLEAN)
        await asyncio.sleep(1.5)
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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "odor_removal"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:scent'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1

        # Pura Air deodorizer
        if self.lb_data.type == 't4':
            if 'k3Device' in self.lb_data.device_detail:
                if lb_online and lb_power_on:
                    return True
                else:
                    return False
            else:
                return False
        # Pura X
        else:
            if lb_online and lb_power_on:
                return True
            else:
                return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.ODOR_REMOVAL)
        await asyncio.sleep(1.5)
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
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        # Pura MAX
        if self.lb_data.type == 't4':
            return "reset_pura_air_liquid"
        # Pura X
        else:
            return "reset_deodorizer"

    @property
    def icon(self) -> str:
        """Set icon."""

        # Pura MAX
        if self.lb_data.type == 't4':
            return 'mdi:cup'
        # Pura X
        else:
            return 'mdi:scent'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1

        # Pura Air deodorizer
        if self.lb_data.type == 't4':
            if 'k3Device' in self.lb_data.device_detail:
                if lb_online and lb_power_on:
                    return True
                else:
                    return False
            else:
                return False
        # Pura X
        else:
            if lb_online and lb_power_on:
                return True
            else:
                return False

    async def async_press(self) -> None:
        """Handle the button press."""

        # Pura MAX
        if self.lb_data.type == 't4':
            await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.RESET_MAX_DEODOR)
        # Pura X:
        else:
            await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.RESET_DEODOR)
        await self.coordinator.async_request_refresh()


class N50Reset(CoordinatorEntity, ButtonEntity):
    """Representation of Pura MAX N50 deodorant reset."""

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

        return str(self.lb_data.id) + '_n50_reset'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "n50_reset"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:air-filter'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.reset_pura_max_deodorizer(self.lb_data)
        await self.coordinator.async_request_refresh()


class MAXLightOn(CoordinatorEntity, ButtonEntity):
    """Representation of Pura MAX light button."""

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

        return str(self.lb_data.id) + '_max_light'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "light_on"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:lightbulb-on'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            # Make sure Pura Air is connected
            if 'k3Device' in self.lb_data.device_detail:
                return True
            else:
                return False
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.LIGHT_ON)
        await asyncio.sleep(1.5)
        await self.coordinator.async_request_refresh()


class MAXStartMaint(CoordinatorEntity, ButtonEntity):
    """Representation of starting Pura MAX maintenance mode."""

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

        return str(self.lb_data.id) + '_start_max_maint'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "start_maintenance"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:tools'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.START_MAINTENANCE)
        await asyncio.sleep(1.5)
        await self.coordinator.async_request_refresh()


class MAXExitMaint(CoordinatorEntity, ButtonEntity):
    """Representation of exiting Pura MAX maintenance mode."""

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

        return str(self.lb_data.id) + '_exit_max_maint'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "exit_maintenance"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:tools'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.EXIT_MAINTENANCE)
        await asyncio.sleep(1.5)
        await self.coordinator.async_request_refresh()


class MAXPauseExitMaint(CoordinatorEntity, ButtonEntity):
    """Representation of pausing exiting Pura MAX maintenance mode."""

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

        return str(self.lb_data.id) + '_pause_exit_max_maint'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "pause_exit_maintenance"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:tools'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.PAUSE_MAINTENANCE_EXIT)
        await asyncio.sleep(1.5)
        await self.coordinator.async_request_refresh()


class MAXResumeExitMaint(CoordinatorEntity, ButtonEntity):
    """Representation of continuing exiting Pura MAX maintenance mode."""

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

        return str(self.lb_data.id) + '_resume_exit_max_maint'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "resume_exit_maintenance"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:tools'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.RESUME_MAINTENANCE_EXIT)
        await asyncio.sleep(1.5)
        await self.coordinator.async_request_refresh()


class MAXDumpLitter(CoordinatorEntity, ButtonEntity):
    """Representation of dumping cat litter."""

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

        return str(self.lb_data.id) + '_dump_litter'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "dump_litter"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:landslide'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.DUMP_LITTER)
        await asyncio.sleep(1.5)
        await self.coordinator.async_request_refresh()


class MAXPauseDumping(CoordinatorEntity, ButtonEntity):
    """Representation of pausing dumping cat litter."""

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

        return str(self.lb_data.id) + '_pause_dump_litter'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "pause_dump_litter"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:landslide'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.PAUSE_LITTER_DUMP)
        await asyncio.sleep(1.5)
        await self.coordinator.async_request_refresh()


class MAXResumeDumping(CoordinatorEntity, ButtonEntity):
    """Representation of resuming dumping cat litter."""

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

        return str(self.lb_data.id) + '_resume_dump_litter'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "resume_dump_litter"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:landslide'

    @property
    def available(self) -> bool:
        """Only make available if device is online and on."""

        lb_online = self.lb_data.device_detail['state']['pim'] == 1
        lb_power_on = self.lb_data.device_detail['state']['power'] == 1


        if lb_online and lb_power_on:
            return True
        else:
            return False

    async def async_press(self) -> None:
        """Handle the button press."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.RESUME_LITTER_DUMP)
        await asyncio.sleep(1.5)
        await self.coordinator.async_request_refresh()


class FoodReplenished(CoordinatorEntity, ButtonEntity):
    """Representation of food replenished command button."""

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

        return str(self.feeder_data.id) + '_food_replenished'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "food_replenished"

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

        await self.coordinator.client.food_replenished(self.feeder_data)

        self.feeder_data.data['state']['food1'] = 1
        self.feeder_data.data['state']['food2'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class StartFeederCal(CoordinatorEntity, ButtonEntity):
    """Representation of fresh element feeder start calibration button."""

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

        return str(self.feeder_data.id) + '_start_cal'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "start_cal"

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

        await self.coordinator.client.fresh_element_calibration(self.feeder_data, FeederCommand.START_CALIBRATION)
        await self.coordinator.async_request_refresh()


class StopFeederCal(CoordinatorEntity, ButtonEntity):
    """Representation of fresh element feeder stop calibration button."""

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

        return str(self.feeder_data.id) + '_stop_cal'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "stop_cal"

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

        await self.coordinator.client.fresh_element_calibration(self.feeder_data, FeederCommand.STOP_CALIBRATION)
        await self.coordinator.async_request_refresh()
