"""Shared entity helpers for Game Releases."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STEAM_URL
from .coordinator import GameReleasesCoordinator


class GameReleasesEntity(CoordinatorEntity[GameReleasesCoordinator]):
    """Base entity for the Game Releases integration."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GameReleasesCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name="Game Releases",
            manufacturer="Steam",
            model="Release calendar",
            configuration_url=STEAM_URL,
        )
