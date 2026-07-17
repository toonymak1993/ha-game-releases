"""Game Releases integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CARD_URL, PLATFORMS
from .coordinator import GameReleasesCoordinator


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the bundled Lovelace card."""
    card_path = Path(__file__).parent / "frontend" / "game-releases-card.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(card_path), cache_headers=True)]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Game Releases from a config entry."""
    coordinator = GameReleasesCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Game Releases config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
