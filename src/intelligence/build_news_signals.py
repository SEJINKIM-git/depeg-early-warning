"""2023-03 손 정리 기사 → 시간별 뉴스 Signal 파일 생성 + 리드타임 요약 출력.

I/O(파일 읽기·쓰기)는 이 파일의 main()에만 있다. 변환은 news_signal.py 의 순수 함수.

사용: python -m src.intelligence.build_news_signals [--check]
  --check  파일을 쓰지 않고, 저장된 결과가 다시 계산한 값과 같은지만 확인
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.intelligence.news_input_policy import POLICY_VERSION
from src.intelligence.news_signal import hourly_axis, hourly_news_signals, lead_time_summary

ARTICLES = Path("data/historical/news_2023_handpicked.json")
PRICES = Path("data/historical/signals_usdc_2023_depeg_hourly.json")
OUTPUT = Path("data/historical/signals_usdc_2023_news_hourly.json")
# 리드타임은 가격 파일 시작(03-09T01:00Z)보다 앞에서 신호가 켜졌는지도 봐야 하므로 03-06부터 훑는다
SCAN_FROM = "2023-03-06T01:00:00Z"


def main(argv: list[str] | None = None) -> int:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--check", action="store_true")
    opts = args.parse_args(argv)

    articles = json.loads(ARTICLES.read_text(encoding="utf-8"))
    prices = json.loads(PRICES.read_text(encoding="utf-8"))
    axis = sorted({s["observed_at"] for s in prices})

    stale = [a["url"] for a in articles if a.get("input_policy") != POLICY_VERSION]
    if stale:
        print(f"{ARTICLES} 의 {len(stale)}행에 {POLICY_VERSION} 이 없습니다. "
              "python -m scripts.apply_news_input_policy 를 먼저 실행하세요.")
        return 1

    signals = hourly_news_signals("USDC", axis, articles, POLICY_VERSION)
    text = json.dumps(signals, ensure_ascii=False, indent=2) + "\n"
    if opts.check:
        if OUTPUT.read_text(encoding="utf-8") != text:
            print(f"{OUTPUT} 가 기사 표와 맞지 않습니다. --check 없이 다시 생성하세요.")
            return 1
    else:
        OUTPUT.write_text(text, encoding="utf-8")

    print(json.dumps(sensitivity_table(articles, prices, axis), ensure_ascii=False, indent=2))
    return 0


def _is_date_only(article: dict) -> bool:
    return article.get("available_basis") == "date_only_ny_eod" or len(article["published_at"]) == 10


def _is_silvergate(article: dict) -> bool:
    return "silvergate" in article["title"].lower()


def sensitivity_table(articles: list[dict], prices: list[dict], axis: list[str]) -> dict:
    """전체 / 날짜만 있는 행(#47) 제외 / Silvergate 제목 제외 조합별 리드타임 요약."""
    variants = {
        "all": articles,
        "without_date_only": [a for a in articles if not _is_date_only(a)],
        "without_silvergate": [a for a in articles if not _is_silvergate(a)],
        "without_date_only_and_silvergate": [
            a for a in articles if not _is_date_only(a) and not _is_silvergate(a)
        ],
    }
    scan_axis = hourly_axis(SCAN_FROM, axis[-1])
    out = {}
    for name, rows in variants.items():
        summary = lead_time_summary(hourly_news_signals("USDC", scan_axis, rows), prices)
        summary.pop("news_first_evidence")
        if summary["streak_start"]:
            summary["streak_lead_before_low_hours"] = (
                summary["streak_lead_before_breach_hours"] + summary["price_only_lead_hours"]
            )
        summary["hours_flag_on_in_file"] = sum(
            s["value"] for s in hourly_news_signals("USDC", axis, rows)
        )
        summary["hours_in_file"] = len(axis)
        summary["articles_used"] = sum(1 for a in rows if not a.get("excluded"))
        out[name] = summary
    return out


if __name__ == "__main__":
    sys.exit(main())
