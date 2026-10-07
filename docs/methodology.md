# Methodology

The first public release implements the policy logic developed during the V8-V13 experimentation cycle.

## Forecast

The agent supports externally supplied probabilistic forecasts:

- P50: median forecast
- P90: high-demand forecast
- P95: extreme-tail forecast

If external forecasts are absent, historical quantiles are used as a clearly labelled fallback.

## Regime-aware selection

```text
Normal        -> P50
Elevated      -> P90
Spike         -> P90
Extreme Spike -> P95
```

## Demand proxy

```text
D = 0.60 * selected_forecast
  + 0.40 * recent_7 * trend_ratio
```

The result is clipped to 70%-115% of the selected forecast.

## Safety stock

```text
SS =
    selected_forecast * CV * 0.50
  + selected_forecast * max(spike_ratio - 1, 0) * 0.15
```

A regime multiplier is then applied.

## Replenishment

```text
ROP = D * lead_time + SS
OUT = D * order_up_to_horizon + SS
Order = ceil(min(max(OUT - Inventory, 0), MaxOrder))
```

This is a transparent policy model, not a claim that the repository contains any proprietary retailer policy.
