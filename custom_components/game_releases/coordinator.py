"""Data update coordinator for Game Releases."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import SteamStoreClient, SteamStoreError
from .const import (
    CONF_DAYS_AHEAD,
    CONF_MAX_GAMES,
    DEFAULT_DAYS_AHEAD,
    DEFAULT_MAX_GAMES,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .models import GameRelease

_LOGGER = logging.getLogger(__name__)


class GameReleasesCoordinator(DataUpdateCoordinator[tuple[GameRelease, ...]]):
    """Coordinate Steam release data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.client = SteamStoreClient(async_get_clientsession(hass))
        self.entry = entry

    async def _async_update_data(self) -> tuple[GameRelease, ...]:
        """Fetch the latest upcoming releases."""
        options = self.entry.options
        try:
            return await self.client.async_get_upcoming_games(
                int(options.get(CONF_DAYS_AHEAD, DEFAULT_DAYS_AHEAD)),
                int(options.get(CONF_MAX_GAMES, DEFAULT_MAX_GAMES)),
            )
        except SteamStoreError as err:
            raise UpdateFailed(f"Error communicating with Steam Store: {err}") from err
