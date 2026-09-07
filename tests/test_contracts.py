"""데이터 계약 테스트 — 모든 모듈의 출력이 스키마를 지키는지 검증한다.

이 테스트가 초록색이면 팀 간 통합이 깨질 수 없다. 스키마를 바꾸면 여기부터 빨간불이 든다.
"""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from src.collectors.onchain import to_peg_deviation_signal, to_price_signal
from src.engine.risk_score import compute_risk_score
from src.intelligence.attestation_parser import to_reserve_signals

SCHEMAS = Path("schemas")
MOCK = Path("data/mock/signals_usdc_sample.json")


def _validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((SCHEMAS / name).read_text(encoding="utf-8")))


signal_v = _validator("signal.schema.json")
score_v = _validator("score_event.schema.json")


def test_mock_signals_follow_contract():
    for sig in json.loads(MOCK.read_text(encoding="utf-8")):
        signal_v.validate(sig)


def test_onchain_collector_output_follows_contract():
    ts = "2023-03-11T02:00:00Z"
    signal_v.validate(to_price_signal("USDC", ts, 0.9812))
    signal_v.validate(to_peg_deviation_signal("USDC", ts, 0.9812))


def test_offchain_parser_output_follows_contract():
    for sig in to_reserve_signals("USDC", "2023-03-10T00:00:00Z", 0.2, 0.8):
        signal_v.validate(sig)


def test_engine_output_follows_contract():
    signals = json.loads(MOCK.read_text(encoding="utf-8"))
    score_v.validate(compute_risk_score(signals, coin="USDC"))


def test_engine_is_pure():
    """순수 함수 규칙 검증: 같은 입력이면 event_id 외 모든 값이 동일해야 한다."""
    signals = json.loads(MOCK.read_text(encoding="utf-8"))
    a = compute_risk_score(signals, coin="USDC")
    b = compute_risk_score(signals, coin="USDC")
    a.pop("event_id")
    b.pop("event_id")
    assert a == b


def test_usdc_crisis_mock_breaches_nothing_yet():
    """베이스라인 가중치 기준 스모크 테스트 — 역할 3이 모델 교체 시 갱신할 것."""
    signals = json.loads(MOCK.read_text(encoding="utf-8"))
    event = compute_risk_score(signals, coin="USDC")
    assert 0 <= event["risk_score"] <= 100


# ---------- 어댑터 계약 (통합 설계 4장) ----------

from src.adapters.threatwatch_sender import to_alert_request  # noqa: E402

alert_v = _validator("alert_request.schema.json")
CRISIS = Path("data/mock/signals_usdc_crisis.json")


def _crisis_event():
    signals = json.loads(CRISIS.read_text(encoding="utf-8"))
    return compute_risk_score(signals, coin="USDC")


def test_adapter_output_follows_threatwatch_contract():
    event = _crisis_event()
    assert event["threshold_breached"], "위기 mock은 임계값을 넘어야 함"
    alert_v.validate(to_alert_request(event))


def test_adapter_severity_mapping():
    event = _crisis_event()
    alert = to_alert_request(event)
    expected = "high" if event["risk_score"] >= 85 else "medium"
    assert alert["severity"] == expected
    assert alert["alert_id"] == event["event_id"]  # 멱등성 키 보존
    assert alert["incident_type"] == "stablecoin_depeg_risk_usdc"


def test_adapter_rejects_non_breached_event():
    signals = json.loads(MOCK.read_text(encoding="utf-8"))
    calm = compute_risk_score(signals, coin="USDC")
    assert not calm["threshold_breached"]
    with pytest.raises(ValueError):
        to_alert_request(calm)
