"""Inventory control calculations."""

from __future__ import annotations

import math


REGIME_SAFETY_MULTIPLIER = {
    "Normal": 1.00,
    "Elevated": 1.10,
    "Spike": 1.20,
    "Extreme Spike": 1.30,
}


def demand_proxy(
    selected_forecast: float,
    recent_7: float,
    trend_ratio: float,
    forecast_weight: float = 0.60,
) -> float:
    selected = max(float(selected_forecast), 0.0)
    historical_component = max(float(recent_7), 0.0) * float(trend_ratio)

    value = (
        forecast_weight * selected
        + (1.0 - forecast_weight) * historical_component
    )

    lower = 0.70 * selected
    upper = 1.15 * selected

    if selected <= 0:
        return max(historical_component, 0.0)

    return float(min(max(value, lower), upper))


def safety_stock(
    selected_forecast: float,
    cv: float,
    spike_ratio: float,
    regime: str,
) -> float:
    selected = max(float(selected_forecast), 0.0)
    cv = max(float(cv), 0.0)
    spike_adjustment = max(float(spike_ratio) - 1.0, 0.0)

    base = (
        selected * cv * 0.50
        + selected * spike_adjustment * 0.15
    )

    multiplier = REGIME_SAFETY_MULTIPLIER.get(regime, 1.0)
    return float(base * multiplier)


def inventory_parameters(
    selected_forecast: float,
    recent_7: float,
    trend_ratio: float,
    cv: float,
    spike_ratio: float,
    regime: str,
    lead_time_days: float = 1.0,
    order_up_to_horizon_days: float = 2.0,
) -> dict:
    d = demand_proxy(selected_forecast, recent_7, trend_ratio)
    ss = safety_stock(selected_forecast, cv, spike_ratio, regime)

    rop = d * float(lead_time_days) + ss
    out = d * float(order_up_to_horizon_days) + ss

    max_order = max(
        1.5 * max(float(selected_forecast), 0.0),
        1.5 * max(float(recent_7), 0.0),
    )

    return {
        "demand_proxy": float(d),
        "safety_stock": float(ss),
        "reorder_point": float(rop),
        "order_up_to": float(out),
        "max_order": float(max_order),
    }


def recommend_order(
    inventory: float,
    order_up_to: float,
    reorder_point: float,
    max_order: float,
) -> dict:
    """Calculate one decision from current opening inventory."""
    inv = max(float(inventory), 0.0)

    trigger = inv < float(reorder_point)

    if trigger:
        gap = max(float(order_up_to) - inv, 0.0)
        quantity = int(math.ceil(min(gap, max(float(max_order), 0.0))))
    else:
        quantity = 0

    return {
        "reorder_trigger": bool(trigger),
        "recommended_order": int(quantity),
    }


def expected_post_order_inventory(
    inventory: float,
    recommended_order: int,
    expected_demand: float,
) -> dict:
    post_order = max(float(inventory), 0.0) + int(recommended_order)
    closing = post_order - max(float(expected_demand), 0.0)
    expected_stockout = closing < 0.0

    expected_demand = max(float(expected_demand), 1e-9)
    coverage_days = max(closing, 0.0) / expected_demand

    return {
        "post_order_inventory": float(post_order),
        "expected_closing_inventory": float(closing),
        "stockout_proxy": bool(expected_stockout),
        "coverage_days": float(coverage_days),
    }
