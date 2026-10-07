"""Generate a deterministic synthetic dataset for GitHub demos."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate(output_dir: Path, products: int = 20, days: int = 180) -> None:
    rng = np.random.default_rng(20261007)
    output_dir.mkdir(parents=True, exist_ok=True)

    dates = pd.date_range("2026-01-01", periods=days, freq="D")

    sales_rows = []
    inventory_rows = []

    for i in range(1, products + 1):
        pid = f"P{i:03d}"
        base = 12 + 1.2 * i
        weekly_amp = 0.12 + 0.01 * (i % 4)

        for day_index, date in enumerate(dates):
            dow = date.dayofweek
            seasonal = 1.0 + weekly_amp * (1 if dow in (4, 5) else -0.25)
            trend = 1.0 + 0.0008 * day_index
            noise = rng.normal(0, max(1.0, base * 0.16))

            spike = 1.0
            if rng.random() < 0.025:
                spike = rng.uniform(1.7, 2.8)

            demand = max(0.0, base * seasonal * trend * spike + noise)

            sales_rows.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "product_id": pid,
                    "demand": round(float(demand), 3),
                }
            )

        # Current inventory is a decision-time input, not historical demand.
        current_inventory = max(0, int(rng.normal(base * 1.4, base * 0.35)))
        inventory_rows.append(
            {
                "date": "2026-10-07",
                "product_id": pid,
                "inventory": current_inventory,
            }
        )

    sales = pd.DataFrame(sales_rows)
    inventory = pd.DataFrame(inventory_rows)

    sales.to_csv(output_dir / "sales_demo.csv", index=False)
    inventory.to_csv(output_dir / "inventory_demo.csv", index=False)

    print(f"Wrote {len(sales):,} sales rows")
    print(f"Wrote {len(inventory):,} inventory rows")
    print(f"Output directory: {output_dir.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dataset")
    args = parser.parse_args()
    generate(Path(args.output))
