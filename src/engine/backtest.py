"""가중치 후보 백테스트 — 전부 순수 함수 (파일 I/O는 scripts/backtest_weights.py).

규칙: 시각마다 그 시각의 값만 넣는다. 엔진은 지표별 최댓값을 쓰므로 과거 값을 섞으면 점수가 부풀려진다.
(ThreatWatch-AI scripts/build_depeg_replay.py 와 같은 규칙)
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from src.contracts import SIGNAL_SCHEMA_VERSION
from src.engine.risk_score import compute_risk_score

ALERT_LINE = 70.0      # 경보 (P2, 운영자 알림)
APPROVAL_LINE = 85.0   # 사람 승인 필요 (P1)
_TS = "%Y-%m-%dT%H:%M:%SZ"

# 시점별 공시 값 — docs/offchain_attestation_anatomy.md 4장의 손 검증값 (조정 반영 net 기준).
# public_from 은 발행일 당일의 마지막 초 (같은 문서 3-3절).
ATTESTATIONS: tuple[dict[str, Any], ...] = (
    {"report": "2022-11", "public_from": "2022-12-22T23:59:59Z", "cash_ratio": 0.2586, "tbill_ratio": 0.7414},
    {"report": "2022-12", "public_from": "2023-01-25T23:59:59Z", "cash_ratio": 0.2369, "tbill_ratio": 0.7631},
    {"report": "2023-01", "public_from": "2023-03-02T23:59:59Z", "cash_ratio": 0.2034, "tbill_ratio": 0.7966},
)


def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, _TS).replace(tzinfo=timezone.utc)


def hours_between(earlier: str, later: str) -> float:
    return (_parse(later) - _parse(earlier)).total_seconds() / 3600.0


def attestation_at(
    observed_at: str, reports: Sequence[Mapping[str, Any]] = ATTESTATIONS
) -> Mapping[str, Any] | None:
    """시각 t에 공개돼 있던 최신 보고서. 없으면 None."""
    public = [r for r in reports if r["public_from"] <= observed_at]
    return max(public, key=lambda r: r["public_from"]) if public else None


def attestation_signals_at(
    coin: str, observed_at: str, reports: Sequence[Mapping[str, Any]] = ATTESTATIONS
) -> list[dict[str, Any]]:
    """시각 t에 이미 공개돼 있던 공시만 Signal로 만든다 (미래 정보 차단)."""
    report = attestation_at(observed_at, reports)
    if report is None:
        return []
    pub = report["public_from"]
    age_days = round(hours_between(pub, observed_at) / 24.0, 2)
    base = {"schema_version": SIGNAL_SCHEMA_VERSION, "source": "offchain", "coin": coin}
    prefix = f"offchain-{coin.lower()}"
    return [
        {**base, "signal_id": f"{prefix}-{pub}-cash", "observed_at": pub,
         "metric": "reserve_cash_ratio", "value": report["cash_ratio"]},
        {**base, "signal_id": f"{prefix}-{pub}-tbill", "observed_at": pub,
         "metric": "reserve_tbill_ratio", "value": report["tbill_ratio"]},
        {**base, "signal_id": f"{prefix}-{observed_at}-age", "observed_at": observed_at,
         "metric": "attestation_age_days", "value": age_days},
    ]


def score_series(
    coin: str,
    price_signals: Sequence[Mapping[str, Any]],
    *,
    news_signals: Sequence[Mapping[str, Any]] = (),
    with_attestation: bool = True,
    weights: Mapping[str, float] | None = None,
    peg_full_scale_bps: float | None = None,
) -> list[dict[str, Any]]:
    """시각별 점수 [{t, bps, score, news}] — 시각마다 그 시각의 시그널만 엔진에 넣는다.

    news_signals 를 비우면 뉴스 없이(=0) 계산한다.
    """
    by_time: dict[str, list[Mapping[str, Any]]] = {}
    for s in price_signals:
        by_time.setdefault(s["observed_at"], []).append(s)
    news_at = {s["observed_at"]: s for s in news_signals}

    out = []
    for t in sorted(by_time):
        signals = list(by_time[t])
        if with_attestation:
            signals += attestation_signals_at(coin, t)
        news = news_at.get(t)
        if news is not None:
            signals.append(news)
        event = compute_risk_score(
            signals, coin,
            weights=dict(weights) if weights is not None else None,
            peg_full_scale_bps=peg_full_scale_bps,
        )
        bps = next(s["value"] for s in by_time[t] if s["metric"] == "peg_deviation_bps")
        out.append({
            "t": t, "bps": bps, "score": event["risk_score"],
            "news": int(news["value"]) if news is not None else None,
        })
    return out


def first_crossing(series: Sequence[Mapping[str, Any]], line: float) -> str | None:
    """점수가 기준선 이상이 된 첫 시각. 없으면 None."""
    return next((p["t"] for p in series if p["score"] >= line), None)


def hours_at_or_above(series: Sequence[Mapping[str, Any]], line: float) -> int:
    """기준선 이상인 시간 수 — 평시 구간에서는 오경보 수."""
    return sum(1 for p in series if p["score"] >= line)


def news_only_worst_case(
    coin: str,
    observed_at: str,
    *,
    weights: Mapping[str, float] | None = None,
    peg_full_scale_bps: float | None = None,
) -> float:
    """조건 3: 가격 정상(0bps) + 뉴스 1 + 공시가 낼 수 있는 최악값(현금 0, 경과일 90일 이상)의 점수."""
    base = {"schema_version": SIGNAL_SCHEMA_VERSION, "coin": coin, "observed_at": observed_at}
    signals = [
        {**base, "signal_id": "wc-price", "source": "onchain", "metric": "price_usd", "value": 1.0},
        {**base, "signal_id": "wc-pegdev", "source": "onchain", "metric": "peg_deviation_bps", "value": 0.0},
        {**base, "signal_id": "wc-news", "source": "offchain", "metric": "news_risk_flag", "value": 1},
        {**base, "signal_id": "wc-cash", "source": "offchain", "metric": "reserve_cash_ratio", "value": 0.0},
        {**base, "signal_id": "wc-age", "source": "offchain", "metric": "attestation_age_days", "value": 365.0},
    ]
    return compute_risk_score(
        signals, coin,
        weights=dict(weights) if weights is not None else None,
        peg_full_scale_bps=peg_full_scale_bps,
    )["risk_score"]


def _crossing(series: Sequence[Mapping[str, Any]], line: float, low_at: str, breach_at: str) -> dict[str, Any]:
    t = first_crossing(series, line)
    return {
        "first_at": t,
        "hours_before_low": hours_between(t, low_at) if t else None,
        "hours_before_minus_50bps": hours_between(t, breach_at) if t else None,
    }


def evaluate(
    coin: str,
    crisis_prices: Sequence[Mapping[str, Any]],
    calm_prices: Sequence[Mapping[str, Any]],
    news_signals: Sequence[Mapping[str, Any]],
    *,
    weights: Mapping[str, float] | None = None,
    peg_full_scale_bps: float | None = None,
) -> dict[str, Any]:
    """후보 하나의 백테스트 결과와 조건 1~4 통과 여부."""
    from src.engine.risk_score import _BASELINE_WEIGHTS  # 기본값 확인용

    opts = {"weights": weights, "peg_full_scale_bps": peg_full_scale_bps}
    crisis = score_series(coin, crisis_prices, news_signals=news_signals, **opts)
    price_only = score_series(coin, crisis_prices, with_attestation=False, **opts)
    no_news = score_series(coin, crisis_prices, **opts)
    calm = score_series(coin, calm_prices, **opts)

    low = min(crisis, key=lambda p: (p["bps"], p["t"]))
    breach_at = next(p["t"] for p in crisis if p["bps"] <= -50.0)
    news_only = news_only_worst_case(coin, crisis[0]["t"], **opts)
    weight_sum = round(sum((weights or _BASELINE_WEIGHTS).values()), 10)

    def lines(series: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        return {
            "max": max(p["score"] for p in series),
            "alert": _crossing(series, ALERT_LINE, low["t"], breach_at),
            "approval": _crossing(series, APPROVAL_LINE, low["t"], breach_at),
        }

    result = {
        "low_at": low["t"],
        "minus_50bps_at": breach_at,
        "crisis": lines(crisis),                 # 가격 + 공시 + 뉴스
        "crisis_price_attestation": lines(no_news),  # 가격 + 공시
        "crisis_price_only": lines(price_only),      # 가격만
        "crisis_hours_alert": hours_at_or_above(crisis, ALERT_LINE),
        "crisis_hours_approval": hours_at_or_above(crisis, APPROVAL_LINE),
        "calm_max": max(p["score"] for p in calm),
        "calm_false_alarms": hours_at_or_above(calm, ALERT_LINE),
        "calm_hours": len(calm),
        "news_only_worst_case": news_only,
        "weight_sum": weight_sum,
    }
    result["conditions"] = {
        "1_calm_never_70": result["calm_false_alarms"] == 0,
        "2_crisis_crosses_70_and_85": (
            result["crisis"]["alert"]["first_at"] is not None
            and result["crisis"]["approval"]["first_at"] is not None
        ),
        "3_news_alone_below_70": news_only < ALERT_LINE,
        "4_weights_sum_to_1": weight_sum == 1.0,
    }
    result["passes"] = all(result["conditions"].values())
    result["series"] = {"crisis": crisis, "crisis_price_only": price_only, "calm": calm}
    return result


# --- 사전 등록한 후보 (docs/weights_rationale.md 3장) ---------------------------------------------
_V1_WEIGHTS = {
    "peg_deviation_bps": 0.70,
    "news_risk_flag": 0.14,
    "redemption_volume_usd": 0.04,
    "pool_imbalance_ratio": 0.04,
    "reserve_cash_ratio": 0.04,
    "attestation_age_days": 0.04,
}
_K0_WEIGHTS = {
    "peg_deviation_bps": 0.5,
    "redemption_volume_usd": 0.2,
    "pool_imbalance_ratio": 0.1,
    "news_risk_flag": 0.1,
    "reserve_cash_ratio": 0.05,
    "attestation_age_days": 0.05,
}
_X1_WEIGHTS = {**_V1_WEIGHTS, "peg_deviation_bps": 0.50, "news_risk_flag": 0.34}

# selectable=True 인 것만 선택 대상이고, 순서가 곧 "단순한 순서"다 (3-5절 선택 규칙).
CANDIDATES: tuple[dict[str, Any], ...] = (
    {"name": "K0", "label": "현행 (비교용)", "selectable": False,
     "weights": _K0_WEIGHTS, "peg_full_scale_bps": 500.0},
    {"name": "K1", "label": "비중만 변경, 만점 500bps", "selectable": True,
     "weights": _V1_WEIGHTS, "peg_full_scale_bps": 500.0},
    {"name": "K2", "label": "비중 변경 + 만점 200bps", "selectable": True,
     "weights": _V1_WEIGHTS, "peg_full_scale_bps": 200.0},
    {"name": "K3", "label": "비중 변경 + 만점 100bps", "selectable": True,
     "weights": _V1_WEIGHTS, "peg_full_scale_bps": 100.0},
    {"name": "X1", "label": "뉴스 비중 큼 (원칙 1 위반, 비교용)", "selectable": False,
     "weights": _X1_WEIGHTS, "peg_full_scale_bps": 500.0},
)


def select(results: Mapping[str, Mapping[str, Any]]) -> str | None:
    """선택 규칙: 선택 대상 가운데 조건을 모두 통과한 첫 후보(가장 단순한 것)."""
    for c in CANDIDATES:
        if c["selectable"] and results[c["name"]]["passes"]:
            return c["name"]
    return None
