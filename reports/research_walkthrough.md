# Research Walkthrough

This page explains the portfolio in plain English while preserving the exact
research conclusions. It is an interpretation guide, not a performance claim.

## What is being researched?

The portfolio asks whether information visible early in, or immediately before,
a Nasdaq trading decision helps forecast what happens next. The studies move
from slower session-level behavior to cross-asset transmission and then to the
limit order book:

1. Does the first 30 minutes of MNQ trading improve a forecast of volatility
   during the rest of the session?
2. Do lagged MNQ futures returns add predictive information for QQQ one minute
   later?
3. Can the frozen MNQ–QQQ relationship survive realistic delay and transaction
   costs on genuinely new data?
4. Do deeper levels of the MNQ order book improve one-second price-direction
   forecasts beyond top-of-book information?

The objective is not to search indefinitely for a profitable rule. Each study
defines its question, sample, model comparison, and decision threshold before
the protected evaluation data are used.

## Which data are used, and where do they come from?

The research uses licensed market data downloaded from Databento and stored
locally. Raw observations are never committed to GitHub.

- **MNQ one-minute bars:** CME Globex Micro E-mini Nasdaq-100 futures data used
  for opening-range and cross-asset research.
- **QQQ one-minute bars:** Nasdaq-listed QQQ ETF data synchronized with MNQ for
  the cross-asset study.
- **MNQ MBP-10 events:** CME Globex Market by Price data containing ten displayed
  bid and ask price levels for the market-microstructure study.

The public repository contains schemas, data-quality rules, feature code,
modeling code, frozen specifications, aggregate evidence, and synthetic tests.
It does not redistribute licensed market observations or API credentials.

## What is an opening range?

The opening range is the high-to-low price interval during a predefined period
after the regular U.S. market opens. Study 01 uses 09:30–10:00 New York time.
The initial descriptive question was whether a wider opening range is associated
with larger movement later in the day. The stricter forecasting question was
whether opening-range features improve a model that already knows information
available before the market opens.

The stricter model did not improve out-of-sample forecasts. Its relative
out-of-sample R² was -0.0401, its QLIKE loss was worse than the baseline, and it
improved only 3 of 12 walk-forward folds. The registered gate therefore failed,
and the final holdout was deliberately left unopened.

## What is the MNQ–QQQ idea?

MNQ futures and QQQ both represent exposure to Nasdaq-100 companies, but they
trade in different venues and market structures. Study 02 tests whether recent
MNQ returns contain information that has not yet been fully reflected in QQQ.

The restricted model predicts QQQ using only QQQ's own lagged returns. The
unrestricted model adds lagged MNQ returns. Both models are compared on the same
chronological observations, so the question is whether MNQ adds incremental
forecasting information rather than whether either model can explain markets in
general.

On the single-use final holdout, the unrestricted model produced 0.1888%
incremental out-of-sample R². The paired-loss p-value was 0.0182 and the
session-aggregated p-value was 0.0432. The effect was small, short-lived, and
disappeared when the one-minute MNQ lag was removed. This supports a narrow
information-transmission result, not a claim of tradable profit.

## What is a holdout, and why use one?

A holdout is a protected block of later data that is not used to choose
features, tune models, or change thresholds. It answers a simple question:
does the exact decision rule developed earlier still work on observations the
researcher did not use to design it?

Repeatedly checking a holdout turns it into development data and makes the
reported result too optimistic. This portfolio therefore records holdout state
explicitly:

- Study 01 stopped after its development gate failed, so its final holdout
  remains sealed.
- Study 02 opened its final holdout once and then permanently closed it.
- Study 03 can use only sessions strictly after 2026-07-29 and has not started.
- Study 04 opened its July holdout once, failed replication, and closed without
  retuning.

## What is an order book?

An order book is the market's displayed list of buy and sell interest. The best
displayed buy price is the bid; the best displayed sell price is the ask. The
difference is the spread. Deeper levels show additional displayed quantities at
prices farther from the current market.

Study 04 reconstructs ten bid and ten ask levels from MBP-10 event data. It
creates end-labeled book states every 100 milliseconds, meaning ten snapshots
per second. A millisecond is one-thousandth of a second; 100 milliseconds is
one-tenth of a second. Forecast decisions occur once per second and use only
book information available at that decision timestamp.

The ten-level model passed development validation but failed the frozen July
replication threshold. Its favorable holdout point estimate was about 13% of
the development improvement, and the session-bootstrap confidence interval
crossed zero. The study was closed as a failed replication.

## What does the code do?

The Python code implements the research process rather than an automated
trading system. Examples include:

- validating timestamp, OHLCV, duplicate, interval, and contract-roll rules;
- aligning MNQ and QQQ without using future information;
- constructing opening-range, lagged-return, and order-book features;
- creating chronological and expanding-window evaluation splits;
- fitting transparent restricted and unrestricted baseline models;
- computing QLIKE, log loss, out-of-sample R², HAC tests, and session bootstrap
  intervals;
- enforcing single-use holdout and preregistration rules;
- checking that public reports, figures, and evidence links remain consistent.

Synthetic fixtures exercise the complete software path without pretending that
fabricated observations are market evidence.

## What is Alpha, and did these studies find it?

Alpha is a repeatable forecasting or economic advantage that survives genuine
out-of-sample testing and the frictions required to trade it. Statistical
predictability alone is insufficient. A credible Alpha claim also requires
executable timing, spread, fees, slippage, fills, turnover, market impact,
capacity, and stability across regimes.

This portfolio does **not** claim validated Alpha:

- Study 01 is a negative forecasting result.
- Study 02 confirms a small statistical relationship but does not model a
  tradable implementation.
- Study 03 is designed to test economic relevance but has no eligible sample or
  result yet.
- Study 04 failed its final replication threshold.

## How much profit could this make?

No defensible profit estimate exists yet. Converting the Study 02 relationship
directly into dollars would be misleading because the research has not yet
tested executable fills and total costs on the required future sample. Study 03
was preregistered specifically to answer that question without reusing or tuning
on completed holdouts. Until its sample gate is satisfied, the correct reported
profit is **not estimated**, not zero and not a hypothetical backtest number.

## The concise interpretation

This portfolio demonstrates a complete research discipline: formulate a
falsifiable question, audit licensed data, construct point-in-time features,
compare transparent baselines, validate chronologically, quantify uncertainty,
protect holdouts, and preserve negative results. Its strongest result is a
small MNQ-to-QQQ information-transmission effect. Its strongest methodological
evidence is that unsuccessful ideas were stopped and reported rather than
retuned into attractive-looking strategies.

