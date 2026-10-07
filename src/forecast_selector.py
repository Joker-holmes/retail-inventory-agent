"""Regime-aware probabilistic forecast selection."""

from __future__ import annotations

import math


VALID_REGIMES = {"Normal", "Elevated", "Spike", "Extreme Spike"}


def normalize_regime(regime: str | None) -> str:
    if regime is None:
        return "Normal"

    value = str(regime).strip().title()
    aliases = {
        "Extreme": "Extreme Spike",
        "Extreme_spike": "Extreme Spike",
        "Extreme-Spike": "Extreme Spike",
        "High": "Elevated",
    }
    value = aliases.get(value, value)

    return value if value in VALID_REGIMES else "Normal"


def select_forecast(
    forecast_p50: float,
    forecast_p90: float,
    forecast_p95: float,
    regime: str,
) -> tuple[float, str]:
    """Select a forecast quantile according to the demand regime."""
    p50 = max(float(forecast_p50), 0.0)
    p90 = max(float(forecast_p90), p50)
    p95 = max(float(forecast_p95), p90)

    r = normalize_regime(regime)

    if r == "Normal":
        return p50, "P50"
    if r in {"Elevated", "Spike"}:
        return p90, "P90"
    if r == "Extreme Spike":
        return p95, "P95"

    return p50, "P50"


def infer_fallback_forecasts(profile: dict) -> tuple[float, float, float]:
    """Transparent historical fallback; not the hidden/original V8.20 engine."""
    p50 = max(float(profile["q50"]), float(profile["recent_7"]))
    p90 = max(float(profile["q90"]), p50)
    p95 = max(float(profile["q95"]), p90)

    # Keep finite and non-negative.
    values = [p50, p90, p95]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Non-finite fallback forecast encountered.")

    return p50, p90, p95


def infer_fallback_regime(profile: dict, p50: float, p90: float) -> str:
    """Simple transparent regime fallback based on upper-quantile inflation."""
    mean = max(float(profile["history_mean"]), 1e-9)
    q90_ratio = p90 / mean

    if q90_ratio >= 2.20:
        return "Extreme Spike"
    if q90_ratio >= 1.80:
        return "Spike"
    if q90_ratio >= 1.40:
        return "Elevated"
    return "Normal"
