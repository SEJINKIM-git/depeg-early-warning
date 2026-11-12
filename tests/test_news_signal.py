"""시간별 뉴스 Signal 테스트 — 미래 정보 차단, 계약 검사, 저장된 2023 결과의 재현성."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from src.contracts import validate_signals
from src.intelligence import build_news_signals
from src.intelligence.news_signal import (
    articles_in_window,
    hourly_axis,
    hourly_news_signals,
    lead_time_summary,
    to_news_signal,
    usable_from,
)

SIGNAL_V = Draft202012Validator(
    json.loads(Path("schemas/signal.schema.json").read_text(encoding="utf-8")),
    format_checker=FormatChecker(),
)
HIST = Path("data/historical")
ARTICLES = json.loads((HIST / "news_2023_handpicked.json").read_text(encoding="utf-8"))
PRICES = json.loads((HIST / "signals_usdc_2023_depeg_hourly.json").read_text(encoding="utf-8"))
NEWS = json.loads((HIST / "signals_usdc_2023_news_hourly.json").read_text(encoding="utf-8"))

SVB = {
    "published_at": "2023-03-10T16:30:00Z",
    "outlet": "test",
    "title": "Silicon Valley Bank collapses as FDIC takes control",
    "url": "https://example.com/svb",
}


# --- 미래 정보 차단 ---------------------------------------------------------

def test_article_is_invisible_until_after_it_is_published():
    assert to_news_signal("USDC", "2023-03-10T16:00:00Z", [SVB])["value"] == 0
    # 발행 시각과 같은 정각에도 아직 보지 않는다 (t 이전 기사만)
    on_the_hour = {**SVB, "published_at": "2023-03-10T17:00:00Z"}
    assert to_news_signal("USDC", "2023-03-10T17:00:00Z", [on_the_hour])["value"] == 0
    assert to_news_signal("USDC", "2023-03-10T17:00:00Z", [SVB])["value"] == 1


def test_article_expires_after_24_hours():
    assert to_news_signal("USDC", "2023-03-11T16:00:00Z", [SVB])["value"] == 1
    assert to_news_signal("USDC", "2023-03-11T17:00:00Z", [SVB])["value"] == 0


def test_date_only_article_is_usable_from_next_day():
    assert usable_from("2023-03-10") == "2023-03-11T00:00:00Z"
    date_only = {**SVB, "published_at": "2023-03-10"}
    assert to_news_signal("USDC", "2023-03-11T00:00:00Z", [date_only])["value"] == 0
    assert to_news_signal("USDC", "2023-03-11T01:00:00Z", [date_only])["value"] == 1


def test_adding_future_articles_never_changes_past_signals():
    """t 이후 기사를 아무리 더해도 t까지의 신호는 바뀌지 않는다."""
    cutoff = "2023-03-10T12:00:00Z"
    axis = hourly_axis("2023-03-06T01:00:00Z", cutoff)
    past_only = [a for a in ARTICLES if usable_from(a["published_at"]) < cutoff]
    assert len(past_only) < len(ARTICLES)
    assert hourly_news_signals("USDC", axis, past_only) == hourly_news_signals("USDC", axis, ARTICLES)


def test_evidence_in_saved_signals_predates_observation():
    for s in NEWS:
        for e in s["meta"]["evidence"] + s["meta"]["watch"]:
            assert usable_from(e["published_at"]) < s["observed_at"]


def test_counterparty_list_is_as_of_observation_time():
    """SVB 기사라도, SVB가 공시에 나오기 전 시점에는 B 등급이 되지 않는다."""
    early = {**SVB, "published_at": "2022-12-20T10:00:00Z"}
    s = to_news_signal("USDC", "2022-12-20T12:00:00Z", [early])
    assert s["value"] == 0 and s["meta"]["counterparty_report"] is None


def test_window_bounds():
    got = articles_in_window(
        [
            {"published_at": "2023-03-09T11:59:59Z", "title": "old"},
            {"published_at": "2023-03-09T12:00:00Z", "title": "edge-in"},
            {"published_at": "2023-03-10T11:59:59Z", "title": "in"},
            {"published_at": "2023-03-10T12:00:00Z", "title": "edge-out"},
        ],
        "2023-03-10T12:00:00Z",
    )
    assert [a["title"] for a in got] == ["edge-in", "in"]


# --- 계약 검사 ---------------------------------------------------------------

def test_news_signals_follow_contract():
    validate_signals(NEWS, {1: SIGNAL_V})
    s = to_news_signal("USDC", "2023-03-10T17:00:00Z", [SVB])
    SIGNAL_V.validate(s)
    assert s["signal_id"] == "offchain-usdc-2023-03-10T17:00:00Z-news"
    assert s["source"] == "offchain" and s["metric"] == "news_risk_flag"
    assert s["meta"]["evidence"] == [
        {
            "title": SVB["title"], "outlet": "test", "published_at": SVB["published_at"],
            "tier": "B", "who": "Silicon Valley Bank", "why": "FDIC takes", "url": SVB["url"],
        }
    ]


def test_saved_news_file_shares_the_price_time_axis():
    price_axis = sorted({s["observed_at"] for s in PRICES})
    assert [s["observed_at"] for s in NEWS] == price_axis
    assert len({s["signal_id"] for s in NEWS}) == len(NEWS) == 120
    assert all(s["value"] in (0, 1) and s["metric"] == "news_risk_flag" for s in NEWS)


def test_saved_news_file_is_reproducible_from_handpicked_table():
    assert build_news_signals.main(["--check"]) == 0


# --- 손 정리 표 --------------------------------------------------------------

def test_handpicked_articles_are_well_formed():
    assert 30 <= len(ARTICLES) <= 60
    for a in ARTICLES:
        assert set(a) >= {"published_at", "outlet", "title", "url", "time_confidence", "note"}
        usable_from(a["published_at"])  # 형식이 틀리면 여기서 ValueError
        assert "2023-03-06" <= a["published_at"][:10] <= "2023-03-14"
        assert a["url"].startswith("https://")
    assert len({a["url"] for a in ARTICLES}) == len(ARTICLES)


def test_handpicked_doc_lists_every_article():
    doc = Path("docs/news_2023_handpicked.md").read_text(encoding="utf-8")
    for a in ARTICLES:
        assert a["url"] in doc, a["title"]


# --- 리드타임 ----------------------------------------------------------------

def test_lead_time_summary_price_side_matches_known_facts():
    scan = hourly_news_signals("USDC", hourly_axis("2023-03-06T01:00:00Z", "2023-03-14T00:00:00Z"), ARTICLES)
    summary = lead_time_summary(scan, PRICES)
    assert summary["price_first_breach"] == "2023-03-11T05:00:00Z"
    assert summary["price_low_at"] == "2023-03-11T08:00:00Z"
    assert summary["price_only_lead_hours"] == 3.0
    # 뉴스 신호는 가격이 -50bps를 넘기 전에 켜져 있어야 한다 (이 PR의 핵심 주장)
    assert summary["news_first_on"] is not None
    assert summary["news_first_on"] < summary["price_first_breach"]
    assert summary["news_first_evidence"]
