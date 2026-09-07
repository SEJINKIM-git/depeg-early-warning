"""로컬 러너 — mock 시그널로 전체 파이프라인을 관통한다 (8주차 데모의 최소 형태).

사용법: python main.py
I/O는 전부 여기서 담당하고, src/ 의 순수 함수만 호출한다.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.engine.risk_score import compute_risk_score

MOCK = Path("data/mock/signals_usdc_sample.json")


def main() -> None:
    signals = json.loads(MOCK.read_text(encoding="utf-8"))
    event = compute_risk_score(signals, coin="USDC")
    print(json.dumps(event, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
