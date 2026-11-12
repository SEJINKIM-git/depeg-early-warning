"""뉴스 기준표 단위 테스트 — 같은 제목 + 같은 보관처 목록이면 항상 같은 등급."""
from src.intelligence.news_rubric import (
    REPORTS,
    classify,
    counterparties_at,
    news_flag,
)

DEPEG_WEEK = counterparties_at("2023-03-10T00:00:00Z")["names"]
NOV_2026 = counterparties_at("2026-11-11T07:00:00Z")["names"]


def test_rubric_tiers_v0_cases():
    """v0(ThreatWatch-AI tests/test_depeg_live.py)의 기대값이 그대로 유지된다."""
    assert classify("USDC loses peg after Circle reveals $3.3B stuck at SVB", DEPEG_WEEK)["tier"] == "A"
    assert classify("Silicon Valley Bank collapses as FDIC takes control", DEPEG_WEEK)["tier"] == "B"
    assert classify("Circle's USDC moves to EBA supervision under MiCA", DEPEG_WEEK)["tier"] == "C"
    assert classify("Bitcoin rallies past record high", DEPEG_WEEK) is None
    # 은행 이름만 있고 위기 표현이 없으면 해당 없음
    assert classify("BNY Mellon reports quarterly earnings", DEPEG_WEEK) is None


def test_news_flag_only_for_a_or_b():
    flag, matched = news_flag([{"title": "Circle's USDC moves to EBA supervision under MiCA"}], DEPEG_WEEK)
    assert flag == 0 and matched[0]["tier"] == "C"
    flag, _ = news_flag([{"title": "Silvergate halts withdrawals frozen amid bank run"}], DEPEG_WEEK)
    assert flag == 1


def test_real_headlines_from_2026_11_11():
    """2026-11-11 Google News 실제 제목 — 사업 뉴스는 무시, 규제 일정은 관찰, 위기 신호는 없음."""
    assert classify("Goldman, Citi Among Banks in $270 Million Stablecoin Backing", NOV_2026) is None
    assert classify("PNC Launches USDC Payments Pilot With Coinbase", NOV_2026) is None
    c = classify(
        "Crypto News Today: Waller's Rate-Hike Warning, MARA's $1.1B Bitcoin Sale and USDC's EU Deadline",
        NOV_2026,
    )
    assert c["tier"] == "C"
    assert news_flag([{"title": "PNC Launches USDC Payments Pilot With Coinbase"}], NOV_2026)[0] == 0


def test_bank_crisis_counts_only_if_bank_was_disclosed():
    """B 등급은 '그 시점 공시에 나온 은행'일 때만. 목록에 없는 은행의 위기는 신호가 아니다."""
    title = "Silicon Valley Bank collapses as FDIC takes control"
    assert classify(title, DEPEG_WEEK)["tier"] == "B"
    assert classify(title, []) is None
    assert classify(title, ["Bank of New York Mellon", "Cross River Bank"]) is None
    # 2023-03 보고서(04-28 발행) 이후에는 SVB가 목록에서 빠진다
    assert classify(title, counterparties_at("2023-05-01T00:00:00Z")["names"]) is None
    # 공시에 없던 은행
    assert classify("First Republic Bank seized by regulators", DEPEG_WEEK) is None


def test_same_input_same_output():
    title = "SVB Financial plunges after capital raise announcement"
    results = {str(classify(title, DEPEG_WEEK)) for _ in range(5)}
    assert len(results) == 1 and "'tier': 'B'" in results.pop()


def test_counterparties_follow_publication_dates():
    # 2022-11 보고서는 12-22 발행 → 그 전에는 공개된 보고서가 없다
    assert counterparties_at("2022-12-22T12:00:00Z") == {"report": None, "names": [], "banks_from": None}
    assert counterparties_at("2022-12-23T00:00:00Z")["report"] == "2022-11"
    # 디페그 주간: 2023-01 보고서(03-02 발행). 발행일 당일 낮에는 아직 이전 보고서
    assert counterparties_at("2023-03-02T12:00:00Z")["report"] == "2022-12"
    week = counterparties_at("2023-03-09T01:00:00Z")
    assert week["report"] == "2023-01"
    assert {"Silicon Valley Bank", "Signature Bank", "Silvergate Bank"} <= set(week["names"])
    assert len([n for n in week["names"] if n != "Circle Reserve Fund"]) == 7
    # 03-06 스냅샷이 든 2023-03 보고서는 04-28 발행 — 디페그 주간에 쓰면 미래 정보
    assert counterparties_at("2023-04-28T12:00:00Z")["report"] == "2023-02"
    after = counterparties_at("2023-04-29T00:00:00Z")
    assert after["report"] == "2023-03"
    assert "Silicon Valley Bank" not in after["names"] and "Cross River Bank" in after["names"]


def test_reports_without_bank_names_carry_forward_last_named_list():
    """2026년 양식은 은행 이름을 밝히지 않는다 → 이름이 나온 가장 최근 목록을 이어 쓰고 출처를 남긴다."""
    now = counterparties_at("2026-11-11T07:00:00Z")
    assert now["report"] == "2026-09" and now["banks_from"] == "2023-03"
    assert "Bank of New York Mellon" in now["names"] and "Circle Reserve Fund" in now["names"]
    assert classify("BNY Mellon placed into FDIC receivership", now["names"])["tier"] == "B"


def test_report_table_is_sorted_and_well_formed():
    dates = [r["public_from"] for r in REPORTS]
    assert dates == sorted(dates)
    assert all(r["banks"] or not r["banks_named"] for r in REPORTS)
