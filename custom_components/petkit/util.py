"""Utilities for PetKit Integration"""
from __future__ import annotations

from typing import Any
import async_timeout

from petkitaio import PetKitClient
from petkitaio.exceptions import AuthError, PetKitError, ServerError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import LOGGER, PETKIT_ERRORS, TIMEOUT


async def async_validate_api(hass: HomeAssistant, email: str, password: str, asia_account: bool) -> bool:
    """Get data from API."""

    client = PetKitClient(
        email,
        password,
        session=async_get_clientsession(hass),
        asia_account=asia_account,
        timeout=TIMEOUT,
    )

    try:
        async with async_timeout.timeout(TIMEOUT):
            devices_query = await client.get_device_roster()
    except AuthError as err:
        LOGGER.error(f'Could not authenticate on PetKit servers: {err}')
        raise AuthError(err)
    except ServerError as err:
        LOGGER.error(f'PetKit servers are busy.Please try again later.')
        raise ServerError(err)
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
