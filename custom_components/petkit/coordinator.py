"""DataUpdateCoordinator for the PetKit integration."""
from __future__ import annotations

from datetime import timedelta

from petkitaio import PetKitClient
from petkitaio.exceptions import AuthError, PetKitError, ServerError
from petkitaio.model import PetKitData


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import ASIA_ACCOUNT, DOMAIN, LOGGER, POLLING_INTERVAL, TIMEOUT


class PetKitDataUpdateCoordinator(DataUpdateCoordinator):
    """PetKit Data Update Coordinator."""

    data: PetKitData

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the PetKit coordinator."""

        self.client = PetKitClient(
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
            asia_account=entry.options[ASIA_ACCOUNT],
            timeout=TIMEOUT,
        )
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options[POLLING_INTERVAL]),
        )

    async def _async_update_data(self) -> PetKitData:
        """Fetch data from PetKit."""

        try:
            data = await self.client.get_petkit_data()
            LOGGER.debug(f'Found the following PetKit devices/pets: {data}')
        except AuthError as error:
            raise ConfigEntryAuthFailed(error) from error
        except (ServerError, PetKitError) as error:
            raise UpdateFailed(error) from error
        return data
