"""2023-03 기사 표(JSON)에 입력 시각 정책을 적용한다. 규칙은 src/intelligence/news_input_policy.py.

사용: python -m scripts.apply_news_input_policy [--check]
  --check  파일을 쓰지 않고, 저장된 표가 정책을 적용한 결과와 같은지만 확인
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.intelligence.news_input_policy import POLICY_VERSION, apply_policy

ARTICLES = Path("data/historical/news_2023_handpicked.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    opts = parser.parse_args(argv)

    before = ARTICLES.read_text(encoding="utf-8")
    rows = apply_policy(json.loads(before))
    after = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    if opts.check:
        if before != after:
            print(f"{ARTICLES} 에 {POLICY_VERSION} 이 반영돼 있지 않습니다. --check 없이 다시 실행하세요.")
            return 1
        return 0

    ARTICLES.write_text(after, encoding="utf-8")
    moved = sum(1 for r in rows if r["available_basis"] == "archive_capture")
    excluded = sum(1 for r in rows if r.get("excluded"))
    print(f"{POLICY_VERSION}: {len(rows)}행, 캡처 시각 사용 {moved}행, 제외 {excluded}행")
    return 0


if __name__ == "__main__":
    sys.exit(main())
