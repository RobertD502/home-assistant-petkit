"""Utilities for PetKit Integration"""
from __future__ import annotations

from typing import Any
import async_timeout

from petkitaio import PetKitClient
from petkitaio.exceptions import AuthError, PetKitError, RegionError, ServerError, TimezoneError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import LOGGER, PETKIT_ERRORS, TIMEOUT


async def async_validate_api(hass: HomeAssistant, email: str, password: str, region: str, timezone: str) -> bool:
    """Get data from API."""

    if timezone == "Set Automatically":
        tz = None
    else:
        tz = timezone
    client = PetKitClient(
        email,
        password,
        session=async_get_clientsession(hass),
        region=region,
        timezone=tz,
        timeout=TIMEOUT,
    )
    try:
        async with async_timeout.timeout(TIMEOUT):
            devices_query = await client.get_device_roster()
    except AuthError as err:
        LOGGER.error(f'Could not authenticate on PetKit servers: {err}')
        raise AuthError(err)
    except TimezoneError:
        error = 'A timezone could not be found. If you are running Home Assistant as a standalone Docker container, you must define the TZ environmental variable. If the TZ variable is defined or you are running Home Assistant OS, your timezone was not found in the tzlocal library - Please manually select a timezone during setup.'
        LOGGER.error(f'{error}')
        raise TimezoneError(error)
    except ServerError as err:
        LOGGER.error(f'PetKit servers are busy.Please try again later.')
        raise ServerError(err)
    except RegionError as err:
        LOGGER.error(f'{err}')
        raise RegionError(err)
    except PetKitError as err:
        LOGGER.error(f'Unknown PetKit Error: {err}')
        raise PetKitError(err)
    except PETKIT_ERRORS as err:
        LOGGER.error(f'Failed to get information from PetKit servers: {err}')
        raise ConnectionError from err

    devices: dict[str, Any] = devices_query['result']['devices']

    if not devices:
        LOGGER.error("Could not retrieve any devices from PetKit servers")
        raise NoDevicesError
    return True


class NoDevicesError(Exception):
    """ No Devices from PetKit API. """
