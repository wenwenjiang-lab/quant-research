# Phase II Feature-Panel Quality Report

> **Scope:** development period only. Licensed observations and the generated
> panel remain local and are excluded from version control.

| Audit item | Result |
|---|---:|
| Source one-minute rows validated | 2,549,259 |
| Eligible development sessions | 1,255 |
| First eligible session | 2019-05-07 |
| Last eligible session | 2024-05-23 |
| Feature timestamps at or after 10:00 | 0 |
| Final-holdout rows accessed | 0 |
| Missing core intraday features or target | 0 |

The strictly lagged historical fields have the expected initialization gaps:
one session for the previous-session feature, five for the five-session mean,
and twenty for the twenty-session mean. These rows will be removed by the
registered complete-case policy before model evaluation, without imputation.

The opening, target, and overnight windows are constructed independently. The
overnight window is anchored to the preceding complete regular-session close,
not to the final overnight bar. No result in this report evaluates predictive
performance or the final holdout.
