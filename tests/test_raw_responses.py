import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
import requests

from scripts.collect_bitstamp_usdc import DEFAULT_RAW_DIRECTORY, main
from src.collectors.onchain import fetch_signals, fetch_signals_range
from src.collectors.raw_store import (
    RawResponseConflictError,
    RawResponseDirectory,
    raw_response_filename,
)

START = datetime(2023, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def raw_tmp_path():
    base = Path("tests/.raw-test-tmp")
    path = base / uuid4().hex
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
        try:
            base.rmdir()
        except OSError:
            pass


def _iso(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _rows(start: datetime, hours: int) -> list[dict[str, str]]:
    return [
        {
            "timestamp": str(int((start + timedelta(hours=hour)).timestamp())),
            "close": "0.9900",
        }
        for hour in range(hours)
    ]


def _response(body: bytes, rows: list[dict[str, str]], status: int = 200) -> Mock:
    response = Mock(status_code=status, content=body)
    response.json.return_value = {"data": {"ohlc": rows}}
    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status}", response=response
        )
    return response


@patch("src.collectors.onchain.requests.get")
def test_fetch_signals_stores_successful_body_before_json_conversion(mock_get):
    events = []
    body = b'{"data": {"ohlc": [{"timestamp": "1672531200", "close": "0.9900"}]}}'
    response = _response(body, _rows(START, 1))
    response.json.side_effect = lambda: events.append("json") or {
        "data": {"ohlc": _rows(START, 1)}
    }
    mock_get.return_value = response

    def sink(raw_body, start, end):
        events.append("raw")
        assert raw_body == body
        assert start == "2023-01-01T00:00:00Z"
        assert end == "2023-01-01T01:00:00Z"

    fetch_signals(
        "USDC",
        "2023-01-01T00:00:00Z",
        "2023-01-01T01:00:00Z",
        raw_response_sink=sink,
    )

    assert events == ["raw", "json"]


@patch("src.collectors.onchain.requests.get")
def test_raw_directory_preserves_body_bytes_and_original_values(
    mock_get, raw_tmp_path
):
    body = (
        b'{\n  "data": {"ohlc": '
        b'[{"timestamp":"1672531200","close":"0.9900"}]}\n}'
    )
    mock_get.return_value = _response(body, _rows(START, 1))
    raw_directory = raw_tmp_path / "raw"

    signals = fetch_signals(
        "USDC",
        "2023-01-01T00:00:00Z",
        "2023-01-01T01:00:00Z",
        raw_response_sink=RawResponseDirectory(raw_directory),
    )

    raw_file = raw_directory / raw_response_filename(
        "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )
    assert raw_file.read_bytes() == body
    assert b'"timestamp":"1672531200"' in raw_file.read_bytes()
    assert b'"close":"0.9900"' in raw_file.read_bytes()
    assert signals[0]["value"] == 0.99


@patch("src.collectors.onchain.requests.get")
def test_multiple_chunks_create_one_raw_file_per_request(mock_get, raw_tmp_path):
    boundary = START + timedelta(hours=999)
    end = START + timedelta(hours=1_001)
    first_rows = _rows(START, 999)
    second_rows = _rows(boundary, 2)
    first_body = json.dumps({"data": {"ohlc": first_rows}}).encode()
    second_body = json.dumps({"data": {"ohlc": second_rows}}).encode()
    mock_get.side_effect = [
        _response(first_body, first_rows),
        _response(second_body, second_rows),
    ]
    raw_directory = raw_tmp_path / "raw"

    signals = fetch_signals_range(
        "USDC",
        _iso(START),
        _iso(end),
        request_delay_seconds=0,
        raw_response_sink=RawResponseDirectory(raw_directory),
    )

    assert len(signals) == 2_002
    assert {path.name for path in raw_directory.iterdir()} == {
        raw_response_filename(_iso(START), _iso(boundary)),
        raw_response_filename(_iso(boundary), _iso(end)),
    }
    assert (
        raw_directory / raw_response_filename(_iso(START), _iso(boundary))
    ).read_bytes() == first_body
    assert (
        raw_directory / raw_response_filename(_iso(boundary), _iso(end))
    ).read_bytes() == second_body


def test_raw_filename_contains_chunk_bounds_and_is_windows_safe():
    filename = raw_response_filename(
        "2023-03-09T00:00:00Z", "2023-03-14T00:00:00Z"
    )

    assert filename == (
        "bitstamp_usdcusd_2023-03-09T00-00-00Z_"
        "2023-03-14T00-00-00Z.json"
    )
    assert not re.search(r'[<>:"/\\|?*]', filename)


@pytest.mark.parametrize("status", [429, 503])
@patch("src.collectors.onchain.requests.get")
def test_retry_stores_only_successful_response(mock_get, status, raw_tmp_path):
    failed_body = f'{{"error":"HTTP {status}"}}'.encode()
    success_rows = _rows(START, 1)
    success_body = json.dumps({"data": {"ohlc": success_rows}}).encode()
    mock_get.side_effect = [
        _response(failed_body, [], status=status),
        _response(success_body, success_rows),
    ]
    raw_directory = raw_tmp_path / "raw"

    fetch_signals_range(
        "USDC",
        "2023-01-01T00:00:00Z",
        "2023-01-01T01:00:00Z",
        request_delay_seconds=0,
        max_retries=1,
        raw_response_sink=RawResponseDirectory(raw_directory),
    )

    files = list(raw_directory.iterdir())
    assert len(files) == 1
    assert files[0].read_bytes() == success_body
    assert files[0].read_bytes() != failed_body


def test_identical_raw_response_is_reused(raw_tmp_path):
    store = RawResponseDirectory(raw_tmp_path)
    body = b'{"same":true}'

    first = store(body, "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z")
    second = store(body, "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z")

    assert first == second
    assert first.read_bytes() == body
    assert len(list(raw_tmp_path.iterdir())) == 1


def test_different_raw_response_for_same_request_raises_conflict(raw_tmp_path):
    store = RawResponseDirectory(raw_tmp_path)
    target = store(
        b'{"version":1}',
        "2023-01-01T00:00:00Z",
        "2023-01-01T01:00:00Z",
    )

    with pytest.raises(RawResponseConflictError, match="raw response conflict"):
        store(
            b'{"version":2}',
            "2023-01-01T00:00:00Z",
            "2023-01-01T01:00:00Z",
        )

    assert target.read_bytes() == b'{"version":1}'


@patch("src.collectors.onchain.requests.get")
def test_fetch_signals_without_sink_does_not_access_raw_body(mock_get):
    class ResponseWithoutRawAccess:
        def raise_for_status(self):
            return None

        @property
        def content(self):
            raise AssertionError("raw body must not be accessed without a sink")

        def json(self):
            return {"data": {"ohlc": _rows(START, 1)}}

    mock_get.return_value = ResponseWithoutRawAccess()

    signals = fetch_signals(
        "USDC", "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )

    assert len(signals) == 2


@patch("scripts.collect_bitstamp_usdc.fetch_signals_range", return_value=[])
def test_cli_enables_default_raw_directory(mock_fetch, capsys):
    assert main(
        [
            "--start",
            "2023-01-01T00:00:00Z",
            "--end",
            "2023-01-01T01:00:00Z",
        ]
    ) == 0

    sink = mock_fetch.call_args.kwargs["raw_response_sink"]
    assert isinstance(sink, RawResponseDirectory)
    assert sink.directory == DEFAULT_RAW_DIRECTORY
    assert capsys.readouterr().out == "[]\n"
