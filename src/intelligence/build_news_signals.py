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

    signals = hourly_news_signals("USDC", axis, articles)
    text = json.dumps(signals, ensure_ascii=False, indent=2) + "\n"
    if opts.check:
        if OUTPUT.read_text(encoding="utf-8") != text:
            print(f"{OUTPUT} 가 기사 표와 맞지 않습니다. --check 없이 다시 생성하세요.")
            return 1
    else:
        OUTPUT.write_text(text, encoding="utf-8")

    scan = hourly_news_signals("USDC", hourly_axis(SCAN_FROM, axis[-1]), articles)
    summary = lead_time_summary(scan, prices)
    summary["hours_flag_on_in_file"] = sum(s["value"] for s in signals)
    summary["hours_in_file"] = len(signals)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
