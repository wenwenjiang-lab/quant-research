# Quantitative Research Portfolio Roadmap

> **Status: In progress.** Planned items describe intended work, not completed skills, findings, or trading results.

## Positioning

The portfolio is designed to demonstrate transferable research ability across quantitative research, quantitative trading, and markets analytics. MNQ is the first empirical setting, not the limit of the research program.

## Capability milestones

### 1. Research design — in progress

- State a falsifiable question and economic rationale.
- Define hypotheses, variables, sampling rules, and exclusions before confirmatory testing.
- Separate exploratory choices from registered tests.

**Completion evidence:** reviewed research design and a frozen analysis specification.

### 2. Reliable market-data pipeline — in progress

- Validate schema, timestamps, prices, duplicates, missing bars, and session boundaries.
- Document data provenance, licensing, exchange calendar, and futures roll treatment.
- Produce deterministic processed data without committing restricted raw data.

**Completion evidence:** validation report and unit-tested transformation pipeline.

### 3. Statistical inference — in progress

- Report distributions, effect sizes, uncertainty, and sample sizes.
- Test prespecified hypotheses with assumption-aware parametric or nonparametric methods.
- Control multiplicity when comparing intervals, thresholds, or outcomes.

**Completion evidence:** reproducible tables with confidence intervals, corrected p-values, and diagnostics.

### 4. Time-series validation — in progress

- Use chronological train/validation/test periods.
- Add expanding-window analysis and regime sensitivity checks.
- Prevent feature, label, normalization, and selection leakage.

**Completion evidence:** walk-forward evaluation with untouched final holdout data.

### 5. Economic evaluation — planned

- Translate statistical relationships into prespecified, testable decision rules.
- Model spread, commissions, slippage, latency, and contract liquidity.
- Report turnover, drawdown, tail risk, capacity limitations, and benchmark comparisons.

**Completion evidence:** cost-aware evaluation; statistical significance alone is insufficient.

### 6. Cross-market robustness — planned

- Compare MNQ with NQ and QQQ while accounting for different contract structures.
- Test external validity in ES and SPY.
- Identify shared effects, instrument-specific effects, and failure cases.

**Completion evidence:** harmonized study design and cross-instrument robustness report.

### 7. Modeling extensions — planned

- Establish transparent statistical baselines first.
- Evaluate regularized linear models before more complex machine learning.
- Compare out-of-sample incremental value, stability, interpretability, and costs.

**Completion evidence:** model card and walk-forward comparison against simple baselines.

## Job-relevant evidence

| Target role | Evidence this portfolio will emphasize |
|---|---|
| Quantitative Research | Independent hypotheses, statistical modeling, time-series validation, reproducibility |
| Quantitative Trading | Market mechanics, probability, risk, execution costs, rapid but disciplined analysis |
| Markets / Data Analyst | Data quality, Python/SQL-ready workflows, clear reporting, stakeholder communication |

Low-latency engineering is not presented as a current specialty. C++, networking, operating systems, and hardware optimization would require a separate engineering portfolio.
