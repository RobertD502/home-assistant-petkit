"""Config Flow for PetKit integration."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from petkitaio.exceptions import (
    AuthError,
    PetKitError,
    RegionError,
    ServerError,
    TimezoneError,
)
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    BooleanSelector,
    BooleanSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
)

from .const import (
    DEFAULT_NAME,
    DOMAIN,
    POLLING_INTERVAL,
    REGION,
    REGIONS_LIST,
    TIMEZONE,
    USE_BLE_RELAY,
)
from .timezones import TIMEZONES
from .util import NoDevicesError, async_validate_api


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(REGION): SelectSelector(
            SelectSelectorConfig(options=REGIONS_LIST),
        ),
        vol.Required(TIMEZONE): SelectSelector(
            SelectSelectorConfig(options=TIMEZONES),
        ),
        vol.Required(USE_BLE_RELAY, default=True): BooleanSelector(
            BooleanSelectorConfig(),
        ),
    }
)

def reauth_schema(
    def_email: str | vol.UNDEFINED = vol.UNDEFINED,
    def_password: str | vol.UNDEFINED = vol.UNDEFINED,
    def_region: str | vol.UNDEFINED = vol.UNDEFINED,
    def_timezone: str | vol.UNDEFINED = vol.UNDEFINED,
    def_use_ble_relay: bool | vol.UNDEFINED = True
) -> dict[vol.Marker, Any]:
    """Return schema for reauth flow with optional default value."""

    return {
                vol.Required(CONF_EMAIL, default=def_email): cv.string,
                vol.Required(CONF_PASSWORD, default=def_password): cv.string,
                vol.Required(REGION, default=def_region): SelectSelector(
                    SelectSelectorConfig(options=REGIONS_LIST),
                ),
                vol.Required(TIMEZONE, default=def_timezone): SelectSelector(
                    SelectSelectorConfig(options=TIMEZONES),
                ),
                vol.Required(USE_BLE_RELAY, default=def_use_ble_relay): BooleanSelector(
                    BooleanSelectorConfig()
                ),
    }


class PetKitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PetKit integration."""

    VERSION = 6

    entry: config_entries.ConfigEntry | None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> PetKitOptionsFlowHandler:
        """Get the options flow for this handler."""
        return PetKitOptionsFlowHandler()

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Handle re-authentication with PetKit."""

        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm re-authentication with PetKit."""

        errors: dict[str, str] = {}
        if user_input:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]
            region = user_input[REGION] if REGION else None
            timezone = user_input[TIMEZONE]
            use_ble_relay = user_input[USE_BLE_RELAY] if USE_BLE_RELAY in user_input else True

            try:
                await async_validate_api(
                    self.hass,
                    email,
                    password,
                    region,
                    timezone,
                    use_ble_relay
                )
            except RegionError:
                errors["base"] = "region_error"
            except TimezoneError:
                errors["base"] = "timezone_error"
            except AuthError:
                errors["base"] = "invalid_auth"
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except NoDevicesError:
                errors["base"] = "no_devices"
            except ServerError:
                errors["base"] = "server_busy"
            except PetKitError:
                errors["base"] = "petkit_error"
            else:
                assert self.entry is not None

                self.hass.config_entries.async_update_entry(
                    self.entry,
                    data={
                        **self.entry.data,
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                    },
                    options={
                        REGION: region,
                        TIMEZONE: timezone,
                        POLLING_INTERVAL: self.entry.options[POLLING_INTERVAL],
                        USE_BLE_RELAY: use_ble_relay
                    }
                )

                await self.hass.config_entries.async_reload(self.entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                reauth_schema(
                    self.entry.data[CONF_EMAIL],
                    self.entry.data[CONF_PASSWORD],
                    self.entry.options[REGION],
                    self.entry.options[TIMEZONE],
                    self.entry.options[USE_BLE_RELAY]
                )
            ),
            errors=errors,
        )

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]
            region = user_input[REGION] if REGION else None
            timezone = user_input[TIMEZONE]
            use_ble_relay = user_input[USE_BLE_RELAY] if USE_BLE_RELAY in user_input else True

            try:
                await async_validate_api(
                    self.hass,
                    email,
                    password,
                    region,
                    timezone,
                    use_ble_relay
                )
            except RegionError:
                errors["base"] = "region_error"
            except TimezoneError:
                errors["base"] = "timezone_error"
            except AuthError:
                errors["base"] = "invalid_auth"
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except NoDevicesError:
                errors["base"] = "no_devices"
            except ServerError:
                errors["base"] = "server_busy"
            except PetKitError:
                errors["base"] = "petkit_error"
            else:
                await self.async_set_unique_id(email)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password
                    },
                    options={
                        REGION: region,
                        TIMEZONE: timezone,
                        POLLING_INTERVAL: 120,
                        USE_BLE_RELAY: use_ble_relay,
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )


class PetKitOptionsFlowHandler(config_entries.OptionsFlow):
    """ Handle PetKit integration options. """

    async def async_step_init(self, user_input=None):
        """ Manage options. """
        return await self.async_step_petkit_options()

    async def async_step_petkit_options(self, user_input=None):
        """Manage the PetKit options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Required(
                REGION,
                default=self.config_entry.options.get(
                    REGION, None
                ),
            ): SelectSelector(
                   SelectSelectorConfig(options=REGIONS_LIST)
            ),
            vol.Required(
                TIMEZONE,
                default=self.config_entry.options.get(
                    TIMEZONE, "Set Automatically"
                ),
            ): SelectSelector(
                   SelectSelectorConfig(options=TIMEZONES)
            ),
            vol.Required(
                POLLING_INTERVAL,
                default=self.config_entry.options.get(
                    POLLING_INTERVAL, 120
                ),
            ): int,
            vol.Required(
                USE_BLE_RELAY,
                default=self.config_entry.options.get(
                    USE_BLE_RELAY, True
                ),
            ): BooleanSelector(
                   BooleanSelectorConfig()
            ),
        }

        return self.async_show_form(step_id="petkit_options", data_schema=vol.Schema(options))
