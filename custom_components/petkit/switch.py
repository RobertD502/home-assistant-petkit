"""Switch platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import FeederSetting, LitterBoxCommand, LitterBoxSetting, PurifierSetting, W5Command
from petkitaio.exceptions import BluetoothError
from petkitaio.model import Feeder, LitterBox, Purifier, W5Fountain

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FEEDERS, LITTER_BOXES, PETKIT_COORDINATOR, PURIFIERS, WATER_FOUNTAINS
from .coordinator import PetKitDataUpdateCoordinator
from .exceptions import PetKitBluetoothError


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up PetKit Switch Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][PETKIT_COORDINATOR]

    switches = []

    for wf_id, wf_data in coordinator.data.water_fountains.items():
        # Water Fountains (W5)
        if wf_data.ble_relay:
            switches.extend((
                WFLight(coordinator, wf_id),
                WFPower(coordinator, wf_id),
                WFDisturb(coordinator, wf_id),
            ))

    for feeder_id, feeder_data in coordinator.data.feeders.items():
        # All Feeders
        switches.extend((
            IndicatorLight(coordinator, feeder_id),
            ChildLock(coordinator, feeder_id),
        ))

        # D4 and D4s Feeder
        if feeder_data.type in ['d4', 'd4s']:
            switches.extend((
                ShortageAlarm(coordinator, feeder_id),
                DispenseTone(coordinator, feeder_id),
            ))

        # D3 Feeder
        if feeder_data.type == 'd3':
            switches.extend((
                VoiceDispense(coordinator, feeder_id),
                DoNotDisturb(coordinator, feeder_id),
                SurplusControl(coordinator, feeder_id),
                SystemNotification(coordinator, feeder_id),
            ))

    # Litter boxes
    for lb_id, lb_data in coordinator.data.litter_boxes.items():
        # Pura X & Pura MAX
        switches.extend((
            LBAutoClean(coordinator, lb_id),
            LBAvoidRepeat(coordinator, lb_id),
            LBDoNotDisturb(coordinator, lb_id),
            LBPeriodicCleaning(coordinator, lb_id),
            LBKittenMode(coordinator, lb_id),
            LBDisplay(coordinator, lb_id),
            LBChildLock(coordinator, lb_id),
            LBLightWeight(coordinator, lb_id),
            LBPower(coordinator, lb_id)
        ))
        # Pura X & Pura MAX with Pura Air
        if (lb_data.type == 't3') or ('k3Device' in lb_data.device_detail):
            switches.extend((
                LBAutoOdor(coordinator, lb_id),
                LBPeriodicOdor(coordinator, lb_id)
            ))
        # Pura MAX
        if lb_data.type == 't4':
            switches.extend((
                LBContRotation(coordinator, lb_id),
                LBDeepCleaning(coordinator, lb_id)
            ))
            # Pura MAX with Pura Air
            if 'k3Device' in lb_data.device_detail:
                switches.append(
                    LBDeepDeodor(coordinator, lb_id)
                )

    # Purifiers
    for purifier_id, purifier_data in coordinator.data.purifiers.items():
        switches.extend((
            PurifierLight(coordinator, purifier_id),
            PurifierTone(coordinator, purifier_id)
        ))

    async_add_entities(switches)


class WFLight(CoordinatorEntity, SwitchEntity):
    """Representation of Water Fountain light switch."""

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

        return str(self.wf_data.id) + '_light'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "light"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:lightbulb'
        else:
            return 'mdi:lightbulb-off'

    @property
    def is_on(self) -> bool:
        """Determine if light is on."""

        return self.wf_data.data['settings']['lampRingSwitch'] == 1

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

    async def async_turn_on(self, **kwargs) -> None:
        """Turn light on."""

        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.LIGHT_ON)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try turning on the light again.')
        else:
            self.wf_data.data['settings']['lampRingSwitch'] = 1
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn light off."""

        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.LIGHT_OFF)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try turning off the light again.')
        else:
            self.wf_data.data['settings']['lampRingSwitch'] = 0
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

class WFPower(CoordinatorEntity, SwitchEntity):
    """Representation of Water Fountain power switch."""

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

        return str(self.wf_data.id) + '_power'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "power"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:power-plug'
        else:
            return 'mdi:power-plug-off'

    @property
    def is_on(self) -> bool:
        """Determine if water fountain is running."""

        return self.wf_data.data['powerStatus'] == 1

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

    async def async_turn_on(self, **kwargs) -> None:
        """Turn power on.

        Turning power on, puts the device back to the
        mode (normal, smart) it was in before it was paused.
        """

        if self.wf_data.data['mode'] == 1:
            command = W5Command.NORMAL
        else:
            command = W5Command.SMART

        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, command)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try turning on the water fountain again.')
        else:
            self.wf_data.data['powerStatus'] = 1
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn power off.

        This is equivalent to pausing the water fountain
        from the app.
        """

        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.PAUSE)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try turning off the water fountain again.')
        else:
            self.wf_data.data['powerStatus'] = 0
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

class WFDisturb(CoordinatorEntity, SwitchEntity):
    """Representation of Water Fountain do not disturb switch."""

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

        return str(self.wf_data.id) + '_disturb'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "do_not_disturb"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:sleep'
        else:
            return 'mdi:sleep-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if DND is on."""

        return self.wf_data.data['settings']['noDisturbingSwitch'] == 1

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

    async def async_turn_on(self, **kwargs) -> None:
        """Turn DND on."""

        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.DO_NOT_DISTURB)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try turning on Do Not Disturb again.')
        else:
            self.wf_data.data['settings']['noDisturbingSwitch'] = 1
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn DND off."""

        try:
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.DO_NOT_DISTURB_OFF)
        except BluetoothError:
            raise PetKitBluetoothError(f'Bluetooth connection to {self.wf_data.data["name"]} failed. Please try turning off Do Not Disturb again.')
        else:
            self.wf_data.data['settings']['noDisturbingSwitch'] = 0
            self.async_write_ha_state()
            await asyncio.sleep(1)
            await self.coordinator.async_request_refresh()

class IndicatorLight(CoordinatorEntity, SwitchEntity):
    """Representation of Feeder indicator light switch."""

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

        return str(self.feeder_data.id) + '_indicator_light'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "indicator_light"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:lightbulb'
        else:
            return 'mdi:lightbulb-off'

    @property
    def is_on(self) -> bool:
        """Determine if indicator light is on."""

        return self.feeder_data.data['settings']['lightMode'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn indicator light on."""

        if self.feeder_data.type == 'feedermini':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MINI_INDICATOR_LIGHT, 1)
        elif self.feeder_data.type == 'feeder':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.FRESH_ELEMENT_INDICATOR_LIGHT, 1)
        else:
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.INDICATOR_LIGHT, 1)

        self.feeder_data.data['settings']['lightMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn indicator light off."""

        if self.feeder_data.type == 'feedermini':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MINI_INDICATOR_LIGHT, 0)
        elif self.feeder_data.type == 'feeder':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.FRESH_ELEMENT_INDICATOR_LIGHT, 0)
        else:
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.INDICATOR_LIGHT, 0)

        self.feeder_data.data['settings']['lightMode'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

class ChildLock(CoordinatorEntity, SwitchEntity):
    """Representation of Feeder child lock switch."""

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

        return str(self.feeder_data.id) + '_child_lock'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "child_lock"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:lock'
        else:
            return 'mdi:lock-open'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if child lock is on."""

        return self.feeder_data.data['settings']['manualLock'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn child lock on."""

        if self.feeder_data.type == 'feedermini':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MINI_CHILD_LOCK, 1)
        elif self.feeder_data.type == 'feeder':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.FRESH_ELEMENT_CHILD_LOCK, 1)
        else:
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.CHILD_LOCK, 1)

        self.feeder_data.data['settings']['manualLock'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn child lock off."""

        if self.feeder_data.type == 'feedermini':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MINI_CHILD_LOCK, 0)
        elif self.feeder_data.type == 'feeder':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.FRESH_ELEMENT_CHILD_LOCK, 0)
        else:
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.CHILD_LOCK, 0)

        self.feeder_data.data['settings']['manualLock'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

class ShortageAlarm(CoordinatorEntity, SwitchEntity):
    """Representation of Feeder shortage alarm."""

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

        return str(self.feeder_data.id) + '_food_shortage_alarm'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "food_shortage_alarm"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:alarm'
        else:
            return 'mdi:alarm-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if food shortage alarm is on."""

        return self.feeder_data.data['settings']['foodWarn'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn food shortage alarm on."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SHORTAGE_ALARM, 1)
        self.feeder_data.data['settings']['foodWarn'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn food shortage alarm off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SHORTAGE_ALARM, 0)
        self.feeder_data.data['settings']['foodWarn'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

class DispenseTone(CoordinatorEntity, SwitchEntity):
    """Representation of dispense tone switch."""

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

        return str(self.feeder_data.id) + '_dispense_tone'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "dispense_tone"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:ear-hearing'
        else:
            return 'mdi:ear-hearing-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if food dispense tone is on."""

        if self.feeder_data.type == 'd4s':
            return self.feeder_data.data['settings']['feedTone'] == 1
        else:
            return self.feeder_data.data['settings']['feedSound'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn dispense tone on."""

        if self.feeder_data.type == 'd4s':
            setting = FeederSetting.FEED_TONE
        else:
            setting = FeederSetting.DISPENSE_TONE
        await self.coordinator.client.update_feeder_settings(self.feeder_data, setting, 1)

        if self.feeder_data.type == 'd4s':
            self.feeder_data.data['settings']['feedTone'] = 1
        else:
            self.feeder_data.data['settings']['feedSound'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn dispense tone off."""

        if self.feeder_data.type == 'd4s':
            setting = FeederSetting.FEED_TONE
        else:
            setting = FeederSetting.DISPENSE_TONE
        await self.coordinator.client.update_feeder_settings(self.feeder_data, setting, 0)

        if self.feeder_data.type == 'd4s':
            self.feeder_data.data['settings']['feedTone'] = 0
        else:
            self.feeder_data.data['settings']['feedSound'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class VoiceDispense(CoordinatorEntity, SwitchEntity):
    """Representation of D3 Feeder Voice with dispense."""

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

        return str(self.feeder_data.id) + '_voice_dispense'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "voice_with_dispense"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:account-voice'
        else:
            return 'mdi:account-voice-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if voice with dispense is on."""

        return self.feeder_data.data['settings']['soundEnable'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn voice with dispense on."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SOUND_ENABLE, 1)

        self.feeder_data.data['settings']['soundEnable'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn voice with dispense off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SOUND_ENABLE, 0)

        self.feeder_data.data['settings']['soundEnable'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class DoNotDisturb(CoordinatorEntity, SwitchEntity):
    """Representation of D3 Feeder DND."""

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

        return str(self.feeder_data.id) + '_do_not_disturb'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "do_not_disturb"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:sleep'
        else:
            return 'mdi:sleep-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if DND is on."""

        return self.feeder_data.data['settings']['disturbMode'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn DND on."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.DO_NOT_DISTURB, 1)

        self.feeder_data.data['settings']['disturbMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn DND off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.DO_NOT_DISTURB, 0)

        self.feeder_data.data['settings']['disturbMode'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class SurplusControl(CoordinatorEntity, SwitchEntity):
    """Representation of D3 Feeder Surplus Control."""

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

        return str(self.feeder_data.id) + '_surplus_control'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "surplus_control"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:food-drumstick'
        else:
            return 'mdi:food-drumstick-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if surplus control is on."""

        return self.feeder_data.data['settings']['surplusControl'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn surplus control on."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SURPLUS_CONTROL, 1)

        self.feeder_data.data['settings']['surplusControl'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn surplus control off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SURPLUS_CONTROL, 0)

        self.feeder_data.data['settings']['surplusControl'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class SystemNotification(CoordinatorEntity, SwitchEntity):
    """Representation of D3 Feeder System Notification sound."""

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

        return str(self.feeder_data.id) + '_system_notification'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "system_notification_sound"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:bell-ring'
        else:
            return 'mdi:bell-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if system notification is on."""

        return self.feeder_data.data['settings']['systemSoundEnable'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn system notification on."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SYSTEM_SOUND, 1)

        self.feeder_data.data['settings']['systemSoundEnable'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn system notification off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SYSTEM_SOUND, 0)

        self.feeder_data.data['settings']['systemSoundEnable'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBAutoOdor(CoordinatorEntity, SwitchEntity):
    """Representation of litter box auto odor removal."""

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

        return str(self.lb_data.id) + '_auto_odor'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "auto_odor_removal"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:scent'
        else:
            return 'mdi:scent-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if auto odor removal is on."""

        return self.lb_data.device_detail['settings']['autoRefresh'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            # Make Sure Pura MAX has Pura Air associated with it
            if self.lb_data.type == 't4':
                if 'k3Device' in self.lb_data.device_detail:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn auto odor removal on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AUTO_ODOR, 1)

        self.lb_data.device_detail['settings']['autoRefresh'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn auto odor removal off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AUTO_ODOR, 0)

        self.lb_data.device_detail['settings']['autoRefresh'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBAutoClean(CoordinatorEntity, SwitchEntity):
    """Representation of litter box auto cleaning switch."""

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

        return str(self.lb_data.id) + '_auto_clean'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "auto_cleaning"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:vacuum'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if auto cleaning is on."""

        return self.lb_data.device_detail['settings']['autoWork'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if (self.lb_data.device_detail['state']['pim'] != 0) and (self.lb_data.device_detail['settings']['kitten'] != 1):
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn auto cleaning on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AUTO_CLEAN, 1)

        self.lb_data.device_detail['settings']['autoWork'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn auto cleaning off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AUTO_CLEAN, 0)

        self.lb_data.device_detail['settings']['autoWork'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBAvoidRepeat(CoordinatorEntity, SwitchEntity):
    """Representation of litter box avoid repeat cleaning switch."""

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

        return str(self.lb_data.id) + '_avoid_repeat'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "avoid_repeat_cleaning"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:repeat'
        else:
            return 'mdi:repeat-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if avoid repeat is on."""

        return self.lb_data.device_detail['settings']['avoidRepeat'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if (self.lb_data.device_detail['state']['pim'] != 0) and (self.lb_data.device_detail['settings']['kitten'] != 1):
            # Only available if automatic cleaning is turned on
            if self.lb_data.device_detail['settings']['autoWork'] != 0:
                return True
            else:
                return False
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn avoid repeat cleaning on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AVOID_REPEAT_CLEAN, 1)

        self.lb_data.device_detail['settings']['avoidRepeat'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn avoid repeat cleaning off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AVOID_REPEAT_CLEAN, 0)

        self.lb_data.device_detail['settings']['avoidRepeat'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBDoNotDisturb(CoordinatorEntity, SwitchEntity):
    """Representation of litter box dnd switch."""

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

        return str(self.lb_data.id) + '_dnd'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "do_not_disturb"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:sleep'
        else:
            return 'mdi:sleep-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if dnd is on."""

        return self.lb_data.device_detail['settings']['disturbMode'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn dnd on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DO_NOT_DISTURB, 1)

        self.lb_data.device_detail['settings']['disturbMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn dnd off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DO_NOT_DISTURB, 0)

        self.lb_data.device_detail['settings']['disturbMode'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBPeriodicCleaning(CoordinatorEntity, SwitchEntity):
    """Representation of litter box periodic cleaning switch."""

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

        return str(self.lb_data.id) + '_periodic_cleaning'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "periodic_cleaning"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:timer'
        else:
            return 'mdi:timer-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if periodic cleaning is on."""

        return self.lb_data.device_detail['settings']['fixedTimeClear'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if (self.lb_data.device_detail['state']['pim'] != 0) and (self.lb_data.device_detail['settings']['kitten'] != 1):
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn periodic cleaning on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.PERIODIC_CLEAN, 1)

        self.lb_data.device_detail['settings']['fixedTimeClear'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn periodic cleaning off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.PERIODIC_CLEAN, 0)

        self.lb_data.device_detail['settings']['fixedTimeClear'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBPeriodicOdor(CoordinatorEntity, SwitchEntity):
    """Representation of litter box periodic odor removal."""

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

        return str(self.lb_data.id) + '_periodic_odor'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "periodic_odor_removal"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:scent'
        else:
            return 'mdi:scent-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if periodic odor removal is on."""

        return self.lb_data.device_detail['settings']['fixedTimeRefresh'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            # Make sure Pura MAX has associated Pura Air
            if self.lb_data.type == 't4':
                if 'k3Device' in self.lb_data.device_detail:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn periodic odor removal on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.PERIODIC_ODOR, 1)

        self.lb_data.device_detail['settings']['fixedTimeRefresh'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn periodic odor removal off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.PERIODIC_ODOR, 0)

        self.lb_data.device_detail['settings']['fixedTimeRefresh'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBKittenMode(CoordinatorEntity, SwitchEntity):
    """Representation of litter box kitten mode."""

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

        return str(self.lb_data.id) + '_kitten_mode'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "kitten_mode"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:cat'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if kitten mode is on."""

        return self.lb_data.device_detail['settings']['kitten'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn kitten mode on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.KITTEN_MODE, 1)

        self.lb_data.device_detail['settings']['kitten'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn kitten mode off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.KITTEN_MODE, 0)

        self.lb_data.device_detail['settings']['kitten'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBDisplay(CoordinatorEntity, SwitchEntity):
    """Representation of litter box display power."""

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

        return str(self.lb_data.id) + '_display'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "display"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:monitor'
        else:
            return 'mdi:monitor-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if display is on."""

        return self.lb_data.device_detail['settings']['lightMode'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn display on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DISPLAY, 1)

        self.lb_data.device_detail['settings']['lightMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn display off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DISPLAY, 0)

        self.lb_data.device_detail['settings']['lightMode'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBChildLock(CoordinatorEntity, SwitchEntity):
    """Representation of litter box child lock."""

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

        return str(self.lb_data.id) + '_child_lock'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "child_lock"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:lock'
        else:
            return 'mdi:lock-off'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if child lock is on."""

        return self.lb_data.device_detail['settings']['manualLock'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn child lock on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.CHILD_LOCK, 1)

        self.lb_data.device_detail['settings']['manualLock'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn child lock off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.CHILD_LOCK, 0)

        self.lb_data.device_detail['settings']['manualLock'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBLightWeight(CoordinatorEntity, SwitchEntity):
    """Representation of litter box light weight cleaning disabler."""

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

        return str(self.lb_data.id) + '_light_weight'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "light_weight_cleaning_disabled"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:feather'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if light weight disabler is on."""

        return self.lb_data.device_detail['settings']['underweight'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        kitten_mode_off = self.lb_data.device_detail['settings']['kitten'] == 0
        auto_clean = self.lb_data.device_detail['settings']['autoWork'] == 1
        avoid_repeat = self.lb_data.device_detail['settings']['avoidRepeat'] == 1

        if self.lb_data.device_detail['state']['pim'] != 0:
            # Kitten mode must be off and auto cleaning and avoid repeat must be on
            if kitten_mode_off and auto_clean and avoid_repeat:
                return True
            else:
                return False
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn light weight disabler on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DISABLE_LIGHT_WEIGHT, 1)

        self.lb_data.device_detail['settings']['underweight'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn light weight disabler off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DISABLE_LIGHT_WEIGHT, 0)

        self.lb_data.device_detail['settings']['underweight'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBPower(CoordinatorEntity, SwitchEntity):
    """Representation of litter box power switch."""

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

        return str(self.lb_data.id) + '_power'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "power"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:power'
        else:
            return 'mdi:power-off'

    @property
    def is_on(self) -> bool:
        """Determine if litter box is powered on."""

        return self.lb_data.device_detail['state']['power'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn power on."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.POWER)

        self.lb_data.device_detail['state']['power'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn power off."""

        await self.coordinator.client.control_litter_box(self.lb_data, LitterBoxCommand.POWER)

        self.lb_data.device_detail['state']['power'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBContRotation(CoordinatorEntity, SwitchEntity):
    """Representation of litter box continuous rotation setting."""

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

        return str(self.lb_data.id) + '_cont_rotation'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "cont_rotation"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:rotate-3d-variant'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if continuous rotation is on."""

        return self.lb_data.device_detail['settings']['downpos'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn continuous rotation on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.CONT_ROTATION, 1)

        self.lb_data.device_detail['settings']['downpos'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn continuous rotation off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.CONT_ROTATION, 0)

        self.lb_data.device_detail['settings']['downpos'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBDeepCleaning(CoordinatorEntity, SwitchEntity):
    """Representation of litter box deep cleaning setting."""

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

        return str(self.lb_data.id) + '_deep_cleaning'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "deep_cleaning"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:vacuum'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if deep cleaning is on."""

        return self.lb_data.device_detail['settings']['deepClean'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn deep cleaning on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DEEP_CLEAN, 1)

        self.lb_data.device_detail['settings']['deepClean'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn deep cleaning off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DEEP_CLEAN, 0)

        self.lb_data.device_detail['settings']['deepClean'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class LBDeepDeodor(CoordinatorEntity, SwitchEntity):
    """Representation of litter box deep deodorization setting."""

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

        return str(self.lb_data.id) + '_deep_deodor'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "deep_deodor"

    @property
    def icon(self) -> str:
        """Set icon."""

        return 'mdi:spray-bottle'

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to config."""

        return EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Determine if deep deodorization is on."""

        return self.lb_data.device_detail['settings']['deepRefresh'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.lb_data.device_detail['state']['pim'] != 0:
            # Make sure Pura Air is still associated with litter box
            if 'k3Device' in self.lb_data.device_detail:
                return True
            else:
                return False
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn deep deodorization on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DEEP_REFRESH, 1)

        self.lb_data.device_detail['settings']['deepRefresh'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn deep deodorization off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DEEP_REFRESH, 0)

        self.lb_data.device_detail['settings']['deepRefresh'] = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class PurifierLight(CoordinatorEntity, SwitchEntity):
    """Representation of Purifier indicator light switch."""

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

        return str(self.purifier_data.id) + '_indicator_light'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "indicator_light"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:lightbulb'
        else:
            return 'mdi:lightbulb-off'

    @property
    def is_on(self) -> bool:
        """Determine if indicator light is on."""

        return self.purifier_data.device_detail['settings']['lightMode'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.purifier_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn indicator light on."""

        await self.coordinator.client.update_purifier_settings(self.purifier_data, PurifierSetting.LIGHT, 1)

        self.purifier_data.device_detail['settings']['lightMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn indicator light off."""

        await self.coordinator.client.update_purifier_settings(self.purifier_data, PurifierSetting.LIGHT, 0)

        self.purifier_data.device_detail['settings']['lightMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class PurifierTone(CoordinatorEntity, SwitchEntity):
    """Representation of purifier tone switch."""

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

        return str(self.purifier_data.id) + '_tone'

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""

        return True

    @property
    def translation_key(self) -> str:
        """Translation key for this entity."""

        return "prompt_tone"

    @property
    def icon(self) -> str:
        """Set icon."""

        if self.is_on:
            return 'mdi:ear-hearing'
        else:
            return 'mdi:ear-hearing-off'

    @property
    def is_on(self) -> bool:
        """Determine if prompt tone is on."""

        return self.purifier_data.device_detail['settings']['sound'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.purifier_data.device_detail['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn prompt tone on."""

        await self.coordinator.client.update_purifier_settings(self.purifier_data, PurifierSetting.SOUND, 1)

        self.purifier_data.device_detail['settings']['sound'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn prompt tone off."""

        await self.coordinator.client.update_purifier_settings(self.purifier_data, PurifierSetting.SOUND, 0)

        self.purifier_data.device_detail['settings']['sound'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
