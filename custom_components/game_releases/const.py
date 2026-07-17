"""Constants for the Game Releases integration."""

from datetime import timedelta
from typing import Final

DOMAIN: Final = "game_releases"
PLATFORMS: Final = ["sensor", "calendar"]

CONF_DAYS_AHEAD: Final = "days_ahead"
CONF_MAX_GAMES: Final = "max_games"

DEFAULT_DAYS_AHEAD: Final = 120
DEFAULT_MAX_GAMES: Final = 12
DEFAULT_UPDATE_INTERVAL: Final = timedelta(hours=6)
STEAM_SEARCH_URL: Final = "https://store.steampowered.com/search/results/"
STEAM_ATTRIBUTION: Final = "Release data provided by Steam"
STEAM_URL: Final = "https://store.steampowered.com"

CARD_URL: Final = "/game_releases/game-releases-card.js"
INTEGRATION_VERSION: Final = "0.2.0"
