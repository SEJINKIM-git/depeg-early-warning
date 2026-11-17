"""가중치 v1 통과 조건 1~4를 고정한다 (docs/weights_rationale.md 2장).

엔진의 비중이나 만점 지점을 바꾸면 이 테스트가 조건을 다시 검사한다.
"""
import json
from pathlib import Path

import pytest

from src.engine import risk_score
from src.engine.backtest import (
    ALERT_LINE,
    APPROVAL_LINE,
    CANDIDATES,
    attestation_at,
    attestation_signals_at,
    evaluate,
    first_crossing,
    hours_at_or_above,
    news_only_worst_case,
    score_series,
    select,
)

HIST = Path("data/historical")
CRISIS = json.loads((HIST / "signals_usdc_2023_depeg_hourly.json").read_text(encoding="utf-8"))
CALM = json.loads((HIST / "signals_usdc_2023_calm_hourly.json").read_text(encoding="utf-8"))
NEWS = json.loads((HIST / "signals_usdc_2023_news_hourly.json").read_text(encoding="utf-8"))
LOW_AT = "2023-03-11T08:00:00Z"


@pytest.fixture(scope="module")
def current():
    """지금 엔진 기본값(비중·만점 지점)으로 돌린 결과."""
    return evaluate("USDC", CRISIS, CALM, NEWS)


# --- 조건 1: 평상시 4주에 70점을 한 번도 넘지 않는다 --------------------------

def test_condition_1_calm_four_weeks_never_reach_70(current):
    assert current["calm_hours"] == 672
    assert current["calm_false_alarms"] == 0
    assert current["calm_max"] < ALERT_LINE / 2  # 아슬아슬하게 통과하는 것이 아님


def test_condition_1_holds_even_if_news_were_on_all_through_the_calm_weeks():
    """평시 뉴스 파일이 없어 뉴스=0으로 계산한다. 뉴스가 4주 내내 켜져 있었더라도 70 미만인지 확인."""
    always_on = [
        {"schema_version": 1, "signal_id": f"x-{t}", "source": "offchain", "coin": "USDC",
         "observed_at": t, "metric": "news_risk_flag", "value": 1}
        for t in sorted({s["observed_at"] for s in CALM})
    ]
    series = score_series("USDC", CALM, news_signals=always_on)
    assert hours_at_or_above(series, ALERT_LINE) == 0


# --- 조건 2: 사태에서 70점과 85점을 둘 다 넘는다 ------------------------------

def test_condition_2_crisis_crosses_both_lines(current):
    alert, approval = current["crisis"]["alert"], current["crisis"]["approval"]
    assert alert["first_at"] == "2023-03-11T06:00:00Z"
    assert approval["first_at"] == "2023-03-11T06:00:00Z"
    assert alert["hours_before_low"] == approval["hours_before_low"] == 2.0
    # −50bps 를 처음 넘은 05:00 보다 한 시간 늦다 (음수 = 뒤)
    assert alert["hours_before_minus_50bps"] == -1.0
    assert current["low_at"] == LOW_AT and current["minus_50bps_at"] == "2023-03-11T05:00:00Z"
    assert current["crisis"]["max"] >= APPROVAL_LINE


def test_before_the_price_moves_the_score_stays_below_70(current):
    """뉴스 신호는 36시간 전부터 켜져 있지만, 가격이 움직이기 전에는 경보가 나가지 않는다."""
    before = [p for p in current["series"]["crisis"] if p["t"] < "2023-03-11T05:00:00Z"]
    assert all(p["news"] == 1 for p in before)
    assert max(p["score"] for p in before) < 25


# --- 조건 3: 뉴스 신호 하나만으로는 70점을 넘지 않는다 ------------------------

def test_condition_3_news_alone_stays_below_70(current):
    assert current["news_only_worst_case"] < ALERT_LINE
    assert news_only_worst_case("USDC", "2023-03-10T00:00:00Z") == pytest.approx(22.0)


def test_condition_3_holds_with_every_non_price_signal_at_maximum():
    """가격만 정상이면, 나머지 다섯 항목이 전부 최대여도 70 미만이다."""
    base = {"schema_version": 1, "coin": "USDC", "observed_at": "2023-03-10T00:00:00Z", "source": "offchain"}
    signals = [
        {**base, "signal_id": "p", "source": "onchain", "metric": "peg_deviation_bps", "value": 0.0},
        {**base, "signal_id": "n", "metric": "news_risk_flag", "value": 1},
        {**base, "signal_id": "c", "metric": "reserve_cash_ratio", "value": 0.0},
        {**base, "signal_id": "a", "metric": "attestation_age_days", "value": 365.0},
        {**base, "signal_id": "r", "source": "onchain", "metric": "redemption_volume_usd", "value": 9e12},
        {**base, "signal_id": "l", "source": "onchain", "metric": "pool_imbalance_ratio", "value": 1.0},
    ]
    assert risk_score.compute_risk_score(signals, "USDC")["risk_score"] == pytest.approx(30.0)


# --- 조건 4: 비중 합 = 1 -------------------------------------------------------

def test_condition_4_weights_sum_to_one(current):
    weights = risk_score._BASELINE_WEIGHTS
    assert sum(weights.values()) == pytest.approx(1.0)
    assert current["weight_sum"] == 1.0
    assert all(w > 0 for w in weights.values())  # 상환·유동성을 0으로 지우지 않는다
    assert set(weights) == {
        "peg_deviation_bps", "news_risk_flag", "redemption_volume_usd",
        "pool_imbalance_ratio", "reserve_cash_ratio", "attestation_age_days",
    }


def test_all_four_conditions_pass_with_current_engine(current):
    assert current["conditions"] == {
        "1_calm_never_70": True,
        "2_crisis_crosses_70_and_85": True,
        "3_news_alone_below_70": True,
        "4_weights_sum_to_1": True,
    }
    assert risk_score.RISK_THRESHOLD == ALERT_LINE == 70.0  # 기준선은 바꾸지 않는다


# --- 원칙 1: 근거 하나로는 85점까지 가지 않는다 --------------------------------

def test_price_alone_reaches_70_but_never_85(current):
    assert current["crisis_price_only"]["alert"]["first_at"] == "2023-03-11T06:00:00Z"
    assert current["crisis_price_only"]["approval"]["first_at"] is None
    assert current["crisis_price_attestation"]["approval"]["first_at"] is None
    assert current["crisis_price_attestation"]["max"] < APPROVAL_LINE


def test_price_alone_at_full_scale_is_exactly_the_alert_line():
    signal = {"schema_version": 1, "signal_id": "p", "source": "onchain", "coin": "USDC",
              "observed_at": "2023-03-11T08:00:00Z", "metric": "peg_deviation_bps", "value": -500.0}
    event = risk_score.compute_risk_score([signal], "USDC")
    assert event["risk_score"] == 70.0 and event["threshold_breached"]
    just_under = risk_score.compute_risk_score([{**signal, "value": -499.0}], "USDC")
    assert not just_under["threshold_breached"]


# --- 선택 규칙과 후보 ----------------------------------------------------------

def test_engine_defaults_are_the_selected_candidate():
    results = {
        c["name"]: evaluate("USDC", CRISIS, CALM, NEWS,
                            weights=c["weights"], peg_full_scale_bps=c["peg_full_scale_bps"])
        for c in CANDIDATES
    }
    chosen = select(results)
    assert chosen == "K1"
    selected = next(c for c in CANDIDATES if c["name"] == chosen)
    assert risk_score._BASELINE_WEIGHTS == selected["weights"]
    assert risk_score.PEG_FULL_SCALE_BPS == selected["peg_full_scale_bps"]
    assert not results["K0"]["passes"]  # 현행은 조건 2에서 탈락
    assert results["K0"]["crisis"]["max"] == 64.5


def test_overrides_do_not_leak_into_the_default_engine():
    before = dict(risk_score._BASELINE_WEIGHTS)
    evaluate("USDC", CRISIS, CALM, NEWS, weights=CANDIDATES[0]["weights"], peg_full_scale_bps=100.0)
    assert risk_score._BASELINE_WEIGHTS == before
    assert evaluate("USDC", CRISIS, CALM, NEWS)["crisis"]["max"] == pytest.approx(87.6)


# --- 백테스트 규칙: 그 시각의 값만 ---------------------------------------------

def test_attestation_is_the_latest_report_public_at_that_time():
    assert attestation_at("2022-12-22T12:00:00Z") is None
    assert attestation_at("2023-01-15T01:00:00Z")["report"] == "2022-11"
    assert attestation_at("2023-01-25T23:00:00Z")["report"] == "2022-11"
    assert attestation_at("2023-01-26T00:00:00Z")["report"] == "2022-12"
    assert attestation_at("2023-03-11T08:00:00Z")["report"] == "2023-01"
    signals = {s["metric"]: s["value"] for s in attestation_signals_at("USDC", "2023-03-11T08:00:00Z")}
    assert signals["reserve_cash_ratio"] == 0.2034
    assert signals["attestation_age_days"] == pytest.approx(8.33, abs=0.01)


def test_each_hour_is_scored_from_that_hours_values_only(current):
    """최저점을 지난 뒤 점수가 내려온다 — 과거 최댓값이 섞였다면 내려오지 않는다."""
    series = current["series"]["crisis"]
    by_t = {p["t"]: p for p in series}
    assert by_t["2023-03-12T04:00:00Z"]["score"] < ALERT_LINE < by_t[LOW_AT]["score"]
    assert first_crossing(series, ALERT_LINE) == "2023-03-11T06:00:00Z"
    assert len(series) == 120
