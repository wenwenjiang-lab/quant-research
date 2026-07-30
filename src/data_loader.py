"""Load and validate intraday OHLC market data.

This module intentionally performs no downloading and contains no market data.
Callers are responsible for using a lawfully obtained data source and for making
the source time zone explicit.
"""

from pathlib import Path
from typing import Final

import pandas as pd


REQUIRED_COLUMNS: Final[tuple[str, ...]] = ("timestamp", "open", "high", "low", "close")


def load_ohlc_csv(path: str | Path, *, timezone: str | None = None) -> pd.DataFrame:
    """Load a CSV containing timestamp, open, high, low, and close columns.

    Args:
        path: Location of the input CSV file.
        timezone: IANA time zone assigned to naive timestamps. If timestamps
            already include offsets, they are converted to this time zone when
            supplied. Naive timestamps are rejected when this is omitted.

    Returns:
        A timestamp-sorted DataFrame with validated numeric OHLC columns.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If required columns, timestamps, or prices are invalid.
    """
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Market data file not found: {csv_path}")

    frame = pd.read_csv(csv_path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    timestamps = pd.to_datetime(frame["timestamp"], errors="coerce")
    if timestamps.isna().any():
        raise ValueError("The timestamp column contains invalid values")

    if timestamps.dt.tz is None:
        if timezone is None:
            raise ValueError("Naive timestamps require an explicit timezone")
        timestamps = timestamps.dt.tz_localize(timezone, ambiguous="raise", nonexistent="raise")
    elif timezone is not None:
        timestamps = timestamps.dt.tz_convert(timezone)

    result = frame.copy()
    result["timestamp"] = timestamps
    for column in REQUIRED_COLUMNS[1:]:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    if result[list(REQUIRED_COLUMNS[1:])].isna().any().any():
        raise ValueError("OHLC columns must contain finite numeric values")
    if (result["high"] < result["low"]).any():
        raise ValueError("High prices cannot be below low prices")
    if ((result["open"] > result["high"]) | (result["open"] < result["low"])).any():
        raise ValueError("Open prices must lie within each bar's high-low range")
    if ((result["close"] > result["high"]) | (result["close"] < result["low"])).any():
        raise ValueError("Close prices must lie within each bar's high-low range")

    return result.sort_values("timestamp").reset_index(drop=True)
