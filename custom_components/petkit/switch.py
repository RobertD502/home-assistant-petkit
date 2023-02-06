"""Switch platform for PetKit integration."""
from __future__ import annotations

from typing import Any
import asyncio

from petkitaio.constants import FeederSetting, W5Command
from petkitaio.exceptions import BluetoothError
from petkitaio.model import Feeder, W5Fountain

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FEEDERS, WATER_FOUNTAINS
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
    def icon(self) -> str:
        """Set icon."""

        is_on = self.wf_data.data['settings']['lampRingSwitch'] == 1

        if is_on:
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
    def icon(self) -> str:
        """Set icon."""

        is_on = self.wf_data.data['powerStatus'] == 1

        if is_on:
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
    def icon(self) -> str:
        """Set icon."""

        is_on = self.wf_data.data['settings']['noDisturbingSwitch'] == 1

        if is_on:
            return 'mdi:sleep'
        else:
            return 'mdi:sleep-off'

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
    def icon(self) -> str:
        """Set icon."""

        is_on = self.feeder_data.data['settings']['lightMode'] == 1

        if is_on:
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
    def icon(self) -> str:
        """Set icon."""

        is_on = self.feeder_data.data['settings']['manualLock'] == 1

        if is_on:
            return 'mdi:lock'
        else:
            return 'mdi:lock-open'

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
    def icon(self) -> str:
        """Set icon."""

        is_on = self.feeder_data.data['settings']['foodWarn'] == 1

        if is_on:
            return 'mdi:alarm'
        else:
            return 'mdi:alarm-off'

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
    def icon(self) -> str:
        """Set icon."""

        is_on = self.feeder_data.data['settings']['feedSound'] == 1

        if is_on:
            return 'mdi:ear-hearing'
        else:
            return 'mdi:ear-hearing-off'

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
