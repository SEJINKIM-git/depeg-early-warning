import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, call

import pytest
import requests
from jsonschema import Draft202012Validator

from src.collectors.onchain import fetch_signals_range, rows_to_signals

SIGNAL_SCHEMA = Path("schemas/signal.schema.json")
START = datetime(2023, 1, 1, tzinfo=timezone.utc)


def _iso(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _signals_for_range(coin: str, start: str, end: str):
    start_time = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_time = datetime.fromisoformat(end.replace("Z", "+00:00"))
    hours = int((end_time - start_time).total_seconds() // 3_600)
    rows = [
        {
            "timestamp": int((start_time + timedelta(hours=hour)).timestamp()),
            "close": "0.99",
        }
        for hour in range(hours)
    ]
    return rows_to_signals(coin, rows, start, end)


def _http_error(status_code: int) -> requests.HTTPError:
    response = Mock(status_code=status_code)
    return requests.HTTPError(f"HTTP {status_code}", response=response)


def test_fetch_signals_range_uses_one_request_for_short_period():
    start = _iso(START)
    end = _iso(START + timedelta(hours=3))
    fetch = Mock(side_effect=_signals_for_range)
    sleep = Mock()

    signals = fetch_signals_range(
        "usdc", start, end, fetch_fn=fetch, sleep_fn=sleep
    )

    fetch.assert_called_once_with("USDC", start, end)
    sleep.assert_not_called()
    assert len(signals) == 6


def test_fetch_signals_range_rejects_current_candle_before_fetch():
    now = datetime(2023, 1, 1, 10, 30, tzinfo=timezone.utc)
    fetch = Mock()

    with pytest.raises(ValueError, match="current UTC hour"):
        fetch_signals_range(
            "USDC",
            "2023-01-01T10:00:00Z",
            "2023-01-01T11:00:00Z",
            fetch_fn=fetch,
            now_fn=lambda: now,
        )

    fetch.assert_not_called()


def test_fetch_signals_range_chunks_without_duplicate_or_missing_hours():
    start = _iso(START)
    boundary = _iso(START + timedelta(hours=999))
    end = _iso(START + timedelta(hours=1_001))
    fetch = Mock(side_effect=_signals_for_range)
    sleep = Mock()

    signals = fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=2.5,
        fetch_fn=fetch,
        sleep_fn=sleep,
    )

    assert fetch.call_args_list == [
        call("USDC", start, boundary),
        call("USDC", boundary, end),
    ]
    sleep.assert_called_once_with(2.5)
    price_times = [
        signal["observed_at"]
        for signal in signals
        if signal["metric"] == "price_usd"
    ]
    assert len(price_times) == len(set(price_times)) == 1_001
    assert price_times == [
        _iso(START + timedelta(hours=hour)) for hour in range(1_001)
    ]


@pytest.mark.parametrize(
    "transient_error",
    [
        requests.ConnectionError("connection failed"),
        requests.Timeout("timed out"),
        _http_error(429),
        _http_error(503),
    ],
)
def test_fetch_signals_range_retries_transient_errors(transient_error):
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    expected = _signals_for_range("USDC", start, end)
    fetch = Mock(side_effect=[transient_error, expected])
    sleep = Mock()

    signals = fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=0.25,
        max_retries=1,
        fetch_fn=fetch,
        sleep_fn=sleep,
    )

    assert signals == expected
    assert fetch.call_count == 2
    sleep.assert_called_once_with(0.25)


def test_fetch_signals_range_fails_after_retry_limit():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    fetch = Mock(side_effect=requests.Timeout("timed out"))
    sleep = Mock()

    with pytest.raises(RuntimeError, match="failed after 3 attempts"):
        fetch_signals_range(
            "USDC",
            start,
            end,
            request_delay_seconds=0.1,
            max_retries=2,
            fetch_fn=fetch,
            sleep_fn=sleep,
        )

    assert fetch.call_count == 3
    assert sleep.call_args_list == [call(0.1), call(0.1)]


def test_fetch_signals_range_does_not_retry_regular_http_4xx():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    fetch = Mock(side_effect=_http_error(400))
    sleep = Mock()

    with pytest.raises(requests.HTTPError, match="HTTP 400"):
        fetch_signals_range(
            "USDC",
            start,
            end,
            fetch_fn=fetch,
            sleep_fn=sleep,
        )

    fetch.assert_called_once_with("USDC", start, end)
    sleep.assert_not_called()


def test_fetch_signals_range_output_follows_signal_v1_contract():
    start = _iso(START)
    end = _iso(START + timedelta(hours=2))
    signals = fetch_signals_range(
        "USDC", start, end, fetch_fn=_signals_for_range, sleep_fn=Mock()
    )
    schema = json.loads(SIGNAL_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(
        schema, format_checker=Draft202012Validator.FORMAT_CHECKER
    )

    for signal in signals:
        validator.validate(signal)
        assert signal["schema_version"] == 1
