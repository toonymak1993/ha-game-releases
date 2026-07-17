"""Diagnostics support for Game Releases."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    """Return diagnostics for the release feed."""
    coordinator = entry.runtime_data
    return {
        "entry": {
            "title": entry.title,
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "release_count": len(coordinator.data or ()),
            "releases": [release.as_dict() for release in coordinator.data or ()],
        },
    }
