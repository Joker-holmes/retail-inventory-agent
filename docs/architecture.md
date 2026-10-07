# Architecture

## Decision-time architecture

```text
Historical sales --------------------+
                                      |
                                      v
                              Product Profile
                                      |
                                      v
Current Inventory ----------------> Agent
                                      ^
                                      |
Frozen P50/P90/P95 + Regime ----------+
                                      |
                                      v
                              Forecast Selector
                                      |
                                      v
                               Demand Proxy
                                      |
                                      v
                                Safety Stock
                                      |
                                      v
                              Reorder Point
                                      |
                                      v
                              Order-up-to Level
                                      |
                                      v
                             Recommended Order
```

The key design principle is that the decision function only consumes information that is available when the decision is made.

## Separation of concerns

- `demand_features.py`: historical structural features
- `forecast_selector.py`: probabilistic forecast and regime selection
- `inventory_policy.py`: inventory-control equations
- `inventory_agent.py`: orchestration and public API
- `evaluation.py`: post-hoc evaluation using realized demand
