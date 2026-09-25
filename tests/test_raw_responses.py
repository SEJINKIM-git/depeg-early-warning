import json
import re
import shutil
import subprocess
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
def test_fetch_signals_stages_body_before_json_and_publishes_after_validation(
    mock_get,
):
    events = []
    body = b'{"data": {"ohlc": [{"timestamp": "1672531200", "close": "0.9900"}]}}'
    response = _response(body, _rows(START, 1))
    response.json.side_effect = lambda: events.append("json") or {
        "data": {"ohlc": _rows(START, 1)}
    }
    mock_get.return_value = response

    class Provisional:
        def publish(self):
            events.append("publish")

        def quarantine(self):
            events.append("quarantine")

    class Sink:
        def stage(self, raw_body, start, end):
            events.append("stage")
            assert raw_body == body
            assert start == "2023-01-01T00:00:00Z"
            assert end == "2023-01-01T01:00:00Z"
            return Provisional()

    fetch_signals(
        "USDC",
        "2023-01-01T00:00:00Z",
        "2023-01-01T01:00:00Z",
        raw_response_sink=Sink(),
    )

    assert events == ["stage", "json", "publish"]


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (ValueError("invalid JSON"), "invalid JSON"),
        ({}, "missing data object"),
        ({"data": {}}, "missing ohlc array"),
        ({"data": {"ohlc": []}}, "missing hourly OHLC timestamps"),
    ],
)
@patch("src.collectors.onchain.requests.get")
def test_invalid_success_response_is_quarantined_not_canonical(
    mock_get, payload, error, raw_tmp_path
):
    body = b"invalid-success-body"
    response = _response(body, [])
    if isinstance(payload, Exception):
        response.json.side_effect = payload
    else:
        response.json.return_value = payload
    mock_get.return_value = response
    raw_directory = raw_tmp_path / "raw"

    with pytest.raises(ValueError, match=error):
        fetch_signals(
            "USDC",
            "2023-01-01T00:00:00Z",
            "2023-01-01T01:00:00Z",
            raw_response_sink=RawResponseDirectory(raw_directory),
        )

    canonical = raw_directory / raw_response_filename(
        "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )
    failed_files = list((raw_directory / "failed").glob("*.json"))
    assert not canonical.exists()
    assert len(failed_files) == 1
    assert failed_files[0].read_bytes() == body


@patch("src.collectors.onchain.requests.get")
def test_quarantined_response_does_not_block_later_valid_response(
    mock_get, raw_tmp_path
):
    valid_rows = _rows(START, 1)
    invalid_response = _response(b"invalid", [])
    invalid_response.json.return_value = {"data": {"ohlc": []}}
    mock_get.side_effect = [
        invalid_response,
        _response(b"valid", valid_rows),
    ]
    raw_directory = raw_tmp_path / "raw"
    sink = RawResponseDirectory(raw_directory)

    with pytest.raises(ValueError, match="missing hourly OHLC timestamps"):
        fetch_signals(
            "USDC",
            "2023-01-01T00:00:00Z",
            "2023-01-01T01:00:00Z",
            raw_response_sink=sink,
        )

    signals = fetch_signals(
        "USDC",
        "2023-01-01T00:00:00Z",
        "2023-01-01T01:00:00Z",
        raw_response_sink=sink,
    )
    canonical = raw_directory / raw_response_filename(
        "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )
    assert len(signals) == 2
    assert canonical.read_bytes() == b"valid"


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


def test_two_staged_identical_responses_publish_one_complete_file(raw_tmp_path):
    store = RawResponseDirectory(raw_tmp_path)
    first = store.stage(
        b"same", "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )
    second = store.stage(
        b"same", "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )

    first_path = first.publish()
    second_path = second.publish()

    assert first_path == second_path
    assert first_path.read_bytes() == b"same"
    assert not list(raw_tmp_path.glob("*.tmp"))


def test_two_staged_different_responses_conflict_without_overwrite(raw_tmp_path):
    store = RawResponseDirectory(raw_tmp_path)
    first = store.stage(
        b"first", "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )
    second = store.stage(
        b"second", "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )

    target = first.publish()
    with pytest.raises(RawResponseConflictError):
        second.publish()

    assert target.read_bytes() == b"first"
    assert not list(raw_tmp_path.glob("*.tmp"))


@patch("src.collectors.raw_store.os.link", side_effect=OSError("publish failed"))
def test_publish_failure_leaves_no_partial_canonical(mock_link, raw_tmp_path):
    store = RawResponseDirectory(raw_tmp_path)
    staged = store.stage(
        b"body", "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )
    canonical = raw_tmp_path / raw_response_filename(
        "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
    )

    with pytest.raises(OSError, match="publish failed"):
        staged.publish()

    assert not canonical.exists()
    assert not list(raw_tmp_path.glob("*.tmp"))


@patch("src.collectors.raw_store.os.fsync", side_effect=OSError("write failed"))
def test_write_failure_leaves_no_partial_canonical(mock_fsync, raw_tmp_path):
    store = RawResponseDirectory(raw_tmp_path)

    with pytest.raises(OSError, match="write failed"):
        store.stage(
            b"body", "2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"
        )

    assert not list(raw_tmp_path.iterdir())


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


@patch(
    "scripts.collect_bitstamp_usdc.fetch_signals_range",
    return_value=[{"value": float("nan")}],
)
def test_cli_rejects_non_finite_json_without_partial_stdout(mock_fetch, capsys):
    with pytest.raises(SystemExit) as error:
        main(
            [
                "--start",
                "2023-01-01T00:00:00Z",
                "--end",
                "2023-01-01T01:00:00Z",
            ]
        )

    captured = capsys.readouterr()
    assert error.value.code == 1
    assert captured.out == ""
    assert "Out of range float values" in captured.err


def test_raw_json_and_temp_are_ignored_but_gitkeep_is_retained():
    raw_json = "data/raw/bitstamp/usdcusd/example.json"
    raw_temp = "data/raw/bitstamp/usdcusd/example.tmp"
    gitkeep = "data/raw/bitstamp/usdcusd/.gitkeep"

    assert subprocess.run(
        ["git", "check-ignore", "-q", raw_json], check=False
    ).returncode == 0
    assert subprocess.run(
        ["git", "check-ignore", "-q", raw_temp], check=False
    ).returncode == 0
    assert subprocess.run(
        ["git", "check-ignore", "-q", gitkeep], check=False
    ).returncode == 1
