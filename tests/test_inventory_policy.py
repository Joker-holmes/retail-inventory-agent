from src.inventory_policy import (
    demand_proxy,
    inventory_parameters,
    recommend_order,
)


def test_demand_proxy_is_clipped():
    value = demand_proxy(
        selected_forecast=100,
        recent_7=20,
        trend_ratio=1.0,
    )
    assert 70 <= value <= 115


def test_order_is_zero_above_reorder_point():
    decision = recommend_order(
        inventory=100,
        order_up_to=120,
        reorder_point=80,
        max_order=150,
    )
    assert decision["reorder_trigger"] is False
    assert decision["recommended_order"] == 0


def test_order_is_non_negative_and_capped():
    decision = recommend_order(
        inventory=0,
        order_up_to=200,
        reorder_point=80,
        max_order=50,
    )
    assert decision["reorder_trigger"] is True
    assert decision["recommended_order"] == 50


def test_parameters_are_consistent():
    params = inventory_parameters(
        selected_forecast=50,
        recent_7=45,
        trend_ratio=1.0,
        cv=0.25,
        spike_ratio=1.5,
        regime="Elevated",
    )
    assert params["demand_proxy"] > 0
    assert params["safety_stock"] >= 0
    assert params["order_up_to"] >= params["reorder_point"]
