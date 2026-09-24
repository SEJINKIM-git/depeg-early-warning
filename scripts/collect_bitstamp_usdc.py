"""Collect Bitstamp USDC/USD hourly prices and print Signal v1 JSON."""

from __future__ import annotations

import argparse
import json
import sys

import requests

from src.collectors.onchain import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_REQUEST_DELAY_SECONDS,
    fetch_signals_range,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect Bitstamp USDC/USD hourly Signal v1 JSON."
    )
    parser.add_argument("--start", required=True, help="Inclusive UTC start timestamp")
    parser.add_argument("--end", required=True, help="Exclusive UTC end timestamp")
    parser.add_argument(
        "--request-delay",
        type=float,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
        help="Seconds between consecutive HTTP requests",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help="Retries after the initial attempt for each chunk",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        signals = fetch_signals_range(
            "USDC",
            args.start,
            args.end,
            request_delay_seconds=args.request_delay,
            max_retries=args.max_retries,
        )
    except (ValueError, RuntimeError, requests.RequestException) as error:
        parser.exit(1, f"error: {error}\n")
    json.dump(signals, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
