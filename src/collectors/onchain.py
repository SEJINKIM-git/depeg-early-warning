"""온체인 수집기 스켈레톤 — 역할 1(학생 A) 담당.

랩 규칙: 변환 로직(raw → Signal)은 순수 함수로, HTTP 호출은 fetch_* 함수에만 격리.
그래야 변환 로직을 mock 데이터로 테스트할 수 있다.

TODO(역할 1): 실제 가격 API 연동 + 과거 사고 주간(2022 테라, 2023 USDC) 데이터 확보.
"""
from __future__ import annotations

from typing import Any


def to_price_signal(coin: str, observed_at: str, price_usd: float) -> dict[str, Any]:
    """원시 가격 값을 Signal 계약(schemas/signal.schema.json)으로 변환한다. 순수 함수."""
    return {
        "signal_id": f"onchain-{coin.lower()}-{observed_at}-price",
        "source": "onchain",
        "coin": coin,
        "observed_at": observed_at,
        "metric": "price_usd",
        "value": price_usd,
    }


def to_peg_deviation_signal(coin: str, observed_at: str, price_usd: float) -> dict[str, Any]:
    """가격에서 페그 이탈(bps)을 계산해 Signal로 변환한다. 순수 함수."""
    deviation_bps = (price_usd - 1.0) * 10_000
    return {
        "signal_id": f"onchain-{coin.lower()}-{observed_at}-pegdev",
        "source": "onchain",
        "coin": coin,
        "observed_at": observed_at,
        "metric": "peg_deviation_bps",
        "value": round(deviation_bps, 2),
    }
