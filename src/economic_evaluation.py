"""Frozen economic-evaluation primitives for prospective Study 03."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EconomicSummary:
    """Cost-aware performance summary aggregated by session."""

    gross_pnl: float
    net_pnl: float
    traded_notional: float
    turnover_shares: float
    maximum_drawdown: float
    positive_session_fraction: float
    net_session_sharpe: float
    net_pnl_ci_lower: float
    net_pnl_ci_upper: float
    break_even_one_way_bps: float
    session_count: int


@dataclass(frozen=True)
class DecisionRuleResult:
    """Transparent result of the preregistered pass/fail rule."""

    passed: bool
    positive_net_pnl: bool
    positive_lower_confidence_bound: bool
    majority_positive_sessions: bool
    survives_required_slippage: bool


def session_bootstrap_total_ci(
    session_pnl: pd.Series,
    *,
    confidence: float = 0.95,
    resamples: int = 10_000,
    seed: int = 0,
) -> tuple[float, float]:
    """Bootstrap total P&L by resampling whole sessions with replacement."""
    values = pd.to_numeric(session_pnl, errors="coerce").to_numpy(dtype=float)
    if values.size < 2 or not np.isfinite(values).all():
        raise ValueError("session_pnl must contain at least two finite sessions")
    if not 0 < confidence < 1:
        raise ValueError("confidence must lie strictly between zero and one")
    if not isinstance(resamples, int) or resamples < 1:
        raise ValueError("resamples must be a positive integer")

    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(resamples, values.size), replace=True).sum(axis=1)
    tail = (1.0 - confidence) / 2.0
    lower, upper = np.quantile(draws, [tail, 1.0 - tail])
    return float(lower), float(upper)


def summarize_economic_performance(
    pnl: pd.DataFrame,
    session: pd.Series,
    *,
    annualization_sessions: int = 252,
    bootstrap_resamples: int = 10_000,
    bootstrap_seed: int = 0,
) -> EconomicSummary:
    """Summarize an already costed, chronological intraday P&L stream."""
    required = {"gross_pnl", "net_pnl", "trade_quantity", "traded_notional"}
    missing = required.difference(pnl.columns)
    if missing:
        raise ValueError(f"Missing required P&L columns: {sorted(missing)}")
    if not pnl.index.equals(session.index):
        raise ValueError("pnl and session must have identical indexes")
    if session.isna().any():
        raise ValueError("Session labels cannot be missing")
    numeric = pnl[list(required)].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("P&L inputs must be finite")

    net_by_session = numeric["net_pnl"].groupby(session, sort=False).sum()
    lower, upper = session_bootstrap_total_ci(
        net_by_session,
        resamples=bootstrap_resamples,
        seed=bootstrap_seed,
    )
    cumulative = net_by_session.cumsum()
    drawdown = cumulative - cumulative.cummax().clip(lower=0.0)
    standard_deviation = float(net_by_session.std(ddof=1))
    sharpe = (
        float(net_by_session.mean() / standard_deviation * np.sqrt(annualization_sessions))
        if standard_deviation > 0
        else 0.0
    )
    traded_notional = float(numeric["traded_notional"].sum())
    gross_pnl = float(numeric["gross_pnl"].sum())
    break_even_bps = (
        gross_pnl / traded_notional * 10_000.0 if traded_notional > 0 else 0.0
    )
    return EconomicSummary(
        gross_pnl=gross_pnl,
        net_pnl=float(numeric["net_pnl"].sum()),
        traded_notional=traded_notional,
        turnover_shares=float(numeric["trade_quantity"].abs().sum()),
        maximum_drawdown=float(-drawdown.min()),
        positive_session_fraction=float((net_by_session > 0).mean()),
        net_session_sharpe=sharpe,
        net_pnl_ci_lower=lower,
        net_pnl_ci_upper=upper,
        break_even_one_way_bps=break_even_bps,
        session_count=len(net_by_session),
    )


def evaluate_preregistered_rule(
    base_summary: EconomicSummary,
    required_slippage_summary: EconomicSummary,
) -> DecisionRuleResult:
    """Apply the frozen Study 03 primary decision rule without retuning."""
    positive_net = base_summary.net_pnl > 0.0
    positive_lower = base_summary.net_pnl_ci_lower > 0.0
    majority_positive = base_summary.positive_session_fraction > 0.50
    survives_slippage = required_slippage_summary.net_pnl > 0.0
    return DecisionRuleResult(
        passed=positive_net and positive_lower and majority_positive and survives_slippage,
        positive_net_pnl=positive_net,
        positive_lower_confidence_bound=positive_lower,
        majority_positive_sessions=majority_positive,
        survives_required_slippage=survives_slippage,
    )
