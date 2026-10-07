# Regime-Aware Retail Inventory Decision Agent

A leakage-controlled, SKU-level retail inventory decision system that converts probabilistic demand forecasts and current inventory into daily replenishment recommendations.

## Core pipeline

```text
Historical Sales
      |
      v
Product-level Demand Profile
      |
      +---- P50 / P90 / P95
      |
      +---- CV / spike ratio / trend
      |
      v
Regime-aware Forecast Selection
      |
      v
Demand Proxy
      |
      v
Safety Stock
      |
      v
Reorder Point (ROP)
      |
      v
Order-up-to Level (OUT)
      |
      v
Recommended Order
```

## Key features

- Probabilistic forecast inputs: P50 / P90 / P95
- Regime-aware forecast selection:
  - Normal -> P50
  - Elevated -> P90
  - Spike -> P90
  - Extreme Spike -> P95
- Product-level rolling demand, volatility, quantile and trend features
- Uncertainty-aware safety stock
- Reorder-point and order-up-to inventory policy
- Sequential inventory simulation with inventory consumption
- Daily replenishment support
- Strict separation between decision inputs and final evaluation actuals
- Real-data CSV inference interface
- Deterministic demo data generation
- Unit tests for selector, policy, and leakage boundary

## Important data-policy note

The repository intentionally does **not** contain private operational data.

The agent can accept frozen P50/P90/P95/regime values from an upstream forecasting system. If those fields are absent, it uses a transparent historical fallback based on the sales history. The fallback is **not claimed to be the original hidden V8.20 forecasting engine**.

Test-period actual demand must not be passed into `InventoryAgent.recommend()`.

## Quick start

Python 3.10+ is recommended.

```bash
pip install -r requirements.txt
python scripts/generate_demo_data.py
python scripts/run_demo.py
pytest -q
```

Demo outputs are written to `outputs/`.

## Real-data usage

Prepare:

```text
dataset/sales.csv
dataset/current_inventory.csv
```

Historical sales should contain at least:

```text
date,product_id,demand
```

`current_inventory.csv` should contain:

```text
date,product_id,inventory
```

Optional forecast fields:

```text
forecast_p50
forecast_p90
forecast_p95
regime
```

Example:

```csv
date,product_id,inventory,forecast_p50,forecast_p90,forecast_p95,regime
2026-10-07,P001,55,42,68,82,Elevated
2026-10-07,P002,40,30,48,60,Normal
```

Run:

```bash
python scripts/run_demo.py --sales dataset/sales.csv --inventory dataset/current_inventory.csv
```

## Methodology

### Forecast selector

Let `(P50, P90, P95)` be the available forecast quantiles.

```text
Normal        -> P50
Elevated      -> P90
Spike         -> P90
Extreme Spike -> P95
```

### Demand proxy

```text
D = 0.60 * selected_forecast
  + 0.40 * recent_7_day_mean * trend_ratio
```

The result is clipped to:

```text
0.70 * selected_forecast <= D <= 1.15 * selected_forecast
```

### Safety stock

For product coefficient of variation `CV` and spike ratio `S`:

```text
base_ss =
    selected_forecast * CV * 0.50
  + selected_forecast * max(S - 1, 0) * 0.15
```

Regime multipliers are applied to the base safety stock.

### Inventory policy

With one-day lead-time proxy and two-day order-up-to horizon:

```text
ROP = D * lead_time + SafetyStock

OUT = D * order_up_to_horizon + SafetyStock

Order = ceil(min(OUT - Inventory, MaxOrder))
```

where:

```text
MaxOrder = max(
    1.5 * selected_forecast,
    1.5 * recent_7_day_mean
)
```

No negative order is produced.

## Leakage control

The decision engine receives:

```text
historical sales
current inventory
optional frozen forecasts
optional regime
```

It does **not** receive:

```text
test actual demand
test target
future realized sales
```

A separate evaluation layer may compare recommendations with actual demand after the decisions have been generated. This preserves the distinction between **decision-time information** and **post-hoc evaluation information**.

## Project structure

```text
retail-inventory-agent/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── demand_features.py
│   ├── forecast_selector.py
│   ├── inventory_policy.py
│   ├── inventory_agent.py
│   └── evaluation.py
├── scripts/
│   ├── generate_demo_data.py
│   └── run_demo.py
├── tests/
│   ├── test_forecast_selector.py
│   ├── test_inventory_policy.py
│   └── test_leakage.py
├── configs/
│   └── default.json
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   └── validation.md
├── examples/
│   └── example_output.csv
└── archive/
    └── README.md
```

## Resume value

This project is best described as a:

> Probabilistic forecasting + regime-aware decision + sequential inventory control system

rather than simply a "convenience-store AI project."

Recommended technical keywords:

- probabilistic forecasting
- quantile forecasting
- regime-aware decision making
- time-series feature engineering
- inventory optimization
- safety stock
- reorder point
- order-up-to policy
- sequential simulation
- temporal leakage control
- reproducible ML/algorithm engineering

## License

MIT
