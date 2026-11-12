# 뉴스 기준표 v2 변경 목록 (사전 등록)

작성: Sejin · 작성일 2026-11-12 · 상태: **승인됨** (2026-11-12, Sejin — b7은 노출 표현 조건 포함으로 확정)

v1([src/intelligence/news_rubric.py](../src/intelligence/news_rubric.py))을 v2로 바꿀 때 고칠 항목을
**코드보다 먼저** 여기 확정한다. 항목의 출처는 두 곳뿐이다.

- **(a)** 대시보드 v0.2(ThreatWatch-AI `api/_depeg/news_rubric.py`, 독립 검토 반영)의 오탐 방지 규칙
- **(b)** [news_leadtime_2023.md](news_leadtime_2023.md) 4장 "놓친 제목과 잘못 켠 제목" 표

이 목록 밖의 패턴은 2023-03 결과를 보면서 추가하지 않는다. 같은 데이터로 계속 고치면 리드타임이
부풀려진다. 승인 뒤 바꾸고 싶은 항목이 생기면 이 문서를 먼저 고치고 그 이유를 적는다.

v1에서 그대로 두는 것: `classify(title, counterparties)` 시그니처, `REPORTS` 표, `counterparties_at`,
`news_flag`, 순수 함수 원칙(파일 I/O는 `build_news_signals.py`에만), 표준 라이브러리만 사용.

## (a) v0.2에서 가져오는 오탐 방지 규칙

| # | 항목 | v1 | v2 |
| --- | --- | --- | --- |
| a1 | 발행사 인식 | `USDC`, `USD Coin`, `Circle Internet`, `\bCircle\b` (대소문자 무시) | `\bUSDC\b`, `\bUSD Coin\b`, `\bCircle Internet\b`, `\bCRCL\b` (대소문자 무시). **`Circle`은 대문자로 쓰였고 같은 제목에 `stablecoin`·`USDC`·`crypto`가 있을 때만** |
| a2 | A등급 위기 표현 | `collapse`, `frozen`, `exploit`, `hack`, `stuck at`, `trapped`, `reserve exposure`, `$0.9x` 어디서나, `below $1` 등 | v0.2 목록 그대로: 페그 이탈(`de-peg(ged/s)`, `lost/loses/losing peg`, `breaks peg`), `below $1`(뒤에 숫자·`%`가 오면 제외), USDC 바로 뒤 25자 안의 `$0.xx`, 상환·발행·출금 중단, `bank run`, `insolven-`, `reserve shortfall/gap/hole`, `USDC/stablecoin collapse/crash`. 단독 `collapse`·`stuck at`·`trapped`·`reserve exposure`는 A에서 뺀다 |
| a3 | 보안 사건 | 해킹·동결·익스플로잇 → A | → **C**(관찰): `exploit-`, `hack-`, `freez-`, `froze(n)`, `blacklist-` |
| a4 | 부정·소문·회고 하향 | 없음 | 위기 표현이 있어도 아래가 같이 있으면 A·B → **C**: `holds/keeps/maintains/regains/restores/back to/returns to (dollar) peg`, `rumor(s)`, `denies/denied`, `fears ease/eased/easing/overblown`, `N years/months after`, `anniversary`, `lessons from` |
| a5 | B등급 위기 표현 | `\bFDIC\b` 단독, `fail(s/ed/ure)` 등 | v0.2 목록 그대로. **FDIC는 `FDIC takes/took/seizes/takeover/steps in`일 때만**, `fail(s/ed)`·`bank failure` |
| a6 | 보관처 별칭 | `Cross River`, `BlackRock`, `BNY Mellon` 등 | `Cross River` → **`Cross River Bank`만**. `BlackRock` → **단독으로는 매칭 안 함**(펀드는 `Circle Reserve Fund`·`USDXX`로 잡음). BNY → `BNY Mellon`, `Bank of New York Mellon`, `BNY` 뒤에 `bank`·`custod-`. `Customers Bank(corp)` |

보관처 목록 자체(어느 시점에 어느 기관이 공개돼 있었나)는 v1의 `REPORTS`·`counterparties_at`을 그대로 쓴다.
v0.2의 2026년 상수 목록은 버린다.

## (b) 리드타임 문서 4장 표에서 가져오는 항목

| # | 놓친/잘못 켠 표현 (4장) | 넣을 곳 | v2 패턴 (대소문자 무시) |
| --- | --- | --- | --- |
| b1 | wind down, liquidat- | B 위기 표현 | `\bwind(s\|ing)? down\b`, `\bliquidat\w*` |
| b2 | shutter-, closed by (regulators), takes possession | B 위기 표현 | `\bshutter\w*`, `\bclosed by (\w+ ){0,2}regulators?\b`, `\b(takes?\|took\|taking) possession\b` |
| b3 | conversions paused/suspended | A 위기 표현 | `\b(conversions?\|redemptions?) (are \|were \|is )?(paused\|suspended\|halted)\b` 와 어순이 반대인 `\b(paus\|suspend\|halt)\w* [^.;:]{0,30}\b(conversions?\|redemptions?)\b` (4장의 Coinbase 제목은 "pausing USDC:USD conversions" 어순) |
| b4 | breaks (its/the) peg | A 위기 표현 | `\bbreaks? (its \|the )?(dollar )?peg\b` (v0.2 패턴에 `dollar` 선택어만 더함 — 4장 제목이 "breaks dollar peg") |
| b5 | 주가 급락 (plunge/fall N%) | B 위기 표현 | `\b(plung\|fall\|fell\|drop)\w* (more than \|over \|about \|nearly )?\d+(\.\d+)?%` |
| b6 | 예금 인출 권고 | B 위기 표현 | `\b(move\|pull\|withdraw)\w* (\w+ ){0,2}(money\|funds\|deposits\|cash) (out of\|from)\b` |
| b7 | 발행사 + 보관처가 한 제목에 함께 나옴 | 새 B 규칙 | 발행사(a1) **와** 그 시점 보관처가 함께 있고, **노출 표현**이 있으면 B. 노출 표현: `\breserves? (are \|were \|is )?(held )?(with\|at)\b`, `\bheld (\w+ ){0,2}reserves? (at\|with)\b`, `\bexposure (to\|at)\b` |
| b8 | 해소 표현 (회복기에 신호가 안 꺼짐) | a4 하향 목록에 추가 | `\bde-?peg (closes\|closed\|ends\|ended\|is over)\b`, `\brisk (removed\|eliminated)\b`, `\b(regains?\|regained\|restores?\|restored)\b[^.;:]{0,20}\bpeg\b`, `\bback (to\|toward\|towards) \$?1\b` |

### b7에 노출 표현 조건을 붙인 이유 (승인 때 확정)

프롬프트의 문장 그대로("발행사 + 보관처가 함께 나오면 B")만 쓰면 2026년 실시간 화면에서
"BNY Mellon named custodian for USDC reserves" 같은 **제휴·사업 뉴스가 B로 켜진다.** 그래서 4장 표의
예시("$3.3 billion of USDC reserves are **with** Silicon Valley Bank")가 가진 "준비금이 그 은행에 있다"는
표현을 조건으로 붙였다. 승인 때 이 조건을 포함하기로 확정했다.

## 분류 순서 (v2)

1. 발행사 + A 위기 표현 → **A** (하향 표현이 같이 있으면 C)
2. 보관처 + B 위기 표현 → **B** (하향 표현이 같이 있으면 C)
3. 발행사 + 보관처 + 노출 표현(b7) → **B** (하향 표현이 같이 있으면 C)
4. 발행사 + 관찰 표현(규제·보안 사건) → **C**
5. 그 밖 → 해당 없음

## 고치지 않는 것 (알고 있는 한계)

4장 표에 있지만 위 목록으로 해결되지 않는 제목. 결과를 보며 새 패턴을 만들지 않으려고 그대로 둔다.

| 제목 | 이유 |
| --- | --- |
| SVB Financial Group Announces Proposed Offerings of Common Stock… | 증자 발표문에 위기 단어가 없다. 4장에 "빠진 표현"이 패턴으로 정리돼 있지 않다 |
| Circle's CEO discusses the 'precautions' the company took after SVB's collapse | 회복기 오탐. 4장에 원인("해소 표현이 없음")은 있지만 이 제목에는 해소 표현이 없다. `after … collapse`를 하향하면 사건 당일 기사도 꺼진다 |
| Silicon Valley Bank plunges 60% before halt… 의 `halt` | b5(급락 %)로 잡힌다. `halt` 단독은 넣지 않는다(거래 정지 뉴스가 흔함) |

## 확인 방법

- 각 항목(a1~a6, b1~b8)마다 통과 사례 1개 + 오탐 방지 사례 1개를 `tests/test_news_rubric.py`에 둔다.
- 대시보드 `tests/test_depeg_live.py`의 오탐·미탐 사례를 모두 옮겨 온다(2026년 사례는
  `counterparties_at("2026-11-11T00:00:00Z")` 목록으로).
- 평시 오탐: `docs/news_2023_calm_sample.md`(원준, 11/16 예정)가 생기면 A·B 개수를 센다. 0이어야 한다.
  그 전까지는 "대기".
- 리드타임은 v1·v2 숫자를 나란히 적고 v1을 지우지 않는다. 기사 표가 승인 대기면 둘 다 "잠정".
