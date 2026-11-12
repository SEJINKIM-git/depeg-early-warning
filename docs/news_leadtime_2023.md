# 뉴스 신호 리드타임 — 2023-03 USDC 디페그

작성: Sejin · 작성일 2026-11-12 · 상태: **잠정** (입력인 [기사 손 정리 표](news_2023_handpicked.md)가 승인 대기 중)

## 한 문장

**가격만: 최저점 최대 3시간 전 → 뉴스 포함: 끊기지 않고 켜진 구간 기준 최저점 35시간 전
(가장 보수적으로 잡아도 15시간 전).**

엔진 가중치는 이 PR에서 건드리지 않았다. 아래 숫자는 재석의 가중치 재설계에 넘기는 근거다.

## 1. 기준 시각

| 사건 | 시각 (UTC) | 출처 |
| --- | --- | --- |
| 가격이 처음 −50bps를 넘음 | 2023-03-11 05:00 (−137.8bps) | `signals_usdc_2023_depeg_hourly.json` |
| 가격 최저점 | 2023-03-11 08:00 (−1,373.3bps) | 같은 파일 |
| 가격만으로 낼 수 있는 리드타임 | 3시간 | 위 둘의 차이 |

## 2. 뉴스 신호가 켜진 시각

관측 시각 t마다 "t 이전 24시간 안에 나온 기사"만 보고 0/1을 냈다. 보관처 목록은 그 시점에 공개돼
있던 최신 보고서(2023-01분, 03-02 발행 — SVB·Signature·Silvergate 포함 은행 7곳)다.

| 무엇을 기준으로 보나 | 켜진 시각 (UTC) | −50bps 전 | 최저점 전 | 켠 기사 |
| --- | --- | ---: | ---: | --- |
| ① 처음 켜진 시각 | 03-07 23:00 | 78시간 | 81시간 | Bloomberg "Silvergate Is in Talks With FDIC Officials…" (B: Silvergate + FDIC) |
| ② **가격 이탈까지 끊기지 않고 켜져 있던 구간의 시작** | 03-09 21:00 | **32시간** | **35시간** | TechCrunch "Silvergate's shiny hinges have rusted as the crypto bank plans to shut down" (B) |
| ③ SVB 기사로 처음 켜진 시각 | 03-10 11:00 | 18시간 | 21시간 | Irish Times(FT 전재) "…Silicon Valley Bank races to prevent bank run" (B) |
| ④ SVB 폐쇄 발표로 켜진 시각 | 03-10 17:00 | 12시간 | 15시간 | FDIC 발표문, CNBC, Fortune(AP) (B) |
| ⑤ USDC 자체 위기(A등급)로 처음 켜진 시각 | 03-11 01:00 | 4시간 | 7시간 | CoinDesk "USDC Stablecoin Depegs From $1…" (A) |

켜져 있던 구간: 03-07 23:00 ~ 03-08 23:00 → **꺼짐(21시간)** → 03-09 21:00 ~ 03-12 10:00 → 꺼짐(12시간)
→ 03-12 23:00 ~ 03-14 00:00(파일 끝). 가격 파일과 같은 120시간 축에서는 88시간이 켜져 있다.

## 3. 어느 숫자를 써야 하나

- **①(81시간)은 대표 숫자로 쓰지 않는 것을 권한다.** Silvergate 기사로 켜졌다가 3/9에 21시간 동안
  꺼졌다. Circle은 3/4에 Silvergate에서 자금을 뺐다고 이미 밝혔으므로, 이 신호는 "공시에 나온 은행의
  위기"로는 맞지만 USDC 준비금 위험으로는 약하다.
- **②(35시간)가 이 PR의 대표 숫자다.** 다만 근거가 약하다. 그 21시간 뒤 다시 켠 것은 Silvergate 분석
  기사 1건의 "shut down"이라는 단어다. 이 기사 1건을 빼면 시작이 ③(21시간)으로, FT 전재 기사까지
  빼면 ④(15시간)로 밀린다.
- **④(15시간)는 어떤 기사를 빼도 흔들리지 않는 하한이다.** SVB 폐쇄는 원 발표문과 여러 매체가 같은
  시간대에 동시에 켠다.
- 후보 131건 전체로 계산해도 ①·②·⑤는 같다. 구간 시작 03-09 21:00도 같다.

## 4. 기준표 v0가 놓친 제목과 잘못 켠 제목

이번 PR은 v0 패턴을 **그대로** 두었다. 이 표를 보고 패턴을 고치면 같은 데이터로 잰 리드타임이
부풀려지기 때문이다. 아래는 다음 버전의 후보이며, 고친다면 다른 기간(예: 2023-01~02 평시,
2026년 실시간 제목)으로 오탐을 따로 확인해야 한다.

60건 중 A 8건 · B 12건 · 해당 없음 40건. 해당 없음 가운데 사람이 보면 위기인 제목:

| 시각 (UTC) | 놓친 제목 | 빠진 표현 |
| --- | --- | --- |
| 03-08 21:06 | SVB Financial Group Announces Proposed Offerings of Common Stock… | 증자 발표문에는 "capital raise"라는 말이 없다 |
| 03-08 21:30 | Silvergate … Announces Intent to Wind Down Operations and Voluntarily Liquidate | wind down, liquidat- |
| 03-09 19:33 | Shares of SVB Financial fall 60% as tech-focused bank looks to raise more cash | 주가 급락(fall/plunge N%), raise cash |
| 03-09 20:40 | Venture firms are advising portfolio companies to move money out of SVB | 예금 인출 권고(pull/withdraw/move money) |
| 03-10 14:56 | Silicon Valley Bank plunges 60% before halt… | halt, plunge |
| 03-10 16:50 | Silicon Valley Bank Shuttered by State Regulators | shutter-, closed by, takes possession |
| 03-11 03:26 | Circle says $3.3 billion of USDC reserves are with Silicon Valley Bank | 발행사 + 위기 은행 이름이 함께 나옴 |
| 03-11 03:41 | (Coinbase) We are temporarily pausing USDC:USD conversions… | conversions paused/suspended |
| 03-11 16:03 | Stablecoin USDC breaks dollar peg… | breaks peg |

**3/8 저녁의 두 발표문을 놓친 것이 가장 크다.** Silvergate 청산 발표(21:30Z)만 잡았어도 3/9의
21시간 공백이 메워져, 신호가 ①(03-07 23:00)부터 가격 이탈까지 끊기지 않았을 것이다. 다만 이것은
패턴을 고친 뒤 평시 오탐과 함께 다시 재야 하는 추정이다.

잘못 켠 제목(회복 국면인데 A·B):

| 시각 (UTC) | 제목 | 걸린 단어 |
| --- | --- | --- |
| 03-13 10:00 | $3.3 Billion of USDC Reserve Risk Removed, Dollar De-peg Closes | De-peg |
| 03-14 08:52 | Circle's CEO discusses the 'precautions' the company took after SVB's collapse | collapse |

이 때문에 페그를 회복한 3/13 이후에도 신호가 꺼지지 않는다. 기준표에 "해소" 표현이 없어서다.

## 5. 한계

- **평시 오탐률은 재지 않았다.** 기사 표는 위기 주간만 다룬다. "평소에도 자주 켜지는 신호"인지는
  평시 구간(2023-01-15~02-12) 기사를 모아야 알 수 있다. 가중치를 올리기 전에 필요하다.
- **기사 선정은 사람이 했다.** 60건은 실제로 그 시각에 존재한 제목이지만, 실시간 수집기가 같은 기사를
  같은 시각에 잡았으리라는 보장은 없다. GDELT 자동 수집(2차)으로 대조할 수 있다.
- **발행 시각 오차는 모두 늦은 쪽이다.** 아카이브·전재본 시각을 쓴 15건은 실제보다 늦게 잡혔을 수
  있으므로, 리드타임은 과소 추정 방향이다.
- 가격은 Bitstamp 1시간 종가라 −50bps 돌파 시각은 최대 1시간 늦게 잡힌다.

## 6. 다시 계산하는 법

```
python -m src.intelligence.build_news_signals          # 신호 파일 생성 + 요약 출력
python -m src.intelligence.build_news_signals --check  # 저장된 파일이 기사 표와 맞는지만 확인
```
