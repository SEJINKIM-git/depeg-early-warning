"""뉴스 기준표 v1 — 기사 제목을 정해진 규칙으로만 분류한다 (AI 판단 없음).

같은 제목 + 같은 보관처 목록에는 항상 같은 결과가 나와야 과거 데이터로 검증(백테스트)할 수 있다.
AI는 이 분류를 바꾸지 않고, 나중에 사람이 읽을 설명 문장만 쓴다.

v0(ThreatWatch-AI api/_depeg/news_rubric.py)에서 달라진 점은 하나다:
보관처 목록이 상수가 아니라 "시각 t에 공개돼 있던 최신 Circle 보고서의 은행 목록"이다.
(2023-03에 SVB 기사로 신호가 켜지려면, 그 시점에 SVB가 보관 은행이라고 공개돼 있었어야 한다.)
분류 패턴(ISSUER, ISSUER_DISTRESS, BANK_DISTRESS, WATCH_ONLY)은 v0 그대로다.

등급
  A  발행사·코인 자체의 위기   (USDC/Circle + 위기 표현)            → 신호 켜짐
  B  준비금을 맡은 곳의 위기   (보관 은행·펀드 + 금융 위기 표현)     → 신호 켜짐
  C  관찰만                     (USDC/Circle + 규제·감독 표현)       → 신호 꺼짐, 목록에만 표시

이 파일은 표준 라이브러리만 쓴다 (ThreatWatch-AI 대시보드로 그대로 복사된다).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

RUBRIC_VERSION = "v1"

# 발행사·코인
ISSUER = [r"USDC", r"USD Coin", r"Circle Internet", r"\bCircle\b"]

ISSUER_DISTRESS = [
    r"de-?peg", r"lost (its|the) peg", r"loses? peg", r"below \$?1\b", r"\$0\.9\d",
    r"redemptions? (halted|paused|suspended|delayed)", r"halts? redemptions?",
    r"bank run", r"insolven", r"collapse", r"frozen", r"exploit", r"hack(ed)?\b",
    r"reserve (shortfall|gap|exposure)", r"stuck at", r"trapped",
]

BANK_DISTRESS = [
    r"bank run", r"receivership", r"\bFDIC\b", r"insolven", r"collapse", r"fail(s|ed|ure)\b",
    r"shut(s)? down", r"seiz(e|ed|ure)", r"withdrawals? (halted|frozen|paused)",
    r"capital (raise|shortfall)", r"emergency (sale|funding)", r"liquidity crisis",
]

WATCH_ONLY = [
    r"\bMiCA\b", r"\bEBA\b", r"GENIUS Act", r"\bSEC\b", r"regulat", r"supervis",
    r"licen[cs]e", r"charter", r"\bEU\b", r"\bEEA\b", r"deadline", r"complian",
]

# 보고서에 인쇄된 기관 이름 → 기사 제목에서 찾을 표현.
# v0에 있던 표현은 그대로 두고, 보고서에만 있던 은행 2곳(Citizens Trust, NYCB/Flagstar)을 더했다.
# 여기에 없는 이름이 들어오면 이름 그대로(대소문자 무시) 찾는다.
COUNTERPARTY_ALIASES: dict[str, list[str]] = {
    "Bank of New York Mellon": [r"BNY Mellon", r"Bank of New York Mellon"],
    "Citizens Trust Bank": [r"Citizens Trust"],
    "Cross River Bank": [r"Cross River"],
    "Customers Bank": [r"Customers Bank"],
    "New York Community Bank": [r"New York Community Bank", r"\bNYCB\b", r"Flagstar"],
    "Signature Bank": [r"Signature Bank"],
    "Silicon Valley Bank": [r"Silicon Valley Bank", r"\bSVB\b"],
    "Silvergate Bank": [r"Silvergate"],
    "Circle Reserve Fund": [r"Circle Reserve Fund"],
    "BlackRock": [r"BlackRock"],
}

_FUND = "Circle Reserve Fund"
_BANKS_2022_2023 = (
    "Bank of New York Mellon", "Citizens Trust Bank", "Customers Bank",
    "New York Community Bank", "Signature Bank", "Silicon Valley Bank", "Silvergate Bank",
)
_BANKS_2023_03_31 = ("Bank of New York Mellon", "Cross River Bank", "Customers Bank")

# 보고서별 보관처 — docs/offchain_attestation_anatomy.md 0절(발행일)과 각 PDF의 현금 예치 은행 각주를
# 눈으로 옮긴 표. public_from 은 손 해부 3-3절 규칙(발행일 당일의 마지막 초)이다.
#   banks        : 그 보고서에 이름이 인쇄된 현금 예치 은행 (가장 늦은 기준일 기준)
#   others       : 보고서에 이름이 나온 펀드·운용사
#   banks_named  : False면 보고서가 은행 이름을 밝히지 않음 → 이름이 나온 가장 최근 목록을 이어 쓴다
REPORTS: tuple[dict[str, Any], ...] = (
    {"report": "2022-11", "public_from": "2022-12-22T23:59:59Z", "banks_named": True,
     "banks": _BANKS_2022_2023, "others": (_FUND, "BlackRock")},  # 각주 10
    {"report": "2022-12", "public_from": "2023-01-25T23:59:59Z", "banks_named": True,
     "banks": _BANKS_2022_2023, "others": (_FUND, "BlackRock")},  # 각주 10
    {"report": "2023-01", "public_from": "2023-03-02T23:59:59Z", "banks_named": True,
     "banks": _BANKS_2022_2023, "others": (_FUND,)},  # 각주 2 — 디페그 주간의 최신 보고서
    {"report": "2023-02", "public_from": "2023-03-30T23:59:59Z", "banks_named": True,
     "banks": _BANKS_2022_2023, "others": (_FUND,)},  # 각주 2
    {"report": "2023-03", "public_from": "2023-04-28T23:59:59Z", "banks_named": True,
     "banks": _BANKS_2023_03_31, "others": (_FUND,)},  # 각주 2, 03-31 기준 (03-06은 7곳)
    {"report": "2026-07", "public_from": "2026-08-27T23:59:59Z", "banks_named": False,
     "banks": (), "others": (_FUND,)},  # "regulated financial institutions"로만 표기
    {"report": "2026-08", "public_from": "2026-09-29T23:59:59Z", "banks_named": False,
     "banks": (), "others": (_FUND,)},
    {"report": "2026-09", "public_from": "2026-10-26T23:59:59Z", "banks_named": False,
     "banks": (), "others": (_FUND,)},
)


def counterparties_at(
    observed_at: str, reports: Sequence[Mapping[str, Any]] = REPORTS
) -> dict[str, Any]:
    """시각 t(초 단위 UTC Z 문자열)에 공개돼 있던 최신 보고서의 보관처 목록. 순수 함수.

    반환: {"report", "names", "banks_from"}. 공개된 보고서가 없으면 report=None, names=[].
    보고서가 은행 이름을 밝히지 않으면(2026년 양식) 이름이 나온 가장 최근 보고서의 은행 목록을
    이어 쓰고, 어느 보고서에서 왔는지 banks_from 에 남긴다.
    """
    public = sorted(
        (r for r in reports if r["public_from"] <= observed_at),
        key=lambda r: r["public_from"],
    )
    if not public:
        return {"report": None, "names": [], "banks_from": None}
    latest = public[-1]
    named = [r for r in public if r["banks_named"]]
    bank_source = latest if latest["banks_named"] else (named[-1] if named else None)
    banks = list(bank_source["banks"]) if bank_source else []
    return {
        "report": latest["report"],
        "names": banks + list(latest["others"]),
        "banks_from": bank_source["report"] if bank_source else None,
    }


def _hits(patterns: Iterable[str], text: str) -> list[str]:
    out = []
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            out.append(m.group(0))
    return out


def counterparty_patterns(counterparties: Iterable[str]) -> list[str]:
    """기관 이름 목록을 제목 검색용 표현 목록으로 바꾼다."""
    patterns: list[str] = []
    for name in counterparties:
        patterns.extend(COUNTERPARTY_ALIASES.get(name, [re.escape(name)]))
    return patterns


def classify(title: str, counterparties: Iterable[str]) -> dict[str, Any] | None:
    """기사 제목 하나를 분류한다. 해당 없음이면 None.

    counterparties: 그 시점에 공개돼 있던 보관처 이름 목록 (counterparties_at(t)["names"]).
    """
    issuer = _hits(ISSUER, title)
    party = _hits(counterparty_patterns(counterparties), title)

    if issuer:
        d = _hits(ISSUER_DISTRESS, title)
        if d:
            return {"tier": "A", "who": issuer[0], "why": d[0]}
    if party:
        d = _hits(BANK_DISTRESS, title)
        if d:
            return {"tier": "B", "who": party[0], "why": d[0]}
    if issuer:
        w = _hits(WATCH_ONLY, title)
        if w:
            return {"tier": "C", "who": issuer[0], "why": w[0]}
    return None


def news_flag(
    articles: Iterable[Mapping[str, Any]], counterparties: Iterable[str]
) -> tuple[int, list[dict[str, Any]]]:
    """기사 목록 → (news_risk_flag 0/1, 분류된 기사 목록). 순수 함수."""
    names = list(counterparties)
    matched = []
    for a in articles:
        c = classify(a.get("title", ""), names)
        if c:
            matched.append({**a, **c})
    order = {"A": 0, "B": 1, "C": 2}
    matched.sort(key=lambda m: m.get("seen", ""), reverse=True)  # 최신 먼저
    matched.sort(key=lambda m: order[m["tier"]])  # 그다음 등급 순 (안정 정렬)
    flag = 1 if any(m["tier"] in ("A", "B") for m in matched) else 0
    return flag, matched
