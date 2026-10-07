"""Post-hoc evaluation utilities.

This module is intentionally separate from the decision engine.
Actual demand can be used here only after recommendations have been generated.
"""

from __future__ import annotations

import pandas as pd


def evaluate_realized_demand(
    recommendations: pd.DataFrame,
    actuals: pd.DataFrame,
    actual_column: str = "actual_demand",
) -> dict:
    required_rec = {"product_id", "recommended_order"}
    required_actual = {"product_id", "date", actual_column}

    missing_rec = required_rec - set(recommendations.columns)
    missing_actual = required_actual - set(actuals.columns)

    if missing_rec:
        raise ValueError(f"recommendations missing: {sorted(missing_rec)}")
    if missing_actual:
        raise ValueError(f"actuals missing: {sorted(missing_actual)}")

    rec = recommendations.copy()
    act = actuals.copy()
    rec["date"] = pd.to_datetime(rec["decision_date"])
    act["date"] = pd.to_datetime(act["date"])

    merged = rec.merge(
        act[["date", "product_id", actual_column]],
        on=["date", "product_id"],
        how="left",
        validate="one_to_one",
    )

    merged["order_minus_actual"] = (
        merged["recommended_order"] - merged[actual_column]
    )
    merged["absolute_error"] = merged["order_minus_actual"].abs()

    return {
        "rows_evaluated": int(len(merged)),
        "actual_match_rate": float(merged[actual_column].notna().mean()),
        "mean_order": float(merged["recommended_order"].mean()),
        "mean_actual": float(merged[actual_column].mean()),
        "mean_order_minus_actual": float(merged["order_minus_actual"].mean()),
        "mae_order_vs_actual": float(merged["absolute_error"].mean()),
    }
