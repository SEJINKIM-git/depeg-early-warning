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


# ---- v2: 대시보드 tests/test_depeg_live.py 에서 옮겨 온 사례 (2026년 보관처 목록) ----

LIVE_2026 = counterparties_at("2026-11-11T00:00:00Z")["names"]


def _tier(title, names=LIVE_2026):
    c = classify(title, names)
    return c and c["tier"]


def test_dashboard_rubric_tiers():
    assert _tier("USDC loses peg after Circle reveals $3.3B stuck at SVB") == "A"
    assert _tier("Cross River Bank collapses as FDIC takes control") == "B"
    # 2026년 목록에는 SVB가 없다
    assert _tier("Silicon Valley Bank collapses as FDIC takes control") is None
    assert _tier("Circle's USDC moves to EBA supervision under MiCA") == "C"
    assert _tier("Bitcoin rallies past record high") is None
    assert _tier("BNY Mellon reports quarterly earnings") is None


def test_dashboard_news_flag_only_for_a_or_b():
    flag, matched = news_flag([{"title": "Circle's USDC moves to EBA supervision under MiCA"}], LIVE_2026)
    assert flag == 0 and matched[0]["tier"] == "C"
    flag, _ = news_flag([{"title": "Customers Bank halts withdrawals amid bank run"}], LIVE_2026)
    assert flag == 1


def test_dashboard_rss_title():
    assert _tier("USDC redemptions paused for EEA holders") == "A"


def test_dashboard_real_headlines_2026_11_11():
    assert _tier("Goldman, Citi Among Banks in $270 Million Stablecoin Backing") is None
    assert _tier("PNC Launches USDC Payments Pilot With Coinbase") is None
    assert _tier(
        "Crypto News Today: Waller's Rate-Hike Warning, MARA's $1.1B Bitcoin Sale and USDC's EU Deadline"
    ) == "C"


def test_dashboard_review_false_positives_are_not_alarms():
    assert _tier("Circle freezes $2M in USDC linked to Bybit exploit") == "C"
    assert _tier("Bitcoin price collapse sends traders into USDC") is None
    assert _tier("Trump's inner circle faces collapse after vote") is None
    assert _tier("USDC lending yields fall below 1%") is None
    assert _tier("USDC holds peg despite rumors of depeg") == "C"
    assert _tier("Two years after SVB collapse, regional banks recover") is None
    assert _tier("BlackRock bitcoin ETF fails to attract inflows") is None
    assert _tier("Cross River State bridge collapse kills three") is None
    assert _tier("BNY Mellon reports FDIC assessment charge") is None


def test_dashboard_review_misses_are_caught():
    assert _tier("USD Coin slips to 0.98 as traders rush to exit") == "A"
    assert _tier("Circle halts USDC minting after banking partner issue") == "A"
    assert _tier("BNY Mellon hit by bank run fears, withdrawals halted") == "B"


# ---- v2: 사전 등록 항목(docs/news_rubric_v2_changes.md)마다 통과 1 + 오탐 방지 1 ----

def test_a1_circle_needs_capital_and_stablecoin_context():
    assert _tier("Circle stablecoin issuer hit by bank run", DEPEG_WEEK) == "A"
    assert _tier("circle of crypto traders see bank run", DEPEG_WEEK) is None


def test_a2_lone_collapse_is_not_issuer_distress():
    assert _tier("USDC collapse wipes out holders") == "A"
    assert _tier("Bitcoin collapse pushes traders into USDC") is None


def test_a3_security_incidents_are_watch_only():
    assert _tier("USDC hacked funds blacklisted by Circle") == "C"
    assert _tier("Exchange hacked, $40M in ether stolen") is None


def test_a4_negation_rumor_retrospective_downgrade():
    assert _tier("Circle denies USDC insolvency rumors") == "C"
    assert _tier("USDC insolvency fears grow as redemptions halted") == "A"


def test_a5_fdic_alone_is_not_bank_distress():
    assert _tier("FDIC takes control of Customers Bank") == "B"
    assert _tier("Customers Bank meets with FDIC officials") is None


def test_a6_counterparty_aliases_are_strict():
    assert _tier("Cross River Bank fails") == "B"
    assert _tier("Cross River flooding fails levee") is None
    assert _tier("BlackRock fund collapses", counterparties_at("2023-01-01T00:00:00Z")["names"]) is None
    assert _tier("Circle Reserve Fund (USDXX) seized") == "B"


def test_b1_wind_down_liquidation():
    assert _tier("Silvergate announces intent to wind down operations", DEPEG_WEEK) == "B"
    assert _tier("Goldman to wind down consumer unit") is None  # 보관처 아님


def test_b2_shutter_closed_by_regulators_takes_possession():
    assert _tier("Silicon Valley Bank Shuttered by State Regulators", DEPEG_WEEK) == "B"
    assert _tier("California Financial Regulator Takes Possession of Silicon Valley Bank", DEPEG_WEEK) == "B"
    assert _tier("Silicon Valley Bank closed by California regulator", DEPEG_WEEK) == "B"
    assert _tier("Silicon Valley Bank closed for public holiday", DEPEG_WEEK) is None


def test_b3_conversions_paused():
    assert _tier("USDC conversions suspended at major exchange") == "A"
    assert _tier("Binance has temporarily suspended auto-conversion of USDC to BUSD") == "A"
    assert _tier("USDC conversions resume after weekend") is None


def test_b4_breaks_dollar_peg():
    assert _tier("Stablecoin USDC breaks dollar peg after SVB exposure") == "A"
    assert _tier("USDC breaks daily volume record") is None


def test_b5_share_price_plunge_percent():
    assert _tier("Shares of SVB Financial fall 60% as bank looks to raise cash", DEPEG_WEEK) == "B"
    assert _tier("SVB Financial shares rise 5%", DEPEG_WEEK) is None


def test_b6_advised_to_pull_money():
    assert _tier("Venture firms are advising portfolio companies to move money out of SVB", DEPEG_WEEK) == "B"
    assert _tier("Startups move money into SVB accounts", DEPEG_WEEK) is None


def test_b7_issuer_and_counterparty_with_exposure():
    assert _tier("Circle says $3.3 billion of USDC reserves are with Silicon Valley Bank", DEPEG_WEEK) == "B"
    # 제휴·사업 뉴스는 노출 표현이 없으므로 켜지지 않는다 (승인 때 확정한 조건)
    assert _tier("BNY Mellon named custodian for USDC reserves") is None


def test_b8_resolution_downgrades():
    assert _tier("$3.3 Billion of USDC Reserve Risk Removed, Dollar De-peg Closes") == "C"
    assert _tier("USDC regains dollar peg after weekend depeg") == "C"
    # 해소 표현이 없으면 그대로 A
    assert _tier("USDC Stablecoin Depegs From $1; Circle Says Operations Are Normal") == "A"


def test_rubric_version_is_v2():
    from src.intelligence.news_rubric import RUBRIC_VERSION
    assert RUBRIC_VERSION == "v2"
