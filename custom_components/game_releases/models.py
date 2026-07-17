"""Pure data models and Steam search-result parser."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True, slots=True)
class GameRelease:
    """A normalized upcoming game release."""

    id: int
    name: str
    released: date
    image: str | None
    platforms: tuple[str, ...]
    slug: str
    url: str
    rating: float | None
    metacritic: int | None
    popularity: int

    def as_dict(self) -> dict[str, Any]:
        """Return a Home Assistant state-attribute-safe representation."""
        data = asdict(self)
        data["released"] = self.released.isoformat()
        data["platforms"] = list(self.platforms)
        return data


class _SteamSearchParser(HTMLParser):
    """Extract release data from Steam's compact search-result markup."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[dict[str, Any]] = []
        self._current: dict[str, Any] | None = None
        self._capture: str | None = None
        self._capture_tag: str | None = None

    def handle_starttag(
        self, tag: str, attrs_list: list[tuple[str, str | None]]
    ) -> None:
        attrs = dict(attrs_list)
        classes = set((attrs.get("class") or "").split())

        if tag == "a" and "search_result_row" in classes:
            app_id = attrs.get("data-ds-appid")
            if app_id and app_id.isdigit():
                href = attrs.get("href") or ""
                parts = urlsplit(href)
                self._current = {
                    "id": int(app_id),
                    "url": urlunsplit((parts.scheme, parts.netloc, parts.path, "", "")),
                    "name": "",
                    "released": "",
                    "image": None,
                    "platforms": set(),
                }
            return

        if self._current is None:
            return
        if tag == "img" and not self._current["image"]:
            self._current["image"] = attrs.get("src")
        elif tag == "span" and "title" in classes:
            self._capture, self._capture_tag = "name", tag
        elif tag == "div" and "search_released" in classes:
            self._capture, self._capture_tag = "released", tag
        elif tag == "span" and "platform_img" in classes:
            platform_map = {"win": "PC", "mac": "macOS", "linux": "Linux"}
            for css_class, name in platform_map.items():
                if css_class in classes:
                    self._current["platforms"].add(name)

    def handle_data(self, data: str) -> None:
        if self._current is not None and self._capture:
            self._current[self._capture] += data

    def handle_endtag(self, tag: str) -> None:
        if self._capture_tag == tag:
            self._capture = self._capture_tag = None
        if tag == "a" and self._current is not None:
            self.items.append(self._current)
            self._current = None
            self._capture = self._capture_tag = None


def _parse_steam_date(value: str) -> date | None:
    """Parse the English date format returned by the Steam storefront."""
    normalized = " ".join(value.split()).replace("Sept ", "Sep ")
    for pattern in ("%b %d, %Y", "%d %b, %Y"):
        try:
            return datetime.strptime(normalized, pattern).date()
        except ValueError:
            continue
    return None


def parse_steam_results(
    html: str,
    max_games: int,
    start_date: date,
    end_date: date,
) -> tuple[GameRelease, ...]:
    """Normalize, filter, sort, and limit Steam search results."""
    parser = _SteamSearchParser()
    parser.feed(html)
    releases: list[GameRelease] = []

    for position, item in enumerate(parser.items):
        release_date = _parse_steam_date(item["released"])
        if release_date is None or not start_date <= release_date <= end_date:
            continue
        app_id = item["id"]
        releases.append(
            GameRelease(
                id=app_id,
                name=" ".join(item["name"].split()) or f"Steam app {app_id}",
                released=release_date,
                image=item["image"],
                platforms=tuple(sorted(item["platforms"] or {"PC"})),
                slug=str(app_id),
                url=item["url"] or f"https://store.steampowered.com/app/{app_id}/",
                rating=None,
                metacritic=None,
                popularity=max(0, len(parser.items) - position),
            )
        )

    releases = releases[:max_games]
    releases.sort(key=lambda game: (game.released, -game.popularity, game.name.casefold()))
    return tuple(releases)
