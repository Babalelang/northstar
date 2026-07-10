import unittest
from types import SimpleNamespace

from services.analytics_service import compute_player_metrics


class AnalyticsServiceTests(unittest.TestCase):
    def test_compute_player_metrics_returns_reasonable_values(self):
        player = SimpleNamespace(
            playing_position="st",
            goals=14,
            assists=4,
            minutes_played=1800,
            form_rating=84,
        )

        metrics = compute_player_metrics(player)

        self.assertGreater(metrics["overall_rating"], 70)
        self.assertGreater(metrics["market_value_eur"], 1_000_000)
        self.assertGreaterEqual(metrics["potential_rating"], metrics["overall_rating"])


if __name__ == "__main__":
    unittest.main()
