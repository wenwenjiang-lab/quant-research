# Quantitative Research Roadmap

> **Status: in progress.** Milestones describe intended evidence, not completed
> findings or trading performance.

## 1. Research protocol — in progress

- State a falsifiable question, estimand, and economic rationale.
- Freeze hypotheses, outcomes, sampling rules, and exclusions.
- Separate exploratory analysis from the untouched confirmatory holdout.

**Completion evidence:** versioned analysis specification and holdout boundary.

## 2. Reliable market-data pipeline — in progress

- Validate schema, timestamps, OHLCV invariants, duplicates, and bar intervals.
- Add exchange-calendar, shortened-session, and contract-roll treatment.
- Produce deterministic analytical data without redistributing licensed data.

**Completion evidence:** data-quality report with exclusion counts and tests.

## 3. Session-level research dataset — in progress

- Calculate opening-range features using only the registered opening interval.
- Calculate outcomes strictly after feature formation.
- Record ambiguous boundary breaks and incomplete sessions explicitly.

**Completion evidence:** reproducible data dictionary and session panel.

## 4. Statistical inference — planned

- Report distributions, effect sizes, uncertainty, and diagnostics.
- Use assumption-aware parametric, robust, or resampling inference.
- Control the family-wise error rate across registered hypotheses.

**Completion evidence:** reproducible tables with corrected inference.

## 5. Time-series validation — planned

- Use chronological development, expanding-window validation, and final holdout.
- Prevent leakage in features, labels, scaling, selection, and tuning.
- Evaluate stability across volatility and macro-event regimes.

**Completion evidence:** untouched holdout report with failure-period analysis.

## 6. Economic evaluation — planned

- Translate only validated associations into timestamped decision rules.
- Model spread, fees, slippage, turnover, and conservative fills.
- Report drawdown, tail risk, capacity constraints, and benchmark comparisons.

**Completion evidence:** cost-aware evaluation; significance alone is insufficient.

## 7. External validity — planned

- Compare MNQ with NQ and QQQ using harmonized definitions.
- Extend the registered design to ES and SPY.
- Distinguish shared effects from instrument-specific behavior.

**Completion evidence:** cross-instrument robustness report.

## 8. Modeling extensions — planned

- Establish transparent statistical baselines first.
- Evaluate regularized linear models before nonlinear alternatives.
- Compare machine learning by incremental out-of-sample value, stability,
  calibration, interpretability, and cost sensitivity.

**Completion evidence:** model card and walk-forward baseline comparison.
