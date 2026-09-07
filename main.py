"""로컬 러너 — mock 시그널로 전체 파이프라인을 관통한다 (8주차 데모의 최소 형태).

평시/위기 두 시나리오를 돌리고, 임계값을 넘으면 어댑터 출력(ThreatWatch 경보)까지 보여준다.
I/O는 전부 여기서 담당하고, src/ 의 순수 함수만 호출한다.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.adapters.threatwatch_sender import to_alert_request
from src.engine.risk_score import compute_risk_score

SCENARIOS = {
    "평시 (2023-03-11 새벽)": Path("data/mock/signals_usdc_sample.json"),
    "위기 (2023-03-11 SVB 사태)": Path("data/mock/signals_usdc_crisis.json"),
}


def main() -> None:
    for name, path in SCENARIOS.items():
        signals = json.loads(path.read_text(encoding="utf-8"))
        event = compute_risk_score(signals, coin="USDC")
        print(f"\n=== {name} ===")
        print(json.dumps(event, ensure_ascii=False, indent=2))
        if event["threshold_breached"]:
            alert = to_alert_request(event)
            print("--- ThreatWatch로 발사될 경보 (AlertRequest) ---")
            print(json.dumps(alert, ensure_ascii=False, indent=2))
        else:
            print("--- 임계값 미만: 경보 없음 ---")


if __name__ == "__main__":
    main()
