"""Switch platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import FeederSetting, LitterBoxCommand, LitterBoxSetting, W5Command
from petkitaio.exceptions import BluetoothError
from petkitaio.model import Feeder, LitterBox, W5Fountain

from homeassistant.components.switch import SwitchEntity
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
    """Set Up PetKit Switch Entities."""

    coordinator: PetKitDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

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

        # D4 Feeder
        if feeder_data.type == 'd4':
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
        # Pura X
        switches.extend((
            LBAutoOdor(coordinator, lb_id),
            LBAutoClean(coordinator, lb_id),
            LBAvoidRepeat(coordinator, lb_id),
            LBDoNotDisturb(coordinator, lb_id),
            LBPeriodicCleaning(coordinator, lb_id),
            LBPeriodicOdor(coordinator, lb_id),
            LBKittenMode(coordinator, lb_id),
            LBDisplay(coordinator, lb_id),
            LBChildLock(coordinator, lb_id),
            LBLightWeight(coordinator, lb_id),
            LBPower(coordinator, lb_id),
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
            "model": WATER_FOUNTAINS[self.wf_data.type],
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_light'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Light"

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
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.LIGHTON)
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
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.LIGHTOFF)
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
            "model": WATER_FOUNTAINS[self.wf_data.type],
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_power'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Power"

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
            "model": WATER_FOUNTAINS[self.wf_data.type],
            "sw_version": f'{self.wf_data.data["hardware"]}.{self.wf_data.data["firmware"]}'
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""

        return str(self.wf_data.id) + '_disturb'

    @property
    def name(self) -> str:
        """Return name of the entity."""

        return "Do not disturb"

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
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.DONOTDISTURB)
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
            await self.coordinator.client.control_water_fountain(self.wf_data, W5Command.DONOTDISTURBOFF)
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
    def name(self) -> str:
        """Return name of the entity."""

        return "Indicator light"

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
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MINIINDICATORLIGHT, 1)
        else:
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.INDICATORLIGHT, 1)

        self.feeder_data.data['settings']['lightMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn indicator light off."""

        if self.feeder_data.type == 'feedermini':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MINIINDICATORLIGHT, 0)
        else:
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.INDICATORLIGHT, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Child lock"

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
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MINICHILDLOCK, 1)
        else:
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.CHILDLOCK, 1)

        self.feeder_data.data['settings']['manualLock'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn child lock off."""

        if self.feeder_data.type == 'feedermini':
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.MINICHILDLOCK, 0)
        else:
            await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.CHILDLOCK, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Food shortage alarm"

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

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SHORTAGEALARM, 1)
        self.feeder_data.data['settings']['foodWarn'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn food shortage alarm off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SHORTAGEALARM, 0)
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
    def name(self) -> str:
        """Return name of the entity."""

        return "Dispense tone"

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
        """Determine if food shortage alarm is on."""

        return self.feeder_data.data['settings']['feedSound'] == 1

    @property
    def available(self) -> bool:
        """Only make available if device is online."""

        if self.feeder_data.data['state']['pim'] != 0:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn food shortage alarm on."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.DISPENSETONE, 1)
        self.feeder_data.data['settings']['feedSound'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn food shortage alarm off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.DISPENSETONE, 0)
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
    def name(self) -> str:
        """Return name of the entity."""

        return "Voice with dispense"

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

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SOUNDENABLE, 1)

        self.feeder_data.data['settings']['soundEnable'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn voice with dispense off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SOUNDENABLE, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Do not disturb"

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

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.DONOTDISTURB, 1)

        self.feeder_data.data['settings']['disturbMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn DND off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.DONOTDISTURB, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Surplus control"

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

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SURPLUSCONTROL, 1)

        self.feeder_data.data['settings']['surplusControl'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn surplus control off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SURPLUSCONTROL, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "System notification sound"

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

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SYSTEMSOUND, 1)

        self.feeder_data.data['settings']['systemSoundEnable'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn system notification off."""

        await self.coordinator.client.update_feeder_settings(self.feeder_data, FeederSetting.SYSTEMSOUND, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Auto odor removal"

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
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn auto odor removal on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AUTOODOR, 1)

        self.lb_data.device_detail['settings']['autoRefresh'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn auto odor removal off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AUTOODOR, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Auto cleaning"

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

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AUTOCLEAN, 1)

        self.lb_data.device_detail['settings']['autoWork'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn auto cleaning off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AUTOCLEAN, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Avoid repeat cleaning"

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

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AVOIDREPEATCLEAN, 1)

        self.lb_data.device_detail['settings']['avoidRepeat'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn avoid repeat cleaning off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.AVOIDREPEATCLEAN, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Do not disturb"

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

        if (self.lb_data.device_detail['state']['pim'] != 0):
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn dnd on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DONOTDISTURB, 1)

        self.lb_data.device_detail['settings']['disturbMode'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn dnd off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DONOTDISTURB, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Periodic cleaning"

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

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.PERIODICCLEAN, 1)

        self.lb_data.device_detail['settings']['fixedTimeClear'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn periodic cleaning off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.PERIODICCLEAN, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Periodic odor removal"

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

        if (self.lb_data.device_detail['state']['pim'] != 0):
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn periodic odor removal on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.PERIODICODOR, 1)

        self.lb_data.device_detail['settings']['fixedTimeRefresh'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn periodic odor removal off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.PERIODICODOR, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Kitten mode"

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

        if (self.lb_data.device_detail['state']['pim'] != 0):
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn kitten mode on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.KITTENMODE, 1)

        self.lb_data.device_detail['settings']['kitten'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn kitten mode off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.KITTENMODE, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Display"

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

        if (self.lb_data.device_detail['state']['pim'] != 0):
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
    def name(self) -> str:
        """Return name of the entity."""

        return "Child lock"

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

        if (self.lb_data.device_detail['state']['pim'] != 0):
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn child lock on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.CHILDLOCK, 1)

        self.lb_data.device_detail['settings']['manualLock'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn child lock off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.CHILDLOCK, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Light weight cleaning disabled"

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

        if (self.lb_data.device_detail['state']['pim'] != 0):
            # Kitten mode must be off and auto cleaning and avoid repeat must be on
            if (kitten_mode_off and auto_clean and avoid_repeat):
                return True
            else:
                return False
        else:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn light weight disabler on."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DISABLELIGHTWEIGHT, 1)

        self.lb_data.device_detail['settings']['underweight'] = 1
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn light weight disabler off."""

        await self.coordinator.client.update_litter_box_settings(self.lb_data, LitterBoxSetting.DISABLELIGHTWEIGHT, 0)

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
    def name(self) -> str:
        """Return name of the entity."""

        return "Power"

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

        if (self.lb_data.device_detail['state']['pim'] != 0):
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
