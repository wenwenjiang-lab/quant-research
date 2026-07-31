# Study 03 — Economic-Relevance Protocol

> **Status: preregistered design; analysis not started.** No result, performance
> estimate, Alpha claim, or deployable strategy is reported here.

## Purpose

Study 02 found a small, time-sensitive MNQ-to-QQQ forecasting relationship.
Study 03 asks a different question: can a frozen version of that signal retain
positive economic value after an implementable delay and conservative trading
costs? Statistical predictability is not treated as evidence of tradability.

This is a prospective study. It must use a newly protected evaluation sample.
The completed Study 02 holdout is permanently closed and cannot be reused for
threshold selection, cost calibration, model choice, or confirmation.

## Sample-eligibility gate

The parent study's final observation is dated **2026-07-29**. Study 03 counts
only distinct sessions strictly after that date. The currently audited common
dataset contains zero such sessions, so empirical development remains locked.
This is a sample-availability statement, not a market or performance result.

Before development begins, at least **343 new sessions** are required. This is
the smallest total sample that leaves 274 development sessions (252 initial
training sessions, a one-session embargo, and one 21-session test block) after
reserving the newest 20%, or 69 sessions, as the final holdout. The date-only
gate in `src/economic_relevance.py` enforces this boundary without reading
prices, forecasts, returns, or outcomes. The calculation and chronological
split construction are implemented in `src/economic_validation.py`.

## Primary estimand

The primary estimand is net return after prespecified commissions, spread, and
slippage, relative to a no-trade benchmark. The comparison is evaluated on
chronological out-of-sample predictions from the frozen parent model.

The primary claim requires all of the following:

1. aggregate net return is positive;
2. its lower confidence bound is above zero;
3. more than half of eligible sessions have positive net contribution; and
4. the conclusion survives at least 1 basis point of one-way slippage.

Failure of any condition is a complete, publishable negative result.

## Information and execution timing

- A one-minute forecast becomes available only after its source interval closes.
- Execution in the same interval is forbidden.
- The earliest modeled fill is the following bar's VWAP.
- Positions are intraday only and must be flat before 15:55 New York time.
- Missing observations are not forward-filled to create executable signals.
- Quote-based spread estimates are preferred when licensed quote data are
  available; otherwise the prespecified stress grid is reported transparently.

The next-bar VWAP convention is a research approximation, not a guarantee of
fill quality. Partial fills, queue position, market impact, borrow availability,
and exchange-specific order handling remain limitations.

## Costs and constraints

The base commission assumption is $0.005 per share with a $1.00 minimum per
order. One-way slippage is evaluated at 0.5, 1.0, and 2.0 basis points. Gross
and net outcomes, turnover, maximum drawdown, hit rate, net Sharpe ratio, and
the break-even cost are all reported.

The portfolio is unlevered, has gross exposure capped at one, and permits at
most 30 position changes per session. A no-trade threshold is part of the
position rule and must be fitted exclusively within each development window.

## Validation design

The analysis uses expanding training windows, 21-session test blocks, and a
one-session embargo. Random splits and ordinary K-fold validation are
forbidden. The newest 20% of a future eligible sample is reserved once as the
final holdout. All transformations, thresholds, and nuisance estimates must be
fit without access to that holdout.

Before execution, the exact calendar boundary, data coverage report, code
commit, and authorization phrase must be frozen. The holdout may be evaluated
only once; retuning and repeat evaluation are prohibited.

## Interpretation boundary

Passing this protocol would establish limited cost-aware evidence under the
documented simulation assumptions—not production readiness, capacity, or
guaranteed Alpha. Failing it would show that the statistical relationship does
not survive the registered economic test. Either outcome must be reported.

The machine-readable specification is in
[`configs/economic_relevance.toml`](../configs/economic_relevance.toml).
