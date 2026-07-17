"""Config flow for Game Releases."""

from __future__ import annotations

from typing import Any, override

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_DAYS_AHEAD,
    CONF_MAX_GAMES,
    DEFAULT_DAYS_AHEAD,
    DEFAULT_MAX_GAMES,
    DOMAIN,
)


def _filter_schema(suggested: dict[str, Any] | None = None) -> vol.Schema:
    """Build the release-filter form."""
    suggested = suggested or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_DAYS_AHEAD,
                default=suggested.get(CONF_DAYS_AHEAD, DEFAULT_DAYS_AHEAD),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=7, max=365, step=1, mode=NumberSelectorMode.BOX
                )
            ),
            vol.Required(
                CONF_MAX_GAMES,
                default=suggested.get(CONF_MAX_GAMES, DEFAULT_MAX_GAMES),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=4, max=40, step=1, mode=NumberSelectorMode.BOX
                )
            ),
        }
    )


class GameReleasesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Game Releases."""

    VERSION = 1

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry: ConfigEntry) -> GameReleasesOptionsFlow:
        """Return the options flow."""
        return GameReleasesOptionsFlow()

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up the keyless Steam release feed."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            await self.async_set_unique_id("steam")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Game Releases",
                data={},
                options={
                    CONF_DAYS_AHEAD: int(user_input[CONF_DAYS_AHEAD]),
                    CONF_MAX_GAMES: int(user_input[CONF_MAX_GAMES]),
                },
            )
        return self.async_show_form(step_id="user", data_schema=_filter_schema())


class GameReleasesOptionsFlow(OptionsFlowWithReload):
    """Handle Game Releases options."""

    @override
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update release filters."""
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_DAYS_AHEAD: int(user_input[CONF_DAYS_AHEAD]),
                    CONF_MAX_GAMES: int(user_input[CONF_MAX_GAMES]),
                }
            )
        return self.async_show_form(
            step_id="init",
            data_schema=_filter_schema(dict(self.config_entry.options)),
        )
