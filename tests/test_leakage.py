import inspect

import pandas as pd

from src.inventory_agent import InventoryAgent


def test_decision_api_has_no_actual_demand_or_target_argument():
    signature = inspect.signature(InventoryAgent.recommend)
    names = set(signature.parameters)
    assert "actual_demand" not in names
    assert "target" not in names


def test_agent_runs_without_future_actuals():
    sales = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=30),
            "product_id": ["P001"] * 30,
            "demand": list(range(10, 40)),
        }
    )

    agent = InventoryAgent(sales)
    result = agent.recommend(
        product_id="P001",
        inventory=20,
        decision_date="2026-02-01",
    )

    assert result["product_id"] == "P001"
    assert result["recommended_order"] >= 0
