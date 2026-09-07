"""오프체인 attestation 파서 스켈레톤 — 역할 2 담당.

랩 규칙: PDF 파일 읽기(I/O)와 텍스트 → Signal 변환(순수 함수)을 분리.

TODO(역할 2): PyMuPDF로 USDC attestation에서 준비금 구성을 추출하는 로직 구현.
"""
from __future__ import annotations

from typing import Any


def to_reserve_signals(
    coin: str, observed_at: str, cash_ratio: float, tbill_ratio: float
) -> list[dict[str, Any]]:
    """파싱된 준비금 비중을 Signal 계약 목록으로 변환한다. 순수 함수."""
    base = f"offchain-{coin.lower()}-{observed_at}"
    return [
        {
            "signal_id": f"{base}-cash",
            "source": "offchain",
            "coin": coin,
            "observed_at": observed_at,
            "metric": "reserve_cash_ratio",
            "value": cash_ratio,
        },
        {
            "signal_id": f"{base}-tbill",
            "source": "offchain",
            "coin": coin,
            "observed_at": observed_at,
            "metric": "reserve_tbill_ratio",
            "value": tbill_ratio,
        },
    ]
