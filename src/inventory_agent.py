"""Public inventory decision agent.

The class deliberately separates:
1. historical structural calibration,
2. decision-time inputs,
3. optional frozen probabilistic forecasts,
4. inventory policy.

No future/test actual demand is accepted by the decision method.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .demand_features import build_product_profiles
from .forecast_selector import (
    infer_fallback_forecasts,
    infer_fallback_regime,
    normalize_regime,
    select_forecast,
)
from .inventory_policy import (
    expected_post_order_inventory,
    inventory_parameters,
    recommend_order,
)


@dataclass
class AgentConfig:
    lead_time_days: float = 1.0
    order_up_to_horizon_days: float = 2.0


class InventoryAgent:
    """SKU-level inventory recommendation engine."""

    def __init__(
        self,
        sales: pd.DataFrame,
        config: AgentConfig | None = None,
    ):
        self.config = config or AgentConfig()
        self.sales = sales.copy()
        self.profiles = build_product_profiles(self.sales)

        if self.profiles.empty:
            raise ValueError("No valid product profiles could be built.")

        self.profile_map = {
            str(row["product_id"]): row.to_dict()
            for _, row in self.profiles.iterrows()
        }

    @classmethod
    def from_csv(
        cls,
        sales_path: str | Path,
        config: AgentConfig | None = None,
    ) -> "InventoryAgent":
        sales = pd.read_csv(sales_path)
        return cls(sales, config=config)

    def _get_profile(self, product_id: str) -> dict[str, Any]:
        pid = str(product_id)
        if pid not in self.profile_map:
            raise KeyError(f"Unknown product_id: {pid}")
        return self.profile_map[pid]

    def recommend(
        self,
        product_id: str,
        inventory: float,
        forecast_p50: float | None = None,
        forecast_p90: float | None = None,
        forecast_p95: float | None = None,
        regime: str | None = None,
        decision_date: str | None = None,
    ) -> dict[str, Any]:
        """Generate a decision using only decision-time information.

        There is intentionally no `actual_demand` or `target` argument.
        """
        profile = self._get_profile(product_id)

        supplied_forecasts = (
            forecast_p50 is not None
            and forecast_p90 is not None
            and forecast_p95 is not None
        )

        if supplied_forecasts:
            p50 = float(forecast_p50)
            p90 = float(forecast_p90)
            p95 = float(forecast_p95)
            forecast_source = "frozen_external_forecast"
        else:
            p50, p90, p95 = infer_fallback_forecasts(profile)
            forecast_source = "historical_fallback"

        if regime is None:
            selected_regime = infer_fallback_regime(profile, p50, p90)
            regime_source = "historical_fallback"
        else:
            selected_regime = normalize_regime(regime)
            regime_source = "external_input"

        selected_forecast, selected_quantile = select_forecast(
            p50, p90, p95, selected_regime
        )

        params = inventory_parameters(
            selected_forecast=selected_forecast,
            recent_7=profile["recent_7"],
            trend_ratio=profile["trend_ratio"],
            cv=profile["cv"],
            spike_ratio=profile["spike_ratio"],
            regime=selected_regime,
            lead_time_days=self.config.lead_time_days,
            order_up_to_horizon_days=self.config.order_up_to_horizon_days,
        )

        decision = recommend_order(
            inventory=inventory,
            order_up_to=params["order_up_to"],
            reorder_point=params["reorder_point"],
            max_order=params["max_order"],
        )

        post = expected_post_order_inventory(
            inventory=inventory,
            recommended_order=decision["recommended_order"],
            expected_demand=params["demand_proxy"],
        )

        return {
            "decision_date": decision_date,
            "product_id": str(product_id),
            "inventory": float(inventory),
            "forecast_p50": float(p50),
            "forecast_p90": float(p90),
            "forecast_p95": float(p95),
            "forecast_source": forecast_source,
            "regime": selected_regime,
            "regime_source": regime_source,
            "selected_forecast": float(selected_forecast),
            "selected_quantile": selected_quantile,
            "recent_7": float(profile["recent_7"]),
            "trend_ratio": float(profile["trend_ratio"]),
            "cv": float(profile["cv"]),
            "spike_ratio": float(profile["spike_ratio"]),
            **params,
            **decision,
            **post,
        }

    def recommend_batch(self, current_inventory: pd.DataFrame) -> pd.DataFrame:
        """Generate recommendations for a current-inventory table."""
        required = {"date", "product_id", "inventory"}
        missing = required - set(current_inventory.columns)
        if missing:
            raise ValueError(
                f"current_inventory is missing required columns: {sorted(missing)}"
            )

        rows = []
        for _, row in current_inventory.iterrows():
            kwargs = {
                "product_id": str(row["product_id"]),
                "inventory": float(row["inventory"]),
                "decision_date": str(row["date"]),
            }

            for col in ["forecast_p50", "forecast_p90", "forecast_p95", "regime"]:
                if col in current_inventory.columns and pd.notna(row[col]):
                    kwargs[col] = row[col]

            rows.append(self.recommend(**kwargs))

        return pd.DataFrame(rows)
