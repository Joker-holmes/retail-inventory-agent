"""Historical demand feature engineering.

Only historical sales available at decision time should be used here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {"date", "product_id", "demand"}


def validate_sales_frame(sales: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(sales.columns)
    if missing:
        raise ValueError(f"sales is missing required columns: {sorted(missing)}")


def _safe_cv(series: pd.Series) -> float:
    mean = float(series.mean())
    std = float(series.std(ddof=1)) if len(series) > 1 else 0.0
    return std / mean if mean > 1e-12 else 0.0


def build_product_profiles(sales: pd.DataFrame) -> pd.DataFrame:
    """Build one structural profile per SKU from historical sales only."""
    validate_sales_frame(sales)

    df = sales.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["product_id"] = df["product_id"].astype(str)
    df["demand"] = pd.to_numeric(df["demand"], errors="coerce")
    df = df.dropna(subset=["date", "product_id", "demand"])
    df = df.sort_values(["product_id", "date"])

    rows = []
    for product_id, g in df.groupby("product_id", sort=True):
        x = g["demand"].astype(float)
        recent_3 = float(x.tail(3).mean())
        recent_7 = float(x.tail(7).mean())
        recent_14 = float(x.tail(14).mean())

        q50 = float(x.quantile(0.50))
        q90 = float(x.quantile(0.90))
        q95 = float(x.quantile(0.95))
        mean = float(x.mean())
        std = float(x.std(ddof=1)) if len(x) > 1 else 0.0
        cv = std / mean if mean > 1e-12 else 0.0
        max_demand = float(x.max())

        spike_ratio = max_demand / mean if mean > 1e-12 else 1.0
        trend_ratio = recent_7 / recent_28 if (recent_28 := float(x.tail(28).mean())) > 1e-12 else 1.0

        recent_cv = _safe_cv(x.tail(14))

        rows.append(
            {
                "product_id": product_id,
                "history_rows": int(len(g)),
                "history_mean": mean,
                "history_std": std,
                "cv": cv,
                "q50": q50,
                "q90": q90,
                "q95": q95,
                "max_demand": max_demand,
                "spike_ratio": spike_ratio,
                "recent_3": recent_3,
                "recent_7": recent_7,
                "recent_14": recent_14,
                "recent_cv": recent_cv,
                "trend_ratio": float(np.clip(trend_ratio, 0.70, 1.30)),
            }
        )

    return pd.DataFrame(rows)
