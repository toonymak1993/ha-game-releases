"""Async Steam Store client."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import STEAM_SEARCH_URL
from .models import GameRelease, parse_steam_results


class SteamStoreError(Exception):
    """Steam Store could not be reached or returned invalid data."""


class SteamStoreClient:
    """Fetch upcoming PC releases without an account or API key."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_get_upcoming_games(
        self,
        days_ahead: int,
        max_games: int,
    ) -> tuple[GameRelease, ...]:
        """Fetch upcoming Steam releases and return them chronologically."""
        today = date.today()
        end = today + timedelta(days=days_ahead)
        params: dict[str, Any] = {
            "query": "",
            "start": 0,
            "count": min(100, max(50, max_games * 5)),
            "dynamic_data": "",
            "sort_by": "_ASC",
            "supportedlang": "english",
            "infinite": 1,
            "filter": "popularcomingsoon",
            "category1": 998,
            "cc": "us",
            "l": "english",
        }
        try:
            async with self._session.get(
                STEAM_SEARCH_URL,
                params=params,
                headers={"User-Agent": "Home Assistant Game Releases/0.2"},
                timeout=20,
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise SteamStoreError(str(err)) from err

        if not payload.get("success"):
            raise SteamStoreError("Steam Store returned an unsuccessful response")
        return parse_steam_results(
            str(payload.get("results_html") or ""), max_games, today, end
        )
