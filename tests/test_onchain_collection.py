import json
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
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


def _http_error(
    status_code: int, headers: dict[str, str] | None = None
) -> requests.HTTPError:
    response = Mock(status_code=status_code, headers=headers or {})
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
        _iso(START + timedelta(hours=hour + 1)) for hour in range(1_001)
    ]


@pytest.mark.parametrize(
    "transient_error",
    [
        requests.ConnectionError("connection failed"),
        requests.Timeout("timed out"),
        _http_error(408),
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
        retry_delay_seconds=0.25,
        max_retries=1,
        fetch_fn=fetch,
        sleep_fn=sleep,
    )

    assert signals == expected
    assert fetch.call_count == 2
    sleep.assert_called_once_with(0.25)


def test_fetch_signals_range_uses_exponential_backoff_for_repeated_429s():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    expected = _signals_for_range("USDC", start, end)
    fetch = Mock(
        side_effect=[
            _http_error(429),
            _http_error(429),
            _http_error(429),
            expected,
        ]
    )
    sleep = Mock()

    signals = fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=1.0,
        retry_delay_seconds=1.0,
        max_retries=3,
        fetch_fn=fetch,
        sleep_fn=sleep,
    )

    assert signals == expected
    assert fetch.call_count == 4
    assert sleep.call_args_list == [call(1.0), call(2.0), call(4.0)]


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
            retry_delay_seconds=0.1,
            max_retries=2,
            fetch_fn=fetch,
            sleep_fn=sleep,
        )

    assert fetch.call_count == 3
    assert sleep.call_args_list == [call(0.1), call(0.2)]


def test_retry_wait_is_applied_when_normal_request_delay_is_zero():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    expected = _signals_for_range("USDC", start, end)
    fetch = Mock(side_effect=[requests.Timeout("timed out"), expected])
    sleep = Mock()

    fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=0,
        retry_delay_seconds=0.75,
        max_retries=1,
        fetch_fn=fetch,
        sleep_fn=sleep,
    )

    sleep.assert_called_once_with(0.75)


def test_retry_after_seconds_takes_priority_over_exponential_backoff():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    expected = _signals_for_range("USDC", start, end)
    fetch = Mock(side_effect=[_http_error(429, {"Retry-After": "7"}), expected])
    sleep = Mock()

    fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=0,
        retry_delay_seconds=1,
        max_retry_delay_seconds=10,
        max_retries=1,
        fetch_fn=fetch,
        sleep_fn=sleep,
    )

    sleep.assert_called_once_with(7.0)


def test_retry_after_http_date_is_supported():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    retry_now = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)
    retry_at = format_datetime(retry_now + timedelta(seconds=90), usegmt=True)
    expected = _signals_for_range("USDC", start, end)
    fetch = Mock(side_effect=[_http_error(503, {"Retry-After": retry_at}), expected])
    sleep = Mock()

    fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=0,
        retry_delay_seconds=1,
        max_retry_delay_seconds=10,
        max_retries=1,
        fetch_fn=fetch,
        sleep_fn=sleep,
        retry_now_fn=lambda: retry_now,
    )

    sleep.assert_called_once_with(90.0)


def test_rate_limit_reset_takes_priority_over_maximum_backoff():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    retry_now = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)
    reset_at = str(int((retry_now + timedelta(seconds=120)).timestamp()))
    expected = _signals_for_range("USDC", start, end)
    fetch = Mock(
        side_effect=[_http_error(429, {"X-RateLimit-Reset": reset_at}), expected]
    )
    sleep = Mock()

    fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=0,
        retry_delay_seconds=1,
        max_retry_delay_seconds=30,
        max_retries=1,
        fetch_fn=fetch,
        sleep_fn=sleep,
        retry_now_fn=lambda: retry_now,
    )

    sleep.assert_called_once_with(120.0)


def test_invalid_retry_after_uses_capped_exponential_backoff():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    expected = _signals_for_range("USDC", start, end)
    error = _http_error(429, {"Retry-After": "not-a-delay"})
    fetch = Mock(side_effect=[error, error, error, expected])
    sleep = Mock()

    fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=0,
        retry_delay_seconds=2,
        max_retry_delay_seconds=3,
        max_retries=3,
        fetch_fn=fetch,
        sleep_fn=sleep,
    )

    assert sleep.call_args_list == [call(2), call(3), call(3)]


def test_retry_after_is_not_capped_by_maximum_backoff_delay():
    start = _iso(START)
    end = _iso(START + timedelta(hours=1))
    expected = _signals_for_range("USDC", start, end)
    fetch = Mock(side_effect=[_http_error(429, {"Retry-After": "600"}), expected])
    sleep = Mock()

    fetch_signals_range(
        "USDC",
        start,
        end,
        request_delay_seconds=0,
        retry_delay_seconds=1,
        max_retry_delay_seconds=30,
        max_retries=1,
        fetch_fn=fetch,
        sleep_fn=sleep,
    )

    sleep.assert_called_once_with(600.0)


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
