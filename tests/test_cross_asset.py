import pandas as pd
import pytest

from src.cross_asset import build_synchronized_return_panel, validate_price_bars


def _bars(prices, *, start="2024-01-02 09:30", missing=()):
    timestamps = pd.date_range(start, periods=len(prices), freq="min", tz="America/New_York")
    frame = pd.DataFrame({"timestamp": timestamps, "close": prices})
    return frame.drop(index=list(missing)).reset_index(drop=True)


def test_validation_rejects_naive_timestamps():
    bars = pd.DataFrame(
        {"timestamp": pd.date_range("2024-01-02 09:30", periods=2, freq="min"), "close": [1, 2]}
    )
    with pytest.raises(ValueError, match="timezone-aware"):
        validate_price_bars(bars, asset="test")


def test_panel_uses_only_exactly_overlapping_timestamps():
    futures = _bars([100, 101, 102, 103, 104, 105])
    qqq = _bars([400, 401, 402, 403, 404, 405], missing=(2,))

    panel = build_synchronized_return_panel(futures, qqq, lags=(1,))

    missing_timestamp = pd.Timestamp("2024-01-02 09:32", tz="America/New_York")
    assert missing_timestamp not in set(panel["timestamp"])
    assert panel["timestamp"].is_unique


def test_cross_asset_predictors_are_strictly_lagged():
    futures = _bars([100, 102, 101, 104, 108, 107])
    qqq = _bars([400, 404, 408, 406, 410, 412])

    panel = build_synchronized_return_panel(futures, qqq, lags=(1, 2))
    full_returns = futures.set_index("timestamp")["close"].pct_change(fill_method=None)

    for _, row in panel.iterrows():
        timestamp = pd.Timestamp(row["timestamp"])
        assert row["futures_return_lag1"] == pytest.approx(
            full_returns.loc[timestamp - pd.Timedelta(minutes=1)]
        )
        assert row["futures_return_lag2"] == pytest.approx(
            full_returns.loc[timestamp - pd.Timedelta(minutes=2)]
        )


@pytest.mark.parametrize("lags", [(), (0,), (1, 1)])
def test_invalid_lag_specifications_fail(lags):
    with pytest.raises(ValueError):
        build_synchronized_return_panel(_bars([1, 2, 3]), _bars([1, 2, 3]), lags=lags)
