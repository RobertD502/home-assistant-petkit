"""Config Flow for PetKit integration."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from petkitaio.exceptions import AuthError, PetKitError, ServerError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import ASIA_ACCOUNT, DEFAULT_NAME, DOMAIN, POLLING_INTERVAL
from .util import NoDevicesError, async_validate_api


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(ASIA_ACCOUNT): cv.boolean,
    }
)


class PetKitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PetKit integration."""

    VERSION = 2

    entry: config_entries.ConfigEntry | None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> PetKitOptionsFlowHandler:
        """Get the options flow for this handler."""
        return PetKitOptionsFlowHandler(config_entry)

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
            asia_account = user_input[ASIA_ACCOUNT] if ASIA_ACCOUNT in user_input else False
            try:
                await async_validate_api(self.hass, email, password, asia_account)
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
                        ASIA_ACCOUNT: asia_account,
                        POLLING_INTERVAL: self.entry.options[POLLING_INTERVAL],
                    }
                )

                await self.hass.config_entries.async_reload(self.entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=DATA_SCHEMA,
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
            asia_account = user_input[ASIA_ACCOUNT] if ASIA_ACCOUNT in user_input else False
            try:
                await async_validate_api(self.hass, email, password, asia_account)
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
                        ASIA_ACCOUNT: asia_account,
                        POLLING_INTERVAL: 120,
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )


class PetKitOptionsFlowHandler(config_entries.OptionsFlow):
    """ Handle PetKit integration options. """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """ Manage options. """
        return await self.async_step_petkit_options()

    async def async_step_petkit_options(self, user_input=None):
        """Manage the PetKit options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Required(
                ASIA_ACCOUNT,
                default=self.config_entry.options.get(
                    ASIA_ACCOUNT, False
                ),
            ): bool,
            vol.Required(
                POLLING_INTERVAL,
                default=self.config_entry.options.get(
                    POLLING_INTERVAL, 120
                ),
            ): int,
        }

        return self.async_show_form(step_id="petkit_options", data_schema=vol.Schema(options))
