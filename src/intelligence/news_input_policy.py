"""2023-03 기사 입력 시각 정책 (policy-2026-11-16). 전부 순수 함수 — 파일 I/O는 scripts/apply_news_input_policy.py.

확정된 정책 (세진, 2026-11-16):
1. 제목이 바뀐 기사는 "안 A": 그 제목을 직접 확인한 가장 이른 보관본 캡처 시각부터 쓴다.
   제목과 시각이 함께 확인된 판본이 없으면 제외한다. 판본이 여러 개여도 가장 이른 1행만 쓴다.
2. 초 아래 단위: 원래 값은 source_published_at 에 문자열 그대로 두고, 신호에는 정수 초로 올린 값을 쓴다.
3. 날짜만 있는 기사: 뉴욕 현지 그날의 끝(다음 날 00:00 뉴욕 시각)부터 쓴다.

행 번호는 data/historical/news_2023_handpicked.json 의 순서(1부터)이고 docs/news_2023_handpicked.md 표의 #와 같다.
행이 밀려도 엉뚱한 기사에 적용되지 않도록 각 항목에 URL 일부(url_has)를 함께 적고 적용할 때 대조한다.
값과 근거 URL은 docs/news_2023_verification.md 3장·5-4절, docs/news_2023_corrections_proposed.md 2~4장에서 손으로 옮겼다.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

POLICY_VERSION = "policy-2026-11-16"
_TS = "%Y-%m-%dT%H:%M:%SZ"
_NEW_YORK = ZoneInfo("America/New_York")
_ARCHIVE = "https://web.archive.org/web/"

# --- 정책 2: 확인한 원시 발행 시각 (검증 문서 5-4절 19건 + #42) -------------------------------
# 행 번호: (url_has, 원시 시각, 근거 URL)
RAW_PUBLISHED: dict[int, tuple[str, str, str]] = {
    1: ("silvergate-in-talks-with-fdic", "2023-03-07T22:44:37.431Z",
        _ARCHIVE + "20230308014111id_/https://www.bloomberg.com/news/articles/2023-03-07/silvergate-in-talks-with-fdic-officials-on-ways-to-salvage-bank"),
    6: ("silvergate-announces-voluntary-liquidation", "2023-03-08T21:41:13.841Z",
        _ARCHIVE + "20230308223442id_/https://www.coindesk.com/policy/2023/03/08/crypto-bank-silvergate-announces-voluntary-liquidation/"),
    7: ("no-exposure-to-shuttered-silvergate", "2023-03-09T03:49:15.898Z",
        _ARCHIVE + "20230310165725id_/https://www.coindesk.com/business/2023/03/09/crypto-stakeholders-say-no-exposure-to-shuttered-silvergate/"),
    8: ("circle-ceo-jeremy-allaire", "2023-03-09T10:00:36.436Z",
        _ARCHIVE + "20230309195802id_/https://www.bloomberg.com/news/articles/2023-03-09/circle-ceo-jeremy-allaire-on-us-crypto-regulation-stablecoins-usdc"),
    10: ("svb-plunges-most-since-1998", "2023-03-09T16:08:06.143Z",
         _ARCHIVE + "20230310002958id_/https://www.bloomberg.com/news/articles/2023-03-09/svb-plunges-most-since-1998-on-stock-offering-securities-sales?cmpId=google"),
    13: ("makerdao-founder-calls-for-rebranding", "2023-03-09T20:14:01.808Z",
         _ARCHIVE + "20230311145327id_/https://www.coindesk.com/business/2023/03/09/makerdao-founder-calls-for-rebranding-of-dai-stablecoin/"),
    15: ("svb-ceo-becker-asks", "2023-03-09T20:53:52.443Z",
         _ARCHIVE + "20230310005643id_/https://www.bloomberg.com/news/articles/2023-03-09/svb-ceo-becker-asks-silicon-valley-bank-clients-to-stay-calm"),
    16: ("voyager-continues-liquidating", "2023-03-09T21:39:47.143Z",
         _ARCHIVE + "20230310002300id_/https://www.coindesk.com/business/2023/03/09/voyager-continues-liquidating-crypto-assets-for-circles-usdc-stablecoin/"),
    17: ("founders-fund-advises-companies", "2023-03-09T22:11:27.741Z",
         _ARCHIVE + "20230309223412id_/https://www.bloomberg.com/news/articles/2023-03-09/founders-fund-advises-companies-to-withdraw-money-from-svb"),
    20: ("irishtimes.com", "2023-03-10T10:29:41.969Z",
         "https://www.irishtimes.com/business/financial-services/2023/03/10/startup-world-spooked-as-silicon-valley-bank-races-to-prevent-bank-run/"),
    33: ("usdc-stablecoin-depegs-from-1", "2023-03-11T00:01:50.050Z",
         _ARCHIVE + "20230311002915id_/https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-depegs-from-1-circle-says-operations-are-normal/"),
    # SNS 4건(#35·36·38·45)의 밀리초는 게시글 ID에서 계산한 생성 시각이다: (ID >> 22) + 1288834974657 ms
    35: ("1634361554543030273", "2023-03-11T01:12:14.229Z", "https://x.com/binance/status/1634361554543030273"),
    36: ("1634391505988206592", "2023-03-11T03:11:15.210Z", "https://x.com/circle/status/1634391505988206592"),
    38: ("1634399032767307776", "2023-03-11T03:41:09.734Z", "https://x.com/coinbase/status/1634399032767307776"),
    41: ("go-haywire-after-silicon-valley-bank", "2023-03-11T05:51:23.756Z",
         _ARCHIVE + "20230311071031id_/https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-and-crypto-market-go-haywire-after-silicon-valley-bank-collapses/"),
    # #42 Reuters: 초기 판본의 published_time 은 07:25:40Z, 후판 내부 값은 07:26:23.713Z.
    # 원표(07:26:23Z)가 따온 후판 값을 원시값으로 두고 올린다 — 둘 중 늦은 쪽이라 신호가 앞당겨지지 않는다.
    42: ("crypto-firm-circle-reveals-33-bln", "2023-03-11T07:26:23.713Z",
         _ARCHIVE + "20230311080308id_/https://www.reuters.com/business/crypto-firm-circle-reveals-33-bln-exposure-silicon-valley-bank-2023-03-11/"),
    45: ("1634649346535833601", "2023-03-11T20:15:49.187Z", "https://x.com/jerallaire/status/1634649346535833601"),
    46: ("circle-to-cover-any-shortfall", "2023-03-11T20:58:36.640Z",
         _ARCHIVE + "20230312012118id_/https://www.coindesk.com/business/2023/03/11/circle-to-cover-any-shortfall-in-usdc-reserves-sparking-stablecoin-rally/"),
    50: ("signature-bank-shut-down-by-state-regulators", "2023-03-12T22:25:41.430Z",
         _ARCHIVE + "20230312224421id_/https://www.coindesk.com/policy/2023/03/12/crypto-friendly-signature-bank-shut-down-by-state-regulators-fed/"),
    54: ("circle-scrambles-to-right-usdc", "2023-03-13T01:55:18.818Z",
         _ARCHIVE + "20230313174111id_/https://www.coindesk.com/policy/2023/03/12/circle-scrambles-to-right-usdc-after-signature-bank-failure/"),
}

# --- 정책 1: 제목이 바뀐 기사의 판본 (정정 제안 문서 2·3장) -------------------------------------
# 판본마다 {title, captured_at, evidence_url}. 제목이나 캡처 시각이 None 이면 "확인되지 않은 판본"이다.
# 후판(예: #11의 60% 제목, 22:14:41Z)은 정정 제안 문서에만 두고 여기에는 넣지 않는다.
TITLE_EDITIONS: dict[int, dict[str, Any]] = {
    10: {"url_has": "svb-plunges-most-since-1998", "editions": [{
        "title": "SVB Drops Most on Record as Startup Clients Face Cash Crunch",
        "captured_at": "2023-03-10T00:29:58Z",
        "evidence_url": _ARCHIVE + "20230310002958id_/https://www.bloomberg.com/news/articles/2023-03-09/svb-plunges-most-since-1998-on-stock-offering-securities-sales?cmpId=google"}]},
    11: {"url_has": "svb-financial-falls-more-than-50percent", "editions": [{
        "title": "Shares of SVB Financial fall more than 50% as tech-focused bank looks to raise more cash",
        "captured_at": "2023-03-09T19:44:13Z",
        "evidence_url": _ARCHIVE + "20230309194413id_/https://www.cnbc.com/2023/03/09/svb-financial-falls-more-than-50percent-as-tech-bank-looks-to-raise-more-cash.html"}]},
    15: {"url_has": "svb-ceo-becker-asks", "editions": [{
        "title": "Thiel Fund, Venture Firms Advise Companies to Pull Money From SVB",
        "captured_at": "2023-03-10T00:56:43Z",
        "evidence_url": _ARCHIVE + "20230310005643id_/https://www.bloomberg.com/news/articles/2023-03-09/svb-ceo-becker-asks-silicon-valley-bank-clients-to-stay-calm"}]},
    24: {"url_has": "silicon-valley-bank-is-shut-down-by-regulators", "editions": [{
        "title": "Silicon Valley Bank is shut down by regulators, FDIC to protect insured deposits",
        "captured_at": "2023-03-10T16:48:12Z",
        "evidence_url": _ARCHIVE + "20230310164812id_/https://www.cnbc.com/2023/03/10/silicon-valley-bank-is-shut-down-by-regulators-fdic-to-protect-insured-deposits.html"}]},
    41: {"url_has": "go-haywire-after-silicon-valley-bank", "editions": [{
        "title": "USDC Stablecoin and Crypto Market Go Haywire After Silicon Valley Bank Collapses",
        "captured_at": "2023-03-11T07:10:31Z",
        "evidence_url": _ARCHIVE + "20230311071031id_/https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-and-crypto-market-go-haywire-after-silicon-valley-bank-collapses/"}]},
    # #43 The Block: 기사 하단 정정 문구로 제목에서 DAI가 빠진 사실만 확인됐다.
    # 최초 제목 전체와 그 공개 시각, 현재 제목이 처음 보인 시각 모두 확인된 판본이 없다.
    43: {"url_has": "remain-at-about-0-90", "editions": [{
        "title": None, "captured_at": None,
        "evidence_url": "https://www.theblock.co/news/markets/2023-03-11-usdc-and-dai-remain-at-about-0-90-following-circles-disclosure-of-funds-at-svb-218993"}],
        "exclusion_reason": "제목이 발행 뒤 정정됨(DAI 삭제). 제목과 시각이 함께 확인된 판본이 없어 제외 (정책 1)"},
}

# --- 정책 3: 날짜만 있는 기사 (검증 문서 5-3절) --------------------------------------------------
DATE_ONLY: dict[int, dict[str, str]] = {
    47: {"url_has": "dfs.ny.gov",
         "evidence_url": _ARCHIVE + "20240113192024id_/https://www.dfs.ny.gov/reports_and_publications/press_releases/pr20230312",
         "time_assumption": "발행 날짜(2023-03-12)를 뉴욕 현지 날짜로 보고 그날의 끝(03-13 00:00 EDT = 04:00Z)부터 사용. "
                            "실제 공개 시각을 확인한 값이 아님"},
}


_FIELD_ORDER = (
    "published_at", "source_published_at", "available_at", "available_basis", "time_assumption",
    "outlet", "title", "title_as_recorded", "url", "evidence_url", "time_confidence",
    "excluded", "exclusion_reason", "input_policy", "note",
)


def ceil_to_second(raw: str) -> str:
    """원시 UTC 시각 문자열('…SS.fffZ' 또는 '…SSZ')을 정수 초로 올린다. 정수 초는 그대로."""
    if not raw.endswith("Z"):
        raise ValueError(f"UTC Z 시각이 아님: {raw!r}")
    whole, _, fraction = raw[:-1].partition(".")
    base = datetime.strptime(whole, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    if fraction:
        if not fraction.isdigit():
            raise ValueError(f"초 아래 단위를 읽을 수 없음: {raw!r}")
        base += timedelta(seconds=math.ceil(int(fraction) / 10 ** len(fraction)))
    return base.strftime(_TS)


def ny_end_of_day_utc(date: str) -> str:
    """뉴욕 현지 날짜 'YYYY-MM-DD'의 끝(다음 날 00:00 뉴욕 시각)을 UTC로. 서머타임을 반영한다."""
    day = datetime.strptime(date, "%Y-%m-%d")
    end_local = (day + timedelta(days=1)).replace(tzinfo=_NEW_YORK)
    return end_local.astimezone(timezone.utc).strftime(_TS)


def choose_edition(editions: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    """제목과 캡처 시각이 함께 확인된 판본 중 가장 이른 것. 없으면 None(제외)."""
    confirmed = [e for e in editions if e.get("title") and e.get("captured_at")]
    return min(confirmed, key=lambda e: e["captured_at"]) if confirmed else None


def _check_row(number: int, row: Mapping[str, Any], url_has: str) -> None:
    if url_has not in row["url"]:
        raise ValueError(f"#{number} 행의 URL이 정책 표와 다름 — 행 순서가 바뀌었는지 확인: {row['url']}")


def apply_policy(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """기사 행 목록에 정책 필드를 붙인 새 목록을 돌려준다. 여러 번 적용해도 결과가 같다.

    붙는 필드: source_published_at, available_at, available_basis, evidence_url, input_policy.
    제목 판본을 바꾼 행은 title 을 쓰는 판본으로 바꾸고 원래 값을 title_as_recorded 에 둔다.
    제외한 행은 excluded=True, exclusion_reason 을 달고 available_at 은 None 이다.
    기존 published_at 은 건드리지 않는다.
    """
    out: list[dict[str, Any]] = []
    for number, original in enumerate(rows, start=1):
        row = dict(original)
        recorded_title = row.pop("title_as_recorded", row["title"])
        for key in ("excluded", "exclusion_reason", "time_assumption"):
            row.pop(key, None)
        row["title"] = recorded_title

        raw = row["published_at"]
        evidence = row["url"]
        if number in RAW_PUBLISHED:
            url_has, raw, evidence = RAW_PUBLISHED[number]
            _check_row(number, row, url_has)
        row["source_published_at"] = raw

        if number in DATE_ONLY:
            rule = DATE_ONLY[number]
            _check_row(number, row, rule["url_has"])
            row["available_at"] = ny_end_of_day_utc(raw)
            row["available_basis"] = "date_only_ny_eod"
            row["time_assumption"] = rule["time_assumption"]
            evidence = rule["evidence_url"]
        elif number in TITLE_EDITIONS:
            rule = TITLE_EDITIONS[number]
            _check_row(number, row, rule["url_has"])
            edition = choose_edition(rule["editions"])
            if edition is None:
                row["available_at"] = None
                row["available_basis"] = None
                row["excluded"] = True
                row["exclusion_reason"] = rule["exclusion_reason"]
                evidence = rule["editions"][0]["evidence_url"]
            else:
                row["available_at"] = ceil_to_second(edition["captured_at"])
                row["available_basis"] = "archive_capture"
                evidence = edition["evidence_url"]
                if edition["title"] != recorded_title:
                    row["title_as_recorded"] = recorded_title
                    row["title"] = edition["title"]
        elif len(raw) == 10:
            raise ValueError(f"#{number}: 날짜만 있는 행인데 DATE_ONLY 표에 없음")
        else:
            row["available_at"] = ceil_to_second(raw)
            row["available_basis"] = "published"

        row["evidence_url"] = evidence
        row["input_policy"] = POLICY_VERSION
        # 키 순서를 고정해 다시 적용해도 파일이 바이트 단위로 같게 한다
        out.append({k: row[k] for k in _FIELD_ORDER if k in row}
                   | {k: v for k, v in row.items() if k not in _FIELD_ORDER})
    return out
