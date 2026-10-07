from src.forecast_selector import select_forecast


def test_normal_uses_p50():
    value, source = select_forecast(10, 20, 30, "Normal")
    assert value == 10
    assert source == "P50"


def test_elevated_uses_p90():
    value, source = select_forecast(10, 20, 30, "Elevated")
    assert value == 20
    assert source == "P90"


def test_spike_uses_p90():
    value, source = select_forecast(10, 20, 30, "Spike")
    assert value == 20
    assert source == "P90"


def test_extreme_spike_uses_p95():
    value, source = select_forecast(10, 20, 30, "Extreme Spike")
    assert value == 30
    assert source == "P95"
