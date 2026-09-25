"""Bitstamp OHLC 가격 데이터를 Signal로 변환하는 온체인 수집기.

랩 규칙: 변환 로직(raw → Signal)은 순수 함수로, HTTP 호출은 fetch_* 함수에만 격리.
그래야 변환 로직을 mock 데이터로 테스트할 수 있다.
"""
from __future__ import annotations

import time
from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta, timezone
from math import ceil, isfinite
from typing import Any, Callable, Protocol

import requests

from src.contracts import SIGNAL_SCHEMA_VERSION

BITSTAMP_OHLC_URL = "https://www.bitstamp.net/api/v2/ohlc/usdcusd/"
BITSTAMP_STEP_SECONDS = 3_600
BITSTAMP_MAX_LIMIT = 1_000
BITSTAMP_MAX_HOURS_PER_REQUEST = BITSTAMP_MAX_LIMIT - 1
REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_REQUEST_DELAY_SECONDS = 1.0
DEFAULT_MAX_RETRIES = 3
SUPPORTED_COINS = frozenset({"USDC"})
TimestampValue = str | int | float | datetime
FetchSignals = Callable[[str, TimestampValue, TimestampValue], list[dict[str, Any]]]
Sleep = Callable[[float], None]
UtcNow = Callable[[], datetime]


class ProvisionalRawResponse(Protocol):
    def publish(self) -> object: ...

    def quarantine(self) -> object: ...


class RawResponseSink(Protocol):
    def stage(
        self, body: bytes, start_time: str, end_time: str
    ) -> ProvisionalRawResponse: ...


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_price_signal(coin: str, observed_at: str, price_usd: float) -> dict[str, Any]:
    """원시 가격 값을 Signal 계약(schemas/signal.schema.json)으로 변환한다. 순수 함수."""
    normalized_price = _normalize_price(price_usd)
    return {
        "schema_version": SIGNAL_SCHEMA_VERSION,
        "signal_id": f"onchain-{coin.lower()}-{observed_at}-price",
        "source": "onchain",
        "coin": coin,
        "observed_at": observed_at,
        "metric": "price_usd",
        "value": normalized_price,
    }


def to_peg_deviation_signal(
    coin: str, observed_at: str, price_usd: float
) -> dict[str, Any]:
    """가격에서 페그 이탈(bps)을 계산해 Signal로 변환한다. 순수 함수."""
    normalized_price = _normalize_price(price_usd)
    deviation_bps = (normalized_price - 1.0) * 10_000
    if not isfinite(deviation_bps):
        raise ValueError("peg deviation must be finite")
    return {
        "schema_version": SIGNAL_SCHEMA_VERSION,
        "signal_id": f"onchain-{coin.lower()}-{observed_at}-pegdev",
        "source": "onchain",
        "coin": coin,
        "observed_at": observed_at,
        "metric": "peg_deviation_bps",
        "value": round(deviation_bps, 2),
    }


def _normalize_coin(coin: str) -> str:
    normalized_coin = coin.upper()
    if normalized_coin not in SUPPORTED_COINS:
        raise ValueError(f"unsupported coin: {coin}")
    return normalized_coin


def _to_utc_datetime(value: TimestampValue) -> datetime:
    if value is None:
        raise ValueError("timestamp must not be null")
    if isinstance(value, bool):
        raise ValueError("timestamp must be an ISO 8601 value or Unix epoch seconds")
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, (int, float)):
        if not isfinite(value):
            raise ValueError("timestamp must be finite")
        parsed = datetime.fromtimestamp(value, tz=timezone.utc)
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("timestamp must not be empty")
        try:
            epoch_seconds = int(stripped)
        except ValueError:
            try:
                parsed = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"invalid timestamp: {value!r}") from exc
        else:
            parsed = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
    else:
        raise ValueError("timestamp must be an ISO 8601 value or Unix epoch seconds")

    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    if parsed.microsecond:
        raise ValueError("timestamp must have whole-second precision")
    return parsed.astimezone(timezone.utc)


def normalize_timestamp(value: TimestampValue) -> str:
    """지원되는 timestamp를 Signal v1의 초 단위 UTC Z 형식으로 정규화한다."""
    return _to_utc_datetime(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_epoch_seconds(value: TimestampValue) -> int:
    return int(_to_utc_datetime(value).timestamp())


def _validate_completed_hour_end(end: datetime, now: datetime) -> None:
    if now.tzinfo is None:
        raise ValueError("current time must include a timezone")
    current_utc_hour = now.astimezone(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    )
    if end > current_utc_hour:
        raise ValueError("end_time must not be later than the current UTC hour")


def _normalize_price(value: Any) -> float:
    if value is None:
        raise ValueError("price must not be null")
    if isinstance(value, bool):
        raise ValueError("price must be a finite non-negative number")
    try:
        price = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("price must be a finite non-negative number") from exc
    if not isfinite(price) or price < 0:
        raise ValueError("price must be a finite non-negative number")
    return price


def _validate_hourly_timestamps(
    timestamps: list[int], start_timestamp: int, end_timestamp: int
) -> None:
    """필터링된 OHLC 행이 요청한 모든 시간 관측값을 정확히 포함하는지 검증한다."""
    if len(timestamps) != len(set(timestamps)):
        raise ValueError("duplicate hourly OHLC timestamps")
    if any((timestamp - start_timestamp) % BITSTAMP_STEP_SECONDS for timestamp in timestamps):
        raise ValueError("non-hourly OHLC timestamp")

    expected_timestamps = list(
        range(start_timestamp, end_timestamp, BITSTAMP_STEP_SECONDS)
    )
    if timestamps != expected_timestamps:
        missing_timestamps = sorted(set(expected_timestamps) - set(timestamps))
        if missing_timestamps:
            raise ValueError("missing hourly OHLC timestamps")
        raise ValueError("unexpected hourly OHLC timestamps")


def rows_to_signals(
    coin: str,
    rows: Iterable[Mapping[str, Any]],
    start_time: TimestampValue,
    end_time: TimestampValue,
) -> list[dict[str, Any]]:
    """OHLC 행을 UTC로 정규화하고 완전한 시간대의 Signal로 변환한다."""
    normalized_coin = _normalize_coin(coin)
    start_timestamp = _to_epoch_seconds(start_time)
    end_timestamp = _to_epoch_seconds(end_time)

    normalized_rows = [(_to_epoch_seconds(row.get("timestamp")), row) for row in rows]
    sorted_rows = sorted(normalized_rows, key=lambda item: item[0])
    filtered_rows = [
        (timestamp, row)
        for timestamp, row in sorted_rows
        if start_timestamp <= timestamp < end_timestamp
    ]
    _validate_hourly_timestamps(
        [timestamp for timestamp, _ in filtered_rows],
        start_timestamp,
        end_timestamp,
    )

    signals: list[dict[str, Any]] = []
    for timestamp, row in filtered_rows:
        observed_at = normalize_timestamp(timestamp)
        price_usd = _normalize_price(row.get("close"))
        signals.extend(
            (
                to_price_signal(normalized_coin, observed_at, price_usd),
                to_peg_deviation_signal(normalized_coin, observed_at, price_usd),
            )
        )
    return signals


def fetch_signals(
    coin: str,
    start_time: TimestampValue,
    end_time: TimestampValue,
    *,
    raw_response_sink: RawResponseSink | None = None,
    now_fn: UtcNow = _utc_now,
) -> list[dict[str, Any]]:
    """Bitstamp Public API에서 시간별 종가를 수집해 Signal 목록을 반환한다."""
    normalized_coin = _normalize_coin(coin)
    start = _to_utc_datetime(start_time)
    end = _to_utc_datetime(end_time)
    if end <= start:
        raise ValueError("end_time must be later than start_time")
    _validate_completed_hour_end(end, now_fn())

    required_rows = ceil((end - start).total_seconds() / BITSTAMP_STEP_SECONDS)
    request_rows = required_rows + 1
    if request_rows > BITSTAMP_MAX_LIMIT:
        raise ValueError("requested OHLC range exceeds Bitstamp limit of 1000 rows")
    params = {
        "step": BITSTAMP_STEP_SECONDS,
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
        "limit": request_rows,
    }
    response = requests.get(
        BITSTAMP_OHLC_URL,
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    provisional_raw = None
    if raw_response_sink is not None:
        provisional_raw = raw_response_sink.stage(
            response.content,
            normalize_timestamp(start),
            normalize_timestamp(end),
        )
    try:
        payload = response.json()
        if not isinstance(payload, Mapping):
            raise ValueError("invalid Bitstamp response: expected an object")
        data = payload.get("data")
        if not isinstance(data, Mapping):
            raise ValueError("invalid Bitstamp response: missing data object")
        rows = data.get("ohlc")
        if not isinstance(rows, list):
            raise ValueError("invalid Bitstamp response: missing ohlc array")
        signals = rows_to_signals(normalized_coin, rows, start_time, end_time)
    except Exception:
        if provisional_raw is not None:
            provisional_raw.quarantine()
        raise
    if provisional_raw is not None:
        provisional_raw.publish()
    return signals


def _is_retryable_request_error(error: requests.RequestException) -> bool:
    if isinstance(error, (requests.ConnectionError, requests.Timeout)):
        return True
    if isinstance(error, requests.HTTPError) and error.response is not None:
        status_code = error.response.status_code
        return status_code == 429 or 500 <= status_code < 600
    return False


def fetch_signals_range(
    coin: str,
    start_time: TimestampValue,
    end_time: TimestampValue,
    *,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    sleep_fn: Sleep = time.sleep,
    fetch_fn: FetchSignals | None = None,
    raw_response_sink: RawResponseSink | None = None,
    now_fn: UtcNow = _utc_now,
) -> list[dict[str, Any]]:
    """긴 기간을 안전한 Bitstamp 요청으로 나눠 완전한 Signal 목록을 수집한다."""
    normalized_coin = _normalize_coin(coin)
    start = _to_utc_datetime(start_time)
    end = _to_utc_datetime(end_time)
    if end <= start:
        raise ValueError("end_time must be later than start_time")
    now = now_fn()
    _validate_completed_hour_end(end, now)
    if int(start.timestamp()) % BITSTAMP_STEP_SECONDS or int(
        end.timestamp()
    ) % BITSTAMP_STEP_SECONDS:
        raise ValueError("start_time and end_time must be aligned to an hour")
    if request_delay_seconds < 0:
        raise ValueError("request_delay_seconds must be non-negative")
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    if fetch_fn is not None and raw_response_sink is not None:
        raise ValueError("raw_response_sink requires the default fetch_signals")

    fetch = fetch_fn or fetch_signals
    max_chunk_duration = timedelta(
        seconds=BITSTAMP_MAX_HOURS_PER_REQUEST * BITSTAMP_STEP_SECONDS
    )
    collected: list[dict[str, Any]] = []
    request_count = 0
    chunk_start = start

    while chunk_start < end:
        chunk_end = min(chunk_start + max_chunk_duration, end)
        attempt = 0
        while True:
            if request_count and request_delay_seconds:
                sleep_fn(request_delay_seconds)
            request_count += 1
            try:
                chunk_start_text = normalize_timestamp(chunk_start)
                chunk_end_text = normalize_timestamp(chunk_end)
                if fetch_fn is None:
                    chunk_signals = fetch_signals(
                        normalized_coin,
                        chunk_start_text,
                        chunk_end_text,
                        raw_response_sink=raw_response_sink,
                        now_fn=lambda: now,
                    )
                else:
                    chunk_signals = fetch(
                        normalized_coin,
                        chunk_start_text,
                        chunk_end_text,
                    )
            except requests.RequestException as error:
                if not _is_retryable_request_error(error):
                    raise
                if attempt >= max_retries:
                    raise RuntimeError(
                        "Bitstamp request failed after "
                        f"{attempt + 1} attempts for "
                        f"{normalize_timestamp(chunk_start)} to "
                        f"{normalize_timestamp(chunk_end)}"
                    ) from error
                attempt += 1
                continue
            collected.extend(chunk_signals)
            break
        chunk_start = chunk_end

    price_rows = [
        {"timestamp": signal["observed_at"], "close": signal["value"]}
        for signal in collected
        if signal["metric"] == "price_usd"
    ]
    return rows_to_signals(normalized_coin, price_rows, start, end)
