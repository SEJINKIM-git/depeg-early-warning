import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests
from jsonschema import Draft202012Validator

from src.collectors.onchain import (
    fetch_signals,
    normalize_timestamp,
    rows_to_signals,
    to_peg_deviation_signal,
)

START_TIME = "2023-03-09T00:00:00Z"
END_TIME = "2023-03-14T00:00:00Z"
DEPEG_HISTORICAL_DATA = Path(
    "data/historical/signals_usdc_2023_depeg_hourly.json"
)
CALM_HISTORICAL_DATA = Path(
    "data/historical/signals_usdc_2023_calm_hourly.json"
)
SIGNAL_SCHEMA = Path("schemas/signal.schema.json")


def _response(payload: dict) -> Mock:
    response = Mock()
    response.json.return_value = payload
    return response


def test_rows_to_signals_converts_timestamps_filters_range_and_sorts():
    rows = [
        {"timestamp": "1678327200", "close": "0.98"},
        {"timestamp": "1678752000", "close": "1.01"},
        {"timestamp": "1678316400", "close": "1.00"},
        {"timestamp": "1678320000", "close": "0.99"},
        {"timestamp": "1678323600", "close": "0.97"},
    ]

    signals = rows_to_signals(
        "usdc", rows, START_TIME, "2023-03-09T03:00:00Z"
    )

    assert [signal["observed_at"] for signal in signals[::2]] == [
        "2023-03-09T01:00:00Z",
        "2023-03-09T02:00:00Z",
        "2023-03-09T03:00:00Z",
    ]
    assert [signal["value"] for signal in signals[::2]] == [0.99, 0.97, 0.98]
    assert [signal["metric"] for signal in signals] == [
        "price_usd",
        "peg_deviation_bps",
    ] * 3
    assert all(signal["coin"] == "USDC" for signal in signals)
    assert all(signal["schema_version"] == 1 for signal in signals)

    schema = json.loads(SIGNAL_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(
        schema, format_checker=Draft202012Validator.FORMAT_CHECKER
    )
    for signal in signals:
        validator.validate(signal)


@pytest.mark.parametrize(
    ("raw_timestamp", "expected"),
    [
        ("2023-03-11T02:00:00Z", "2023-03-11T02:00:00Z"),
        ("2023-03-11T11:00:00+09:00", "2023-03-11T02:00:00Z"),
        (
            datetime(2023, 3, 11, 11, tzinfo=timezone(timedelta(hours=9))),
            "2023-03-11T02:00:00Z",
        ),
        ("1678500000", "2023-03-11T02:00:00Z"),
    ],
)
def test_normalize_timestamp_outputs_canonical_utc(raw_timestamp, expected):
    assert normalize_timestamp(raw_timestamp) == expected


def test_rows_to_signals_normalizes_mixed_timestamp_types_and_sorts():
    rows = [
        {"timestamp": "2023-03-09T11:00:00+09:00", "close": "0.98"},
        {
            "timestamp": datetime(2023, 3, 9, 9, tzinfo=timezone(timedelta(hours=9))),
            "close": "1.00",
        },
        {"timestamp": "2023-03-09T01:00:00Z", "close": "0.99"},
    ]

    signals = rows_to_signals(
        "USDC", rows, "2023-03-09T09:00:00+09:00", "2023-03-09T03:00:00Z"
    )

    assert [signal["observed_at"] for signal in signals[::2]] == [
        "2023-03-09T01:00:00Z",
        "2023-03-09T02:00:00Z",
        "2023-03-09T03:00:00Z",
    ]


@pytest.mark.parametrize("raw_timestamp", [None, "", "2023-03-11T02:00:00"])
def test_normalize_timestamp_rejects_null_empty_or_timezone_naive_values(
    raw_timestamp,
):
    with pytest.raises(ValueError, match="timestamp"):
        normalize_timestamp(raw_timestamp)


def test_rows_to_signals_rejects_null_price():
    rows = [{"timestamp": "1678320000", "close": None}]

    with pytest.raises(ValueError, match="price must not be null"):
        rows_to_signals("USDC", rows, START_TIME, "2023-03-09T01:00:00Z")


@pytest.mark.parametrize("price", [float("nan"), float("inf"), float("-inf")])
def test_rows_to_signals_rejects_non_finite_price(price):
    rows = [{"timestamp": "1678320000", "close": price}]

    with pytest.raises(ValueError, match="finite non-negative number"):
        rows_to_signals("USDC", rows, START_TIME, "2023-03-09T01:00:00Z")


def test_peg_deviation_rejects_finite_price_when_calculation_overflows():
    with pytest.raises(ValueError, match="peg deviation must be finite"):
        to_peg_deviation_signal("USDC", START_TIME, 1e308)


def test_rows_to_signals_rejects_null_timestamp():
    rows = [{"timestamp": None, "close": "0.99"}]

    with pytest.raises(ValueError, match="timestamp must not be null"):
        rows_to_signals("USDC", rows, START_TIME, "2023-03-09T01:00:00Z")


@patch("src.collectors.onchain.requests.get")
def test_fetch_signals_uses_bitstamp_parameters(mock_get):
    mock_get.return_value = _response(
        {
            "data": {
                "ohlc": [
                    {
                        "timestamp": str(1678320000 + (hour * 3600)),
                        "close": "0.99",
                    }
                    for hour in range(121)
                ]
            }
        }
    )

    signals = fetch_signals("usdc", START_TIME, END_TIME)

    mock_get.assert_called_once_with(
        "https://www.bitstamp.net/api/v2/ohlc/usdcusd/",
        params={
            "step": 3600,
            "start": 1678320000,
            "end": 1678752000,
            "limit": 121,
        },
        timeout=30,
    )
    mock_get.return_value.raise_for_status.assert_called_once_with()
    assert len(signals) == 240
    assert signals[0]["observed_at"] == "2023-03-09T01:00:00Z"
    assert signals[0]["signal_id"] == "onchain-usdc-2023-03-09T01:00:00Z-price"
    assert signals[-1]["observed_at"] == END_TIME


@patch("src.collectors.onchain.requests.get")
def test_fetch_signals_rejects_current_candle_before_http_request(mock_get):
    now = datetime(2023, 3, 9, 10, 30, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="current UTC hour"):
        fetch_signals(
            "USDC",
            "2023-03-09T10:00:00Z",
            "2023-03-09T11:00:00Z",
            now_fn=lambda: now,
        )

    mock_get.assert_not_called()


@patch("src.collectors.onchain.requests.get")
def test_fetch_signals_accepts_range_ending_at_current_hour(mock_get):
    now = datetime(2023, 3, 9, 10, 30, tzinfo=timezone.utc)
    mock_get.return_value = _response(
        {
            "data": {
                "ohlc": [
                    {"timestamp": "1678352400", "close": "0.99"},
                    {"timestamp": "1678356000", "close": "1.00"},
                ]
            }
        }
    )

    signals = fetch_signals(
        "USDC",
        "2023-03-09T09:00:00Z",
        "2023-03-09T10:00:00Z",
        now_fn=lambda: now,
    )

    assert len(signals) == 2
    mock_get.assert_called_once()


@patch("src.collectors.onchain.requests.get")
def test_fetch_signals_propagates_http_errors(mock_get):
    response = _response({"data": {"ohlc": []}})
    response.raise_for_status.side_effect = requests.HTTPError("server error")
    mock_get.return_value = response

    with pytest.raises(requests.HTTPError, match="server error"):
        fetch_signals("USDC", START_TIME, END_TIME)

    response.raise_for_status.assert_called_once_with()
    response.json.assert_not_called()


@patch("src.collectors.onchain.requests.get")
def test_fetch_signals_rejects_unsupported_coin_without_http_request(mock_get):
    with pytest.raises(ValueError, match="unsupported coin: USDT"):
        fetch_signals("USDT", START_TIME, END_TIME)

    mock_get.assert_not_called()


@patch("src.collectors.onchain.requests.get")
def test_fetch_signals_rejects_ranges_requiring_more_than_1000_rows(mock_get):
    with pytest.raises(ValueError, match="exceeds Bitstamp limit"):
        fetch_signals("USDC", START_TIME, "2023-04-19T16:00:00Z")

    mock_get.assert_not_called()


def test_rows_to_signals_rejects_missing_hourly_timestamp():
    rows = [
        {"timestamp": "1678320000", "close": "0.99"},
        {"timestamp": "1678327200", "close": "0.98"},
    ]

    with pytest.raises(ValueError, match="missing hourly OHLC timestamps"):
        rows_to_signals("USDC", rows, START_TIME, "2023-03-09T03:00:00Z")


def test_rows_to_signals_rejects_duplicate_hourly_timestamp():
    rows = [
        {"timestamp": "1678320000", "close": "0.99"},
        {"timestamp": "2023-03-09T09:00:00+09:00", "close": "0.99"},
        {"timestamp": "1678323600", "close": "0.98"},
    ]

    with pytest.raises(ValueError, match="duplicate hourly OHLC timestamps"):
        rows_to_signals("USDC", rows, START_TIME, "2023-03-09T02:00:00Z")


@pytest.mark.parametrize(
    ("historical_data", "start_time", "expected_hours"),
    [
        (
            DEPEG_HISTORICAL_DATA,
            datetime(2023, 3, 9, tzinfo=timezone.utc),
            120,
        ),
        (
            CALM_HISTORICAL_DATA,
            datetime(2023, 1, 15, tzinfo=timezone.utc),
            672,
        ),
    ],
)
def test_historical_signals_are_complete_unique_and_schema_valid(
    historical_data,
    start_time,
    expected_hours,
):
    signals = json.loads(historical_data.read_text(encoding="utf-8"))
    schema = json.loads(SIGNAL_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(
        schema, format_checker=Draft202012Validator.FORMAT_CHECKER
    )

    assert len(signals) == expected_hours * 2
    for signal in signals:
        validator.validate(signal)

    signal_keys = [
        (signal["observed_at"], signal["metric"])
        for signal in signals
    ]
    assert len(signal_keys) == len(set(signal_keys))

    signal_ids = [signal["signal_id"] for signal in signals]
    assert len(signal_ids) == len(set(signal_ids))

    price_times = [
        signal["observed_at"]
        for signal in signals
        if signal["metric"] == "price_usd"
    ]
    expected_times = [
        (start_time + timedelta(hours=hour + 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for hour in range(expected_hours)
    ]

    # Historical exports must be complete and stored in chronological order.
    assert price_times == expected_times
    assert len(price_times) == len(set(price_times)) == expected_hours

    metrics_by_time: dict[str, set[str]] = {}
    prices_by_time: dict[str, float] = {}
    peg_deviations_by_time: dict[str, float] = {}

    for signal in signals:
        metrics_by_time.setdefault(
            signal["observed_at"], set()
        ).add(signal["metric"])

        if signal["metric"] == "price_usd":
            prices_by_time[signal["observed_at"]] = signal["value"]

        if signal["metric"] == "peg_deviation_bps":
            peg_deviations_by_time[signal["observed_at"]] = signal["value"]

    assert set(metrics_by_time) == set(expected_times)
    assert all(
        metrics == {"price_usd", "peg_deviation_bps"}
        for metrics in metrics_by_time.values()
    )
    assert all(
        peg_deviations_by_time[observed_at]
        == round((price_usd - 1.0) * 10_000, 2)
        for observed_at, price_usd in prices_by_time.items()
    )
