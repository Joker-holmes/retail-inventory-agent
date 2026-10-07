"""Run the inventory agent on demo or user-provided CSV files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.inventory_agent import AgentConfig, InventoryAgent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sales", default="dataset/sales_demo.csv")
    parser.add_argument("--inventory", default="dataset/inventory_demo.csv")
    parser.add_argument("--output", default="outputs/order_recommendations.csv")
    args = parser.parse_args()

    sales_path = Path(args.sales)
    inventory_path = Path(args.inventory)
    output_path = Path(args.output)

    if not sales_path.exists():
        raise FileNotFoundError(
            f"Sales file not found: {sales_path}. "
            "Run: python scripts/generate_demo_data.py"
        )
    if not inventory_path.exists():
        raise FileNotFoundError(f"Inventory file not found: {inventory_path}")

    agent = InventoryAgent.from_csv(
        sales_path,
        config=AgentConfig(
            lead_time_days=1.0,
            order_up_to_horizon_days=2.0,
        ),
    )

    inventory = pd.read_csv(inventory_path)
    result = agent.recommend_batch(inventory)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    print("=" * 78)
    print("RETAIL INVENTORY DECISION AGENT")
    print("=" * 78)
    print(f"Sales rows:        {len(sales_path.read_text(encoding='utf-8').splitlines()) - 1:,}")
    print(f"Products:          {result['product_id'].nunique()}")
    print(f"Decision rows:     {len(result)}")
    print(f"Mean order:        {result['recommended_order'].mean():.2f}")
    print(f"Median order:      {result['recommended_order'].median():.2f}")
    print(f"Zero-order rate:   {(result['recommended_order'].eq(0)).mean():.2%}")
    print(f"Trigger rate:      {result['reorder_trigger'].mean():.2%}")
    print(f"Stockout proxy:    {result['stockout_proxy'].mean():.2%}")
    print(f"Output:            {output_path.resolve()}")
    print("=" * 78)


if __name__ == "__main__":
    main()
