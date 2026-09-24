"""로컬 러너 — mock 시그널로 전체 파이프라인을 관통한다 (8주차 데모의 최소 형태).

평시/위기 두 시나리오를 돌리고, 임계값을 넘으면 어댑터 출력(ThreatWatch 경보)까지 보여준다.
I/O는 전부 여기서 담당하고, src/ 의 순수 함수만 호출한다.
"""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from src.adapters.threatwatch_sender import to_alert_request
from src.contracts import SIGNAL_SCHEMA_VERSION, validate_signals
from src.engine.risk_score import compute_risk_score

SCENARIOS = {
    "평시 (2023-03-11 새벽)": Path("data/mock/signals_usdc_sample.json"),
    "위기 (2023-03-11 SVB 사태)": Path("data/mock/signals_usdc_crisis.json"),
}
SIGNAL_SCHEMA_PATHS = {SIGNAL_SCHEMA_VERSION: Path("schemas/signal.schema.json")}


def _load_signal_validators() -> dict[int, Draft202012Validator]:
    """버전별 Signal 스키마를 읽고 실제 형식 검사기를 연결한다."""
    return {
        version: Draft202012Validator(
            json.loads(path.read_text(encoding="utf-8")),
            format_checker=FormatChecker(),
        )
        for version, path in SIGNAL_SCHEMA_PATHS.items()
    }


def main() -> None:
    signal_validators = _load_signal_validators()
    for name, path in SCENARIOS.items():
        signals = json.loads(path.read_text(encoding="utf-8"))
        validate_signals(signals, signal_validators)
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
