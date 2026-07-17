"""Tests for the pure Steam search-result parser."""

from datetime import date
import importlib.util
from pathlib import Path
import sys
import unittest


MODEL_PATH = Path(__file__).parents[1] / "custom_components" / "game_releases" / "models.py"
SPEC = importlib.util.spec_from_file_location("game_releases_models", MODEL_PATH)
assert SPEC and SPEC.loader
MODELS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODELS
SPEC.loader.exec_module(MODELS)


HTML = """
<a href="https://store.steampowered.com/app/20/later/?snr=test"
   data-ds-appid="20" class="search_result_row">
  <img src="https://example.com/later.jpg">
  <span class="title">Later Game</span>
  <span class="platform_img win"></span><span class="platform_img linux"></span>
  <div class="search_released">Aug 02, 2026</div>
</a>
<a href="https://store.steampowered.com/app/10/sooner/?snr=test"
   data-ds-appid="10" class="search_result_row">
  <img src="https://example.com/sooner.jpg">
  <span class="title">Sooner Game</span>
  <span class="platform_img win"></span>
  <div class="search_released">Aug 01, 2026</div>
</a>
<a href="https://store.steampowered.com/app/30/unknown/"
   data-ds-appid="30" class="search_result_row">
  <span class="title">Unknown Date</span>
  <div class="search_released">Coming soon</div>
</a>
"""


class ParseSteamResultsTest(unittest.TestCase):
    """Verify extraction, filtering, normalization, and ordering."""

    def test_parse_sorts_and_normalizes(self) -> None:
        games = MODELS.parse_steam_results(
            HTML, 10, date(2026, 7, 17), date(2026, 9, 1)
        )

        self.assertEqual([game.name for game in games], ["Sooner Game", "Later Game"])
        self.assertEqual(games[0].released, date(2026, 8, 1))
        self.assertEqual(games[1].platforms, ("Linux", "PC"))
        self.assertEqual(games[0].url, "https://store.steampowered.com/app/10/sooner/")

    def test_parse_applies_date_range_and_limit(self) -> None:
        games = MODELS.parse_steam_results(
            HTML, 1, date(2026, 8, 2), date(2026, 8, 2)
        )

        self.assertEqual(len(games), 1)
        self.assertEqual(games[0].name, "Later Game")


if __name__ == "__main__":
    unittest.main()
