"""기사 입력 시각 정책(policy-2026-11-16) 테스트 — 올림, 뉴욕 날짜 끝, 판본 선택, 신호 반영."""
import json
import re
from pathlib import Path

import pytest

from scripts import apply_news_input_policy
from src.intelligence.news_input_policy import (
    POLICY_VERSION,
    RAW_PUBLISHED,
    TITLE_EDITIONS,
    apply_policy,
    ceil_to_second,
    choose_edition,
    ny_end_of_day_utc,
)
from src.intelligence.news_rubric import classify, counterparties_at
from src.intelligence.news_signal import articles_in_window, signal_time, to_news_signal

ARTICLES = json.loads(Path("data/historical/news_2023_handpicked.json").read_text(encoding="utf-8"))
NEWS = json.loads(Path("data/historical/signals_usdc_2023_news_hourly.json").read_text(encoding="utf-8"))


def row(number: int) -> dict:
    return ARTICLES[number - 1]


# --- 정책 2: 정수 초로 올림 ---------------------------------------------------

def test_fractional_seconds_round_up_to_next_second():
    assert ceil_to_second("2023-03-11T05:51:23.756Z") == "2023-03-11T05:51:24Z"
    assert ceil_to_second("2023-03-11T00:01:50.050Z") == "2023-03-11T00:01:51Z"
    assert ceil_to_second("2023-03-07T22:44:37.001Z") == "2023-03-07T22:44:38Z"


def test_whole_seconds_are_unchanged():
    assert ceil_to_second("2023-03-09T19:33:04Z") == "2023-03-09T19:33:04Z"
    assert ceil_to_second("2023-03-09T19:33:04.000Z") == "2023-03-09T19:33:04Z"


def test_round_up_carries_over_minute_hour_and_day():
    assert ceil_to_second("2023-03-10T23:59:59.500Z") == "2023-03-11T00:00:00Z"


def test_ceil_rejects_non_utc_or_malformed_input():
    for bad in ("2023-03-11T05:51:23", "2023-03-11T05:51:23+00:00", "2023-03-11T05:51:23.7x6Z", "2023-03-12"):
        with pytest.raises(ValueError):
            ceil_to_second(bad)


def test_all_twenty_raw_times_are_preserved_and_rounded_up():
    assert len(RAW_PUBLISHED) == 20  # 검증 문서 5-4절 19건 + #42
    for number, (_, raw, evidence_url) in RAW_PUBLISHED.items():
        assert row(number)["source_published_at"] == raw
        assert evidence_url.startswith("https://")
        if number not in TITLE_EDITIONS:
            assert row(number)["available_at"] == ceil_to_second(raw) > raw[:19] + "Z"


# --- 정책 3: 뉴욕 날짜 끝 -----------------------------------------------------

def test_new_york_end_of_day_respects_daylight_saving_start():
    # 서머타임은 2023-03-12 02:00(현지)에 시작 → 3/12의 끝은 EDT(UTC-4)
    assert ny_end_of_day_utc("2023-03-12") == "2023-03-13T04:00:00Z"
    # 하루 전은 끝나는 순간이 아직 EST(UTC-5)
    assert ny_end_of_day_utc("2023-03-11") == "2023-03-12T05:00:00Z"
    assert ny_end_of_day_utc("2023-01-15") == "2023-01-16T05:00:00Z"


def test_row_47_uses_new_york_end_of_day_and_records_the_assumption():
    r = row(47)
    assert r["published_at"] == r["source_published_at"] == "2023-03-12"
    assert r["available_at"] == "2023-03-13T04:00:00Z"
    assert r["available_basis"] == "date_only_ny_eod"
    assert "뉴욕" in r["time_assumption"]
    assert to_news_signal("USDC", "2023-03-13T04:00:00Z", [r])["value"] == 0
    assert to_news_signal("USDC", "2023-03-13T05:00:00Z", [r])["value"] == 1


# --- 정책 1: 제목 판본 ---------------------------------------------------------

def test_choose_edition_takes_earliest_confirmed_and_skips_unconfirmed():
    early = {"title": "a", "captured_at": "2023-03-09T19:44:13Z"}
    late = {"title": "b", "captured_at": "2023-03-09T22:14:41Z"}
    assert choose_edition([late, early]) == early
    assert choose_edition([{"title": "a", "captured_at": None}, late]) == late
    assert choose_edition([{"title": None, "captured_at": "2023-03-09T19:44:13Z"}]) is None
    assert choose_edition([]) is None


@pytest.mark.parametrize(
    ("number", "available_at", "title_start"),
    [
        (10, "2023-03-10T00:29:58Z", "SVB Drops Most on Record"),
        (11, "2023-03-09T19:44:13Z", "Shares of SVB Financial fall more than 50%"),
        (15, "2023-03-10T00:56:43Z", "Thiel Fund, Venture Firms Advise"),
        (24, "2023-03-10T16:48:12Z", "Silicon Valley Bank is shut down by regulators, FDIC to protect"),
        (41, "2023-03-11T07:10:31Z", "USDC Stablecoin and Crypto Market Go Haywire"),
    ],
)
def test_changed_title_rows_use_capture_time_of_the_confirmed_title(number, available_at, title_start):
    r = row(number)
    assert r["available_at"] == available_at
    assert r["available_basis"] == "archive_capture"
    assert r["title"].startswith(title_start)
    assert r["evidence_url"].startswith("https://web.archive.org/web/")
    assert r["available_at"] > r["published_at"]  # 원래 발행 시각은 그대로 남아 있다


def test_replaced_titles_keep_the_recorded_title():
    assert "60%" in row(11)["title_as_recorded"] and "60%" not in row(11)["title"]
    assert "title_as_recorded" in row(24) and "title_as_recorded" in row(41)
    assert "title_as_recorded" not in row(10) and "title_as_recorded" not in row(15)


def test_article_is_not_in_signal_before_its_capture_time():
    """발행 시각은 지났어도, 그 제목을 확인한 캡처 시각 전에는 신호에 들어가지 않는다."""
    r = row(15)  # 발행 03-09T20:53:52Z, 제목 확인 03-10T00:56:43Z, v2.1 B등급
    assert classify(r["title"], counterparties_at("2023-03-09T21:00:00Z")["names"])["tier"] == "B"
    for t in ("2023-03-09T21:00:00Z", "2023-03-09T23:00:00Z", "2023-03-10T00:00:00Z"):
        assert to_news_signal("USDC", t, [r])["value"] == 0
    assert to_news_signal("USDC", "2023-03-10T01:00:00Z", [r])["value"] == 1
    # 24시간 창도 캡처 시각에서 센다
    assert to_news_signal("USDC", "2023-03-11T00:00:00Z", [r])["value"] == 1
    assert to_news_signal("USDC", "2023-03-11T01:00:00Z", [r])["value"] == 0


def test_row_43_is_excluded_with_a_reason():
    r = row(43)
    assert r["excluded"] is True and r["available_at"] is None
    assert "제외" in r["exclusion_reason"]
    assert r["published_at"] == "2023-03-11T10:10:40Z"  # 원래 값은 지우지 않는다
    assert articles_in_window([r], "2023-03-11T12:00:00Z") == []
    for s in NEWS:
        assert all(e["url"] != r["url"] for e in s["meta"]["evidence"] + s["meta"]["watch"])


# --- available_at 우선 ---------------------------------------------------------

def test_available_at_wins_over_published_at_and_falls_back_when_missing():
    base = {"published_at": "2023-03-10T16:30:00Z", "title": "Silicon Valley Bank collapses"}
    assert signal_time(base) == "2023-03-10T16:30:00Z"
    assert signal_time({**base, "available_at": "2023-03-10T18:05:00Z"}) == "2023-03-10T18:05:00Z"
    assert signal_time({**base, "available_at": None}) == "2023-03-10T16:30:00Z"
    later = {**base, "available_at": "2023-03-10T18:05:00Z"}
    assert to_news_signal("USDC", "2023-03-10T18:00:00Z", [later])["value"] == 0
    assert to_news_signal("USDC", "2023-03-10T19:00:00Z", [later])["value"] == 1


# --- 표 전체 -------------------------------------------------------------------

def test_every_row_carries_policy_fields():
    for r in ARTICLES:
        assert r["input_policy"] == POLICY_VERSION
        assert r["evidence_url"].startswith("https://")
        assert "published_at" in r and "source_published_at" in r
        if r.get("excluded"):
            continue
        assert r["available_basis"] in {"published", "archive_capture", "date_only_ny_eod"}
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", r["available_at"])
        # 정책은 사용 시각을 늦추기만 한다
        assert r["available_at"] >= r["published_at"]
    assert sum(1 for r in ARTICLES if r.get("excluded")) == 1


def test_policy_is_idempotent_and_saved_table_is_current():
    assert apply_policy(ARTICLES) == ARTICLES
    assert apply_news_input_policy.main(["--check"]) == 0


def test_policy_refuses_to_run_on_reordered_rows():
    with pytest.raises(ValueError):
        apply_policy(list(reversed(ARTICLES)))


def test_saved_signals_record_rubric_and_policy_versions():
    assert {s["meta"]["rubric_version"] for s in NEWS} == {"v2.1"}
    assert {s["meta"]["input_policy"] for s in NEWS} == {POLICY_VERSION}


# --- 평시 표본 -----------------------------------------------------------------

def test_calm_sample_has_no_a_or_b_under_current_rubric():
    """docs/news_2023_calm_sample.md 본표 21건: A/B 0건, C 1건(#19)."""
    doc = Path("docs/news_2023_calm_sample.md").read_text(encoding="utf-8")
    table = doc.split("## 2. 본표 21건")[1].split("## 3.")[0]
    tiers = {}
    for line in table.splitlines():
        m = re.match(r"\| (\d+) \| (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})(?::(\d{2}))?[^|]*\| [^|]+\| \[(.+?)\]\(http", line)
        if m:
            t = f"{m.group(2)}T{m.group(3)}:{m.group(4) or '00'}Z"
            hit = classify(m.group(5), counterparties_at(t)["names"])
            tiers[int(m.group(1))] = hit["tier"] if hit else None
    assert len(tiers) == 21
    assert [n for n, tier in tiers.items() if tier in ("A", "B")] == []
    assert [n for n, tier in tiers.items() if tier == "C"] == [19]
