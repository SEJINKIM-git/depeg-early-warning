"""가중치 후보 백테스트 — 후보별 결과 표를 출력하고, 선택된 엔진 설정의 그래프를 그린다.

계산은 src/engine/backtest.py 의 순수 함수. 이 파일은 파일 읽기·쓰기와 그래프만 맡는다.

사용: python -m scripts.backtest_weights [--plots] [--json]
  --plots  docs/img/weights_crisis.png, docs/img/weights_calm.png 를 현재 엔진 설정으로 다시 그린다
  --json   후보별 결과를 JSON으로 출력 (시각별 점수 제외)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.engine.backtest import ALERT_LINE, APPROVAL_LINE, CANDIDATES, evaluate, select

HIST = Path("data/historical")
IMG = Path("docs/img")


def _load(name: str) -> list[dict]:
    return json.loads((HIST / name).read_text(encoding="utf-8"))


def _fmt(cross: dict) -> str:
    if cross["first_at"] is None:
        return "넘지 못함"
    return f"{cross['first_at'][5:16].replace('T', ' ')} (최저점 {cross['hours_before_low']:.0f}h 전)"


def _plot(series: list[dict], extra: list[dict] | None, title: str, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    def ts(p: dict) -> datetime:
        return datetime.strptime(p["t"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=150)
    if extra:
        ax.plot([ts(p) for p in extra], [p["score"] for p in extra],
                color="#8a8f98", linewidth=1.2, label="price only")
    ax.plot([ts(p) for p in series], [p["score"] for p in series],
            color="#1f4e9c", linewidth=1.8, label="risk score")
    ax.axhline(ALERT_LINE, color="#c77700", linestyle="--", linewidth=1, label="70 alert (P2)")
    ax.axhline(APPROVAL_LINE, color="#b3261e", linestyle="--", linewidth=1, label="85 approval (P1)")
    ax.set_ylim(0, 100)
    ax.set_ylabel("risk score")
    ax.set_title(title)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d", tz=timezone.utc))
    ax.grid(alpha=0.25)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=8, frameon=False)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, metadata={"Software": None})
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plots", action="store_true")
    parser.add_argument("--json", action="store_true")
    opts = parser.parse_args(argv)

    crisis = _load("signals_usdc_2023_depeg_hourly.json")
    calm = _load("signals_usdc_2023_calm_hourly.json")
    news = _load("signals_usdc_2023_news_hourly.json")

    results = {
        c["name"]: evaluate("USDC", crisis, calm, news,
                            weights=c["weights"], peg_full_scale_bps=c["peg_full_scale_bps"])
        for c in CANDIDATES
    }
    chosen = select(results)

    if opts.json:
        slim = {k: {kk: vv for kk, vv in v.items() if kk != "series"} for k, v in results.items()}
        print(json.dumps({"selected": chosen, "candidates": slim}, ensure_ascii=False, indent=2))
    else:
        for c in CANDIDATES:
            r = results[c["name"]]
            print(f"{c['name']} {c['label']}")
            print(f"  사태 최고 {r['crisis']['max']:.2f} | 70: {_fmt(r['crisis']['alert'])} | "
                  f"85: {_fmt(r['crisis']['approval'])}")
            print(f"  가격만 최고 {r['crisis_price_only']['max']:.2f} | 70: {_fmt(r['crisis_price_only']['alert'])}")
            print(f"  평시 최고 {r['calm_max']:.2f} (오경보 {r['calm_false_alarms']}/{r['calm_hours']}h) | "
                  f"뉴스 단독 최악 {r['news_only_worst_case']:.2f} | 조건 {r['conditions']} "
                  f"→ {'통과' if r['passes'] else '탈락'}")
        print(f"선택: {chosen}")

    if opts.plots:
        current = evaluate("USDC", crisis, calm, news)  # 엔진 기본값(선택 반영 후)
        _plot(current["series"]["crisis"], current["series"]["crisis_price_only"],
              "USDC 2023-03 crisis week: price + attestation + news", IMG / "weights_crisis.png")
        _plot(current["series"]["calm"], None,
              "USDC 2023-01-15 to 02-12 calm weeks: price + attestation (news = 0)", IMG / "weights_calm.png")
        print(f"그래프: {IMG / 'weights_crisis.png'}, {IMG / 'weights_calm.png'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
