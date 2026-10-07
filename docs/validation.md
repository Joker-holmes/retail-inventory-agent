# Validation

The validation strategy has three distinct stages.

## 1. Structural calibration

Historical sales are used to calculate SKU-level statistics.

## 2. Decision simulation

The agent generates decisions from decision-time information:

- inventory
- frozen forecast inputs, if available
- historical features

## 3. Post-hoc evaluation

Realized demand can be merged after decisions have been generated.

This separation prevents future actual demand from leaking into the ordering policy.

## Unit tests

The first release tests:

- regime-to-quantile mapping
- demand-proxy bounds
- non-negative/capped order quantities
- ROP/OUT consistency
- absence of `actual_demand` and `target` from the decision API
