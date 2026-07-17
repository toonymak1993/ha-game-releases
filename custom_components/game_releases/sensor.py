"""Sensor platform for Game Releases."""

from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.components.sensor import SensorEntity

from .const import STEAM_ATTRIBUTION, STEAM_URL
from .coordinator import GameReleasesCoordinator
from .entity import GameReleasesEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the upcoming releases sensor."""
    async_add_entities([GameReleasesSensor(entry.runtime_data)])


class GameReleasesSensor(GameReleasesEntity, SensorEntity):
    """Expose upcoming releases to Home Assistant and the bundled card."""

    _attr_name = "Upcoming releases"
    _attr_icon = "mdi:gamepad-variant"
    _attr_native_unit_of_measurement = "releases"

    def __init__(self, coordinator: GameReleasesCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_upcoming"

    @property
    def native_value(self) -> int:
        """Return the number of upcoming releases."""
        return len(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return normalized game data for dashboards."""
        today = date.today()
        games = []
        for release in self.coordinator.data:
            game = release.as_dict()
            game["days_until"] = (release.released - today).days
            games.append(game)
        return {
            "games": games,
            "next_release": games[0] if games else None,
            "attribution": STEAM_ATTRIBUTION,
            "source": STEAM_URL,
        }
