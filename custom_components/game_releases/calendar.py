"""Calendar platform for Game Releases."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import STEAM_ATTRIBUTION
from .coordinator import GameReleasesCoordinator
from .entity import GameReleasesEntity
from .models import GameRelease


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the releases calendar."""
    async_add_entities([GameReleasesCalendar(entry.runtime_data)])


def _to_event(release: GameRelease) -> CalendarEvent:
    platforms = ", ".join(release.platforms) or "Unknown platform"
    return CalendarEvent(
        start=release.released,
        end=release.released + timedelta(days=1),
        summary=release.name,
        description=(
            f"Platforms: {platforms}\n{release.url}\n\n{STEAM_ATTRIBUTION}"
        ),
        location=platforms,
        uid=f"steam-{release.id}-{release.released.isoformat()}",
    )


class GameReleasesCalendar(GameReleasesEntity, CalendarEntity):
    """Native calendar containing upcoming game releases."""

    _attr_name = "Release calendar"
    _attr_icon = "mdi:calendar-star"

    def __init__(self, coordinator: GameReleasesCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming release."""
        today = date.today()
        release = next(
            (item for item in self.coordinator.data if item.released >= today), None
        )
        return _to_event(release) if release else None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return releases within a requested range."""
        return [
            _to_event(release)
            for release in self.coordinator.data
            if start_date.date() <= release.released < end_date.date()
        ]
