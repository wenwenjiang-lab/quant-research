"""Adapters for licensed Databento OHLCV batch files.

The functions in this module never download data. They normalize locally held
CSV or CSV.ZST files into the repository's canonical intraday schema.
"""

from __future__ import annotations

from datetime import time
from pathlib import Path
from typing import Final

import pandas as pd


DATABENTO_COLUMNS: Final[tuple[str, ...]] = (
    "ts_event",
    "instrument_id",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


def discover_databento_ohlcv_files(directory: str | Path) -> list[Path]:
    """Return chronologically named Databento OHLCV CSV files."""
    root = Path(directory)
    if not root.is_dir():
        raise FileNotFoundError(f"Databento directory not found: {root}")
    files = sorted((*root.glob("*.csv"), *root.glob("*.csv.zst")))
    if not files:
        raise FileNotFoundError(f"No Databento OHLCV CSV files found in: {root}")
    return files


def load_databento_ohlcv(directory: str | Path) -> pd.DataFrame:
    """Load a Databento batch into the canonical timezone-aware OHLCV schema.

    Databento event timestamps are interpreted as UTC. Vendor identifiers and
    symbol fields are retained so roll and provenance audits remain possible.
    Duplicate timestamps are rejected rather than silently resolved.
    """
    frames: list[pd.DataFrame] = []
    for path in discover_databento_ohlcv_files(directory):
        frame = pd.read_csv(path, compression="infer")
        missing = [column for column in DATABENTO_COLUMNS if column not in frame.columns]
        if missing:
            raise ValueError(f"{path.name} is missing columns: {', '.join(missing)}")
        frames.append(frame)

    result = pd.concat(frames, ignore_index=True).rename(
        columns={"ts_event": "timestamp"}
    )
    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce", utc=True)
    if result["timestamp"].isna().any():
        raise ValueError("Databento files contain invalid event timestamps")

    numeric = ("open", "high", "low", "close", "volume", "instrument_id")
    for column in numeric:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    if result[list(numeric)].isna().any().any():
        raise ValueError("Databento OHLCV and identifier fields must be numeric")
    if (result[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("Databento prices must be positive")
    if (result["volume"] < 0).any():
        raise ValueError("Databento volume cannot be negative")
    if (result["high"] < result[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("Databento high is inconsistent with OHLC values")
    if (result["low"] > result[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("Databento low is inconsistent with OHLC values")

    result = result.sort_values("timestamp").reset_index(drop=True)
    duplicates = int(result["timestamp"].duplicated().sum())
    if duplicates:
        raise ValueError(f"Databento batch contains {duplicates} duplicate timestamps")
    return result


def select_regular_trading_session(
    bars: pd.DataFrame,
    *,
    timezone: str = "America/New_York",
    start: time = time(9, 30),
    end: time = time(16, 0),
) -> pd.DataFrame:
    """Select weekday bars in the half-open local-time interval ``[start, end)``.

    Timestamps in the returned frame are converted to the research time zone.
    Exchange holidays and shortened sessions are not filled; downstream quality
    gates must flag their incomplete observation windows.
    """
    if "timestamp" not in bars.columns:
        raise ValueError("Missing required column: timestamp")
    if start >= end:
        raise ValueError("start must be earlier than end")
    timestamps = pd.to_datetime(bars["timestamp"], errors="coerce")
    if timestamps.isna().any() or timestamps.dt.tz is None:
        raise ValueError("Timestamps must be valid and timezone-aware")

    local = timestamps.dt.tz_convert(timezone)
    clock = local.dt.time
    mask = (local.dt.weekday < 5) & (clock >= start) & (clock < end)
    result = bars.loc[mask].copy()
    result["timestamp"] = local.loc[mask]
    return result.sort_values("timestamp").reset_index(drop=True)
