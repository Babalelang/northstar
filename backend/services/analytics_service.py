from __future__ import annotations

from typing import Any

# Approximate EUR <-> ZAR rate used only for display conversion.
# Keep this in one place so admin router and frontend agree.


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default




def compute_player_metrics(player: Any) -> dict[str, float | int]:
    position = getattr(getattr(player, "playing_position", None), "value", None)
    if position is None:
        position = getattr(player, "playing_position", None)
    position_key = str(position or "cm").lower()

    position_multiplier = {
        "gk": 0.95,
        "cb": 0.88,
        "lb": 0.84,
        "rb": 0.84,
        "cdm": 0.86,
        "cm": 0.82,
        "cam": 0.9,
        "lm": 0.8,
        "rm": 0.8,
        "lw": 0.78,
        "rw": 0.78,
        "cf": 0.84,
        "st": 0.88,
    }.get(position_key, 0.8)

    goals = _coerce_int(getattr(player, "goals", None), 0)
    assists = _coerce_int(getattr(player, "assists", None), 0)
    minutes_played = _coerce_int(getattr(player, "minutes_played", None), 0)
    form_rating = _coerce_float(getattr(player, "form_rating", None), 0.0)

    if form_rating <= 0:
        form_rating = min(99.0, 58 + (goals * 1.8) + (assists * 1.2) + (minutes_played / 1800 * 10))

    overall_rating = round(
        min(99.0, max(55.0, (form_rating * 0.65) + (goals * 2.4) + (assists * 1.6) + (position_multiplier * 8.0) + (minutes_played / 1800 * 6.5))),
        1,
    )
    potential_rating = round(min(99.0, max(45.0, overall_rating + 3.5 + (position_multiplier * 3.0))), 1)

    # Base valuation computed in EUR terms, then converted to Rands for storage
    # (Rands is the model's source of truth — see Player.market_value_rands).
    market_value_rands_base = max(
        250_000,
        min(
            15_000_000,
            (overall_rating * 140_000) + (potential_rating * 90_000) + (goals * 180_000) + (assists * 120_000) + (minutes_played / 1800 * 180_000),
        ),
    )
    market_value_rands = int(market_value_rands_base)

    return {
        "overall_rating": overall_rating,
        "potential_rating": potential_rating,
        "form_rating": round(form_rating, 1),
        "market_value_rands": int(market_value_rands),
    }


def apply_player_metrics(
    player: Any,
    override_rands: int | None = None,
    override_overall: float | None = None,
    override_potential: float | None = None,
) -> dict[str, float | int]:
    metrics = compute_player_metrics(player)
    if override_rands is not None:
        metrics["market_value_rands"] = int(override_rands)
    if override_overall is not None:
        metrics["overall_rating"] = float(override_overall)
        metrics["potential_rating"] = min(99.0, max(45.0, metrics["overall_rating"] + 3.5))
    if override_potential is not None:
        metrics["potential_rating"] = float(override_potential)

    setattr(player, "overall_rating", metrics["overall_rating"])
    setattr(player, "potential_rating", metrics["potential_rating"])
    setattr(player, "form_rating", metrics["form_rating"])
    setattr(player, "market_value_rands", metrics["market_value_rands"])
    return metrics