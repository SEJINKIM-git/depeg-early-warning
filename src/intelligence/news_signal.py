"""기사 목록 → 시간별 news_risk_flag Signal. 전부 순수 함수 (파일·네트워크 I/O 없음).

미래 정보 금지 규칙:
- 관측 시각 t의 신호는 [t-24h, t) 사이에 "쓸 수 있게 된" 기사만 본다. t 정각 이후 기사는 보지 않는다.
- 발행 시각이 날짜까지만 확인된 기사는 그 날짜의 다음 날 00:00Z부터 쓸 수 있다고 본다
  (하루 중 언제 나왔는지 모르므로 가장 늦은 쪽으로 가정 — 신호가 실제보다 일찍 켜지지 않는다).
- 보관처 목록도 t 시점에 공개돼 있던 보고서 것만 쓴다 (news_rubric.counterparties_at).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timedelta, timezone
from typing import Any

from src.contracts import SIGNAL_SCHEMA_VERSION
from src.intelligence.news_rubric import RUBRIC_VERSION, counterparties_at, news_flag

WINDOW_HOURS = 24
_TS = "%Y-%m-%dT%H:%M:%SZ"


def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, _TS).replace(tzinfo=timezone.utc)


def usable_from(published_at: str) -> str:
    """기사를 신호 계산에 쓸 수 있게 되는 가장 이른 시각 (초 단위 UTC Z)."""
    if len(published_at) == 10:  # YYYY-MM-DD — 시각 미확인
        day = datetime.strptime(published_at, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return (day + timedelta(days=1)).strftime(_TS)
    return _parse(published_at).strftime(_TS)  # 형식 검증 겸 정규화


def articles_in_window(
    articles: Iterable[Mapping[str, Any]], observed_at: str, window_hours: int = WINDOW_HOURS
) -> list[dict[str, Any]]:
    """t 이전 window_hours 동안 쓸 수 있게 된 기사만 고른다: t-window <= usable < t."""
    start = (_parse(observed_at) - timedelta(hours=window_hours)).strftime(_TS)
    out = []
    for a in articles:
        seen = usable_from(a["published_at"])
        if start <= seen < observed_at:
            out.append({**a, "seen": seen})
    return out


def _evidence(m: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "title": m["title"],
        "outlet": m.get("outlet", ""),
        "published_at": m["published_at"],
        "tier": m["tier"],
        "who": m["who"],
        "why": m["why"],
        "url": m.get("url", ""),
    }


def to_news_signal(
    coin: str, observed_at: str, articles: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    """관측 시각 t의 news_risk_flag Signal 하나를 만든다 (schemas/signal.schema.json)."""
    parties = counterparties_at(observed_at)
    flag, matched = news_flag(articles_in_window(articles, observed_at), parties["names"])
    return {
        "schema_version": SIGNAL_SCHEMA_VERSION,
        "signal_id": f"offchain-{coin.lower()}-{observed_at}-news",
        "source": "offchain",
        "coin": coin,
        "observed_at": observed_at,
        "metric": "news_risk_flag",
        "value": flag,
        "meta": {
            "rubric_version": RUBRIC_VERSION,
            "window_hours": WINDOW_HOURS,
            "counterparty_report": parties["report"],
            "counterparty_banks_from": parties["banks_from"],
            # 신호를 켠 근거(A·B)와 관찰만 하는 기사(C)를 나눠 적는다
            "evidence": [_evidence(m) for m in matched if m["tier"] in ("A", "B")],
            "watch": [_evidence(m) for m in matched if m["tier"] == "C"],
        },
    }


def hourly_news_signals(
    coin: str, observed_ats: Iterable[str], articles: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """주어진 시각 축의 각 t마다 Signal을 만든다."""
    return [to_news_signal(coin, t, articles) for t in observed_ats]


def hourly_axis(first: str, last: str) -> list[str]:
    """first부터 last까지(둘 다 포함) 1시간 간격 시각 목록."""
    t, end = _parse(first), _parse(last)
    out = []
    while t <= end:
        out.append(t.strftime(_TS))
        t += timedelta(hours=1)
    return out


def first_time(signals: Iterable[Mapping[str, Any]], metric: str, predicate) -> str | None:
    """metric 값이 조건을 처음 만족한 observed_at. 없으면 None."""
    times = sorted(
        s["observed_at"] for s in signals if s["metric"] == metric and predicate(s["value"])
    )
    return times[0] if times else None


def hours_between(earlier: str, later: str) -> float:
    return (_parse(later) - _parse(earlier)).total_seconds() / 3600.0


def on_segments(signals: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """신호가 연속으로 켜져 있던 구간 목록 [{"from", "to"}] (둘 다 켜져 있던 시각, 포함)."""
    segments: list[dict[str, str]] = []
    open_from = last_on = None
    for s in sorted(signals, key=lambda s: s["observed_at"]):
        if s["value"] >= 1:
            open_from = open_from or s["observed_at"]
            last_on = s["observed_at"]
        elif open_from:
            segments.append({"from": open_from, "to": last_on})
            open_from = None
    if open_from:
        segments.append({"from": open_from, "to": last_on})
    return segments


def first_on_by(signals: Sequence[Mapping[str, Any]], key: str) -> dict[str, str]:
    """근거 기사의 key("tier" 또는 "who") 값별로, 그 근거가 처음 신호에 잡힌 시각."""
    first: dict[str, str] = {}
    for s in sorted(signals, key=lambda s: s["observed_at"]):
        for e in s["meta"]["evidence"]:
            first.setdefault(e[key], s["observed_at"])
    return first


def lead_time_summary(
    news_signals: Sequence[Mapping[str, Any]],
    price_signals: Sequence[Mapping[str, Any]],
    breach_bps: float = -50.0,
) -> dict[str, Any]:
    """뉴스 신호가 처음 켜진 시각과 가격 기준 시각들의 차이(시간)를 계산한다."""
    pegdev = [s for s in price_signals if s["metric"] == "peg_deviation_bps"]
    low = min(pegdev, key=lambda s: (s["value"], s["observed_at"]))
    breach_at = first_time(pegdev, "peg_deviation_bps", lambda v: v <= breach_bps)
    news_on = first_time(news_signals, "news_risk_flag", lambda v: v >= 1)
    first = next((s for s in news_signals if s["observed_at"] == news_on), None)
    segments = on_segments(news_signals)
    # 가격 이탈 시점에 켜져 있던 연속 구간의 시작 — "끊기지 않고 켜져 있던" 리드타임
    streak = next((g["from"] for g in segments if g["from"] <= breach_at <= g["to"]), None)
    return {
        "on_segments": segments,
        "streak_start": streak,
        "streak_lead_before_breach_hours": hours_between(streak, breach_at) if streak else None,
        "first_on_by_tier": first_on_by(news_signals, "tier"),
        "first_on_by_who": first_on_by(news_signals, "who"),
        "news_first_on": news_on,
        "news_first_evidence": first["meta"]["evidence"] if first else [],
        "price_breach_bps": breach_bps,
        "price_first_breach": breach_at,
        "price_low_at": low["observed_at"],
        "price_low_bps": low["value"],
        "price_only_lead_hours": hours_between(breach_at, low["observed_at"]),
        "news_lead_before_breach_hours": hours_between(news_on, breach_at) if news_on else None,
        "news_lead_before_low_hours": (
            hours_between(news_on, low["observed_at"]) if news_on else None
        ),
    }
