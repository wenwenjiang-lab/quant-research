# Phase II Development Results

> **Decision: confirmation gate not passed.** These are development-period
> walk-forward results. The final holdout remains sealed and no alpha is claimed.

The primary pre-open baseline contains lag-1, lag-5, and lag-20 session-range
features plus overnight return, overnight range, and opening gap. The candidate
adds opening-range width and opening-range return. Both models use identical
expanding-window folds, a 504-session minimum training window, 63-session test
blocks, and a one-session embargo.

| Metric | Pre-open baseline | Baseline + Opening Range |
|---|---:|---:|
| Out-of-sample sessions | 730 | 730 |
| RMSE | 65.0295 | 66.3212 |
| Mean QLIKE | 0.07563 | 0.07927 |
| OOS R² relative to baseline | — | -0.0401 |

The candidate-minus-baseline QLIKE difference is 0.00364. A Newey-West paired
loss comparison with five lags gives a standard error of 0.00212, statistic
1.716, and two-sided p-value 0.086. Positive differences favor the baseline.
The candidate improves QLIKE in only 3 of 12 evaluation folds (25%).

These results fail the registered requirements of positive OOS R², lower
candidate QLIKE, a paired-loss p-value below 0.05 in the favorable direction,
and improvement in more than 60% of folds. Opening-range information therefore
does not demonstrate incremental forecasting value under this specification.
The correct action is to keep the holdout sealed. Any revised specification
must be labeled as a new exploratory study rather than retrofitted confirmation.
