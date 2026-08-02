# Study 04 Post-Hoc Stability Diagnosis

> **Status: descriptive analysis after a failed registered holdout.** This
> analysis does not refit or select a model, change the registered decision,
> validate Alpha, or support a profitability claim.

## Purpose

The registered Study 04 test found that ten-level MNQ order-book features
improved Development log loss but did not reproduce the prespecified magnitude
in the one-time July holdout. This diagnostic asks two narrower questions:

1. did the measured inputs or outcome mix change between the samples; and
2. was the holdout conclusion driven by one unusually influential session?

Because these questions were examined after opening the holdout, every result
below is exploratory. They can motivate a new preregistered study, but they
cannot rescue the closed test.

![Post-hoc Study 04 stability diagnosis](../figures/market_microstructure_stability.svg)

## Samples and method

The comparison uses aggregate summaries derived from the same licensed local
panels as the registered evaluation:

| Sample | Sessions | Eligible one-second decisions |
|---|---:|---:|
| Development, 2026-05-01 to 2026-06-30 | 43 | 77,214 |
| Final holdout, 2026-07-01 to 2026-07-27 | 19 | 34,143 |

For each frozen input, two development-anchored diagnostics are reported:

- standardized mean difference (SMD), measured in Development standard
  deviations; and
- population stability index (PSI), using bin edges estimated from Development
  quantiles only.

PSI is used as a descriptive distribution-shift measure, not as a hypothesis
test. Session influence is measured by recomputing the mean holdout log-loss
difference after omitting each of the 19 sessions once. No model is refit and
no feature, threshold, or observation is selected from these diagnostics.

## Findings

The three-class outcome mix was nearly unchanged. Down / unchanged / up shares
were 48.15% / 3.17% / 48.68% in Development and 48.44% / 2.94% / 48.62% in the
holdout. A large change in the target base rate is therefore not visible.

The clearest measured shift was in displayed depth:

| Feature | Development mean | Holdout mean | SMD | PSI |
|---|---:|---:|---:|---:|
| Ask depth, levels 1–5 | 34.66 | 32.49 | -0.145 | 0.336 |
| Ask depth, levels 1–10 | 84.51 | 80.14 | -0.126 | 0.323 |
| Bid depth, levels 1–5 | 34.16 | 32.44 | -0.120 | 0.310 |
| Bid depth, levels 1–10 | 82.82 | 79.82 | -0.093 | 0.304 |

Other frozen inputs had PSI below 0.04. Holdout message activity was higher
(253.71 versus 233.00 events per 100 milliseconds; SMD 0.134), while average
one-second recent volatility was also slightly higher (3.81 versus 3.63; SMD
0.091). These are associations with sample timing, not evidence that any one
shift caused the attenuation.

The registered mean session log-loss difference was -0.000222. Across all 19
leave-one-session-out calculations it ranged only from -0.000292 to -0.000168
and never changed sign. Omitting the least favorable session (2026-07-17) still
left the result far short of the registered -0.001 replication threshold.
Therefore, the non-replication was not created by one isolated date.

## Interpretation

The most defensible description is that the Development effect attenuated in a
future sample whose displayed-depth distribution differed, while the direction
of the average effect remained slightly favorable. The diagnostics do not
identify a causal mechanism and do not justify excluding dates, changing
features, or retuning the model.

This strengthens the research record in a narrow way: it rules out a simple
single-session explanation and documents observable sample drift. The original
decision remains **failed replication**. A genuine follow-up would require a
new frozen hypothesis, a new untouched sample, and a separate decision rule.

The machine-readable aggregate evidence is in
[`market_microstructure_stability_diagnostics.json`](market_microstructure_stability_diagnostics.json).
Licensed observations and vendor metadata remain local and excluded from Git.
