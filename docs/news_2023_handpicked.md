# 2023-03 USDC 디페그 주간 기사 손 정리 표

작성: Sejin · 작성일 2026-11-12 · 상태: **승인 대기** (승인 전에는 이 표로 만든 신호·리드타임을 잠정값으로 본다)

목적: 2023-03-06 ~ 03-14에 나온 기사 제목을 발행 시각(UTC)과 함께 사람이 먼저 정리해,
뉴스 기준표([src/intelligence/news_rubric.py](../src/intelligence/news_rubric.py))가 가격보다
얼마나 먼저 신호를 켤 수 있었는지 계산하는 입력으로 쓴다. 계산 결과는
[news_leadtime_2023.md](news_leadtime_2023.md)에 있다.

- 기계가 읽는 원본: [data/historical/news_2023_handpicked.json](../data/historical/news_2023_handpicked.json)
  (이 표와 같은 60건. 기사별 시각 확인 방법 전문은 JSON의 `note`에 있다)
- 추리기 전 후보 전체 131건: [data/historical/news_2023_candidates.json](../data/historical/news_2023_candidates.json)

## 1. 어떻게 모았나

1. 사건별로 원 발표문과 주요 매체 기사를 찾아 **기사 페이지를 직접 열어** 제목과 발행 시각을 옮겼다.
   시각은 ① 페이지 메타데이터(`article:published_time`, JSON-LD `datePublished`) ② 페이지에 보이는
   시각 ③ 보도자료 배포 시각 순으로 썼다. 페이지가 막힌 매체(Bloomberg, Reuters, CoinDesk 일부)는
   웹 아카이브(web.archive.org) 스냅샷의 메타데이터를 썼다.
2. 131건 중 60건을 골랐다. 기준: 사건마다 원 발표문 1건 + 매체가 겹치지 않게 2~4건,
   **기준표가 놓치는 제목도 빼지 않고** 포함, 위기와 무관한 대조용 5건 포함.
3. 제목이 발행 뒤에 바뀐 것이 확인된 기사는 **발행 시각에 실제로 있던 제목**만 쓴다.
   그 제목을 확인할 수 없으면 표에서 뺐다(3절).

시각을 확신할 수 없을 때는 항상 **늦은 쪽**으로 잡았다. 신호가 실제보다 일찍 켜진 것으로
계산되는 일을 막기 위해서다. 날짜만 확인된 기사는 다음 날 00:00Z부터 쓴다.

시각 출처별 건수: 페이지 메타데이터 30 · 페이지 표시 시각 13 · 웹 아카이브 12 · 보도자료 배포 시각 4 · 날짜만 1

## 2. 표 (60건, 발행 시각순)

"기준표 등급"은 디페그 주간의 보관처 목록(2023-01 보고서, 03-02 발행)으로 분류한 결과다.
A·B는 신호를 켜고, —는 해당 없음이다. 괄호는 (걸린 기관 + 걸린 단어).

| # | 발행 시각 (UTC) | 매체 | 제목 | 기준표 등급 | 비고 (시각 출처·의심점) |
| ---: | --- | --- | --- | --- | --- |
| 1 | 2023-03-07 22:44 | Bloomberg | [Silvergate Is in Talks With FDIC Officials on Ways to Salvage Bank](https://www.bloomberg.com/news/articles/2023-03-07/silvergate-in-talks-with-fdic-officials-on-ways-to-salvage-bank) | B (`Silvergate` + `FDIC`) | 웹 아카이브 스냅샷 |
| 2 | 2023-03-07 23:00 | CNBC | [Silvergate pops on report it's in talks with the FDIC to save the bank](https://www.cnbc.com/video/2023/03/07/silvergate-pops-on-report-its-in-talks-with-the-fdic-to-save-the-bank.html) | B (`Silvergate` + `FDIC`) | 페이지 메타데이터 |
| 3 | 2023-03-08 21:06 | PR Newswire | [SVB Financial Group Announces Proposed Offerings of Common Stock and Mandatory Convertible Preferred Stock](https://www.prnewswire.com/news-releases/svb-financial-group-announces-proposed-offerings-of-common-stock-and-mandatory-convertible-preferred-stock-301766247.html) | — | 보도자료 배포 시각 |
| 4 | 2023-03-08 21:30 | Business Wire | [Silvergate Capital Corporation Announces Intent to Wind Down Operations and Voluntarily Liquidate Silvergate Bank](https://www.businesswire.com/news/home/20230308005795/en/Silvergate-Capital-Corporation-Announces-Intent-to-Wind-Down-Operations-and-Voluntarily-Liquidate-Silvergate-Bank) | — | 보도자료 배포 시각 |
| 5 | 2023-03-08 21:35 | CNBC | [Crypto-focused bank Silvergate is shutting operations and liquidating after market meltdown](https://www.cnbc.com/2023/03/08/silvergate-shutting-down-operations-and-liquidating-bank.html) | — | 페이지 메타데이터 |
| 6 | 2023-03-08 21:41 | CoinDesk | [Crypto Bank Silvergate Announces 'Voluntary Liquidation'](https://www.coindesk.com/policy/2023/03/08/crypto-bank-silvergate-announces-voluntary-liquidation) | — | 웹 아카이브 스냅샷 |
| 7 | 2023-03-09 03:49 | CoinDesk | [Crypto Stakeholders Say No Exposure to Shuttered Silvergate](https://www.coindesk.com/business/2023/03/09/crypto-stakeholders-say-no-exposure-to-shuttered-silvergate) | — | 웹 아카이브 스냅샷 |
| 8 | 2023-03-09 10:00 | Bloomberg | [‘Transactions at The Speed of The Internet’: Circle CEO Jeremy Allaire on Stablecoins](https://www.bloomberg.com/news/articles/2023-03-09/circle-ceo-jeremy-allaire-on-us-crypto-regulation-stablecoins-usdc) | — | 웹 아카이브 스냅샷. 대조용(위기와 무관). |
| 9 | 2023-03-09 12:35 | CNBC | [Bitcoin, ether fall after go-to crypto bank Silvergate announces liquidation](https://www.cnbc.com/2023/03/09/bitcoin-ether-fall-after-go-to-crypto-bank-silvergate-announces-liquidation.html) | — | 페이지 메타데이터 |
| 10 | 2023-03-09 16:08 | Bloomberg | [SVB Drops Most on Record as Startup Clients Face Cash Crunch](https://www.bloomberg.com/news/articles/2023-03-09/svb-plunges-most-since-1998-on-stock-offering-securities-sales) | — | 웹 아카이브 스냅샷. 제목은 같은 날 21:10Z 수정판. 최초 제목은 슬러그상 'SVB Plunges Most Since 1998…' (어느 쪽도 기준표에 걸리지 않음) |
| 11 | 2023-03-09 19:33 | CNBC | [Shares of SVB Financial fall 60% as tech-focused bank looks to raise more cash](https://www.cnbc.com/2023/03/09/svb-financial-falls-more-than-50percent-as-tech-bank-looks-to-raise-more-cash.html) | — | 페이지 메타데이터. 제목의 60%는 장 마감 뒤 수정(최초 50%). 기준표에 걸리지 않음 |
| 12 | 2023-03-09 20:00 | TechCrunch | [Silvergate’s shiny hinges have rusted as the crypto bank plans to shut down](https://techcrunch.com/2023/03/09/silvergates-shiny-hinges-have-rusted-as-the-crypto-bank-plans-to-shut-down/) | B (`Silvergate` + `shut down`) | 페이지 메타데이터 |
| 13 | 2023-03-09 20:14 | CoinDesk | [MakerDAO Founder Calls for Rebranding of DAI Stablecoin](https://www.coindesk.com/business/2023/03/09/makerdao-founder-calls-for-rebranding-of-dai-stablecoin/) | — | 웹 아카이브 스냅샷. 대조용(위기와 무관). |
| 14 | 2023-03-09 20:40 | TechCrunch | [Venture firms are advising portfolio companies to move money out of SVB](https://techcrunch.com/2023/03/09/silicon-valley-bank-firms-reactions/) | — | 페이지 메타데이터 |
| 15 | 2023-03-09 20:53 | Bloomberg | [Thiel Fund, Venture Firms Advise Companies to Pull Money From SVB](https://www.bloomberg.com/news/articles/2023-03-09/svb-ceo-becker-asks-silicon-valley-bank-clients-to-stay-calm) | — | 웹 아카이브 스냅샷. 03-10T00:56Z 스냅샷의 제목을 씀. 최종 제목 'SVB Races to Prevent Bank Run…'은 03-10T13:45Z 수정판이라 쓰지 않음 |
| 16 | 2023-03-09 21:39 | CoinDesk | [Voyager Continues Liquidating Crypto Assets for Circle’s USDC Stablecoin](https://www.coindesk.com/business/2023/03/09/voyager-continues-liquidating-crypto-assets-for-circles-usdc-stablecoin/) | — | 웹 아카이브 스냅샷. 대조용(위기와 무관). |
| 17 | 2023-03-09 22:11 | Bloomberg | [Peter Thiel’s Founders Fund Advises Companies to Withdraw Money From SVB](https://www.bloomberg.com/news/articles/2023-03-09/founders-fund-advises-companies-to-withdraw-money-from-svb) | — | 웹 아카이브 스냅샷 |
| 18 | 2023-03-10 02:56 | The Block | [Crypto VCs urge portfolio companies to pull funds from Silicon Valley Bank](https://www.theblock.co/post/218664/crypto-vcs-urge-portfolio-companies-to-pull-funds-from-silicon-valley-bank) | — | 페이지 표시 시각(분 단위) |
| 19 | 2023-03-10 03:54 | CNN | [Silicon Valley Bank scrambles to reassure clients after 60% stock wipe-out](https://www.cnn.com/2023/03/09/investing/silicon-valley-bank/index.html) | — | 페이지 메타데이터. CNN은 수정 때 발행 시각을 덮어씀 — 실제 최초 발행은 더 이를 수 있음(늦은 쪽으로 잡힘) |
| 20 | 2023-03-10 10:29 | The Irish Times | [Startup world spooked as Silicon Valley Bank races to prevent bank run](https://www.irishtimes.com/business/financial-services/2023/03/10/startup-world-spooked-as-silicon-valley-bank-races-to-prevent-bank-run) | B (`Silicon Valley Bank` + `bank run`) | 페이지 메타데이터. FT 기사 전재본의 게시 시각. FT 원문은 더 이름(늦은 쪽으로 잡힘) |
| 21 | 2023-03-10 13:08 | CoinDesk | [Cathie Wood's Ark Invest Buys $22M in Coinbase Shares](https://www.coindesk.com/business/2023/03/10/cathie-woods-ark-purchases-over-350k-coinbase-shares-in-biggest-buy-of-2023) | — | 페이지 표시 시각(분 단위). 대조용(위기와 무관). |
| 22 | 2023-03-10 14:56 | The Block | [Silicon Valley Bank plunges 60% before halt, Signature trading stopped shortly after open](https://www.theblock.co/post/218783/silicon-valley-bank-plunges-60-before-halt-signature-trading-stopped-shortly-after-open) | — | 페이지 메타데이터 |
| 23 | 2023-03-10 16:01 | CNBC | [Crypto bank Signature slides on Friday amid troubles at Silicon Valley Bank, Silvergate](https://www.cnbc.com/2023/03/10/crypto-bank-signature-slides-on-friday-amid-troubles-at-silicon-valley-bank-silvergate.html) | — | 페이지 메타데이터 |
| 24 | 2023-03-10 16:46 | CNBC | [Silicon Valley Bank is shut down by regulators in biggest bank failure since global financial crisis](https://www.cnbc.com/2023/03/10/silicon-valley-bank-is-shut-down-by-regulators-fdic-to-protect-insured-deposits.html) | B (`Silicon Valley Bank` + `failure`) | 페이지 메타데이터. 현재 제목은 수정판이나, 슬러그상 최초 제목에도 'shut down by regulators', 'FDIC'가 있었음 |
| 25 | 2023-03-10 16:46 | FDIC | [FDIC Creates a Deposit Insurance National Bank of Santa Clara to Protect Insured Depositors of Silicon Valley Bank, Santa Clara, California](https://www.fdic.gov/news/press-releases/2023/pr23016.html) | B (`Silicon Valley Bank` + `FDIC`) | 웹 아카이브 스냅샷. 페이지에 시각 없음. 가장 이른 아카이브 수집 시각(=늦어도 이때 공개) |
| 26 | 2023-03-10 16:50 | CoinDesk | [Silicon Valley Bank Shuttered by State Regulators](https://www.coindesk.com/policy/2023/03/10/silicon-valley-bank-shuttered-by-state-regulators) | — | 페이지 표시 시각(분 단위) |
| 27 | 2023-03-10 16:51 | California DFPI | [California Financial Regulator Takes Possession of Silicon Valley Bank](https://dfpi.ca.gov/2023/03/10/california-financial-regulator-takes-possession-of-silicon-valley-bank/) | — | 웹 아카이브 스냅샷. 페이지 403. 가장 이른 아카이브 수집 시각(=늦어도 이때 공개) |
| 28 | 2023-03-10 16:55 | Fortune | [Silicon Valley Bank has officially failed after less than a day of panicked selling as the federal government takes it over](https://fortune.com/2023/03/10/silicon-valley-bank-seized-regulators-bank-failure/) | B (`Silicon Valley Bank` + `failed`) | 페이지 메타데이터. AP 기사 전재본(Fortune 게시 시각) |
| 29 | 2023-03-10 16:56 | The Block | [Silicon Valley Bank closed by California regulator](https://www.theblock.co/post/218838/silicon-valley-bank-closed-by-california-regulator) | — | 페이지 메타데이터 |
| 30 | 2023-03-10 17:04 | Cointelegraph | [Silicon Valley Bank shut down by California regulator](https://cointelegraph.com/news/silicon-valley-bank-shut-down-by-california-regulator) | B (`Silicon Valley Bank` + `shut down`) | 페이지 메타데이터 |
| 31 | 2023-03-10 19:35 | CoinDesk | [Scrutiny Falls on $43B USDC Stablecoin’s Cash Reserves at Failed Silicon Valley Bank](https://www.coindesk.com/markets/2023/03/10/scrutiny-falls-on-43b-usdc-stablecoins-cash-reserves-at-failed-silicon-valley-bank) | B (`Silicon Valley Bank` + `Failed`) | 페이지 표시 시각(분 단위) |
| 32 | 2023-03-10 20:53 | TechCrunch | [Uncertainty stands around multibillion USDC empire as issuer Circle held reserves at Silicon Valley Bank](https://techcrunch.com/2023/03/10/uncertainty-stands-around-multi-billion-usdc-empire-as-issuer-circle-held-reserves-at-silicon-valley-bank/) | — | 페이지 메타데이터 |
| 33 | 2023-03-11 00:01 | CoinDesk | [USDC Stablecoin Depegs From $1; Circle Says Operations Are Normal](https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-depegs-from-1-circle-says-operations-are-normal) | A (`USDC` + `Depeg`) | 페이지 표시 시각(분 단위). 02:54Z '새 저점 반영' 수정 이력 있음 — 제목이 그때 손봐졌을 가능성 |
| 34 | 2023-03-11 00:05 | CoinDesk | [USDC Issuer Circle Says It 'Awaits Clarity' From FDIC on Silicon Valley Bank Collapse](https://www.coindesk.com/business/2023/03/11/usdc-issuer-circle-says-it-awaits-clarity-from-fdic-on-silicon-valley-bank-collapse) | A (`USDC` + `Collapse`) | 페이지 표시 시각(분 단위) |
| 35 | 2023-03-11 01:12 | Binance | [Binance has temporarily suspended auto-conversion of USDC to BUSD due to current market conditions, specifically related to high inflows & the incr…](https://twitter.com/binance/status/1634361554543030273) | — | 페이지 메타데이터. 시각은 트윗 ID에서 계산. 본문은 기사 내 임베드로 확인 |
| 36 | 2023-03-11 03:11 | Circle | [1/ Following the confirmation at the end of today that the wires initiated on Thursday to remove balances were not yet processed, $3.3 billion of t…](https://twitter.com/circle/status/1634391505988206592) | — | 페이지 메타데이터. 시각은 트윗 ID에서 계산. 본문은 기사 내 임베드로 확인 |
| 37 | 2023-03-11 03:26 | The Block | [Circle says $3.3 billion of USDC reserves are with Silicon Valley Bank](https://www.theblock.co/post/218971/circle-says-3-3-billion-of-usdc-reserves-are-with-silicon-valley-bank) | — | 페이지 표시 시각(분 단위) |
| 38 | 2023-03-11 03:41 | Coinbase | [We are temporarily pausing USDC:USD conversions over the weekend while banks are closed. During periods of heightened activity, conversions rely on…](https://twitter.com/coinbase/status/1634399032767307776) | — | 페이지 메타데이터. 시각은 트윗 ID에서 계산. 본문은 기사 내 임베드로 확인 |
| 39 | 2023-03-11 03:52 | CoinDesk | [Circle Confirms $3.3B of USDC's Cash Reserves Stuck at Failed Silicon Valley Bank](https://www.coindesk.com/business/2023/03/11/circle-confirms-33b-of-usdcs-cash-reserves-stuck-at-failed-silicon-valley-bank) | A (`USDC` + `Stuck at`) | 페이지 표시 시각(분 단위) |
| 40 | 2023-03-11 05:05 | Cointelegraph | [USDC depegs as Circle confirms $3.3B stuck with Silicon Valley Bank](https://cointelegraph.com/news/usdc-depegs-as-circle-confirms-3-3b-stuck-with-silicon-valley-bank) | A (`USDC` + `depeg`) | 페이지 메타데이터 |
| 41 | 2023-03-11 05:51 | CoinDesk | [USDC Stablecoin Depegs, Crypto Market Goes Haywire After Silicon Valley Bank Collapses](https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-and-crypto-market-go-haywire-after-silicon-valley-bank-collapses) | A (`USDC` + `Depeg`) | 페이지 표시 시각(분 단위) |
| 42 | 2023-03-11 07:26 | Reuters | [Crypto firm Circle reveals $3.3 bln exposure to Silicon Valley Bank](https://www.reuters.com/business/crypto-firm-circle-reveals-33-bln-exposure-silicon-valley-bank-2023-03-11/) | — | 웹 아카이브 스냅샷. 최초 제목(슬러그·Kitco 전재본으로 확인)을 씀. 21:32Z에 'Circle assures market after stablecoin USDC breaks dollar peg'로 바뀜 |
| 43 | 2023-03-11 10:10 | The Block | [USDC remains at about $0.90 following Circle's disclosure of funds at SVB](https://www.theblock.co/post/218993/usdc-and-dai-remain-at-about-0-90-following-circles-disclosure-of-funds-at-svb) | A (`USDC` + `$0.90`) | 페이지 메타데이터 |
| 44 | 2023-03-11 16:03 | CNBC | [Stablecoin USDC breaks dollar peg after firm reveals it has $3.3 billion in SVB exposure](https://www.cnbc.com/2023/03/11/stablecoin-usdc-breaks-dollar-peg-after-firm-reveals-it-has-3point3-billion-in-svb-exposure.html) | — | 페이지 메타데이터 |
| 45 | 2023-03-11 20:15 | Circle | [Sharing an Update on USDC and Silicon Valley Bank.](https://twitter.com/jerallaire/status/1634649346535833601) | — | 페이지 메타데이터. 시각은 트윗 ID에서 계산. 본문은 기사 내 임베드로 확인 |
| 46 | 2023-03-11 20:58 | CoinDesk | [Circle to ‘Cover Any Shortfall’ in USDC Reserves, Sparking Stablecoin Rally](https://www.coindesk.com/business/2023/03/11/circle-to-cover-any-shortfall-in-usdc-reserves-sparking-stablecoin-rally) | — | 페이지 표시 시각(분 단위) |
| 47 | 2023-03-12 | New York DFS | [Superintendent Adrienne A. Harris Announces New York Department of Financial Services Takes Possession of Signature Bank](https://www.dfs.ny.gov/reports_and_publications/press_releases/pr20230312) | — | 날짜만 확인. 페이지 403, 아카이브에도 시각 없음 → 다음 날 00:00Z부터 사용 |
| 48 | 2023-03-12 22:15 | Federal Reserve Board | [Joint Statement by Treasury, Federal Reserve, and FDIC](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230312b.htm) | — | 보도자료 배포 시각. 'For release at 6:15 p.m. EDT' 표기 |
| 49 | 2023-03-12 22:24 | CNBC | [Regulators close crypto-focused Signature Bank, citing systemic risk](https://www.cnbc.com/2023/03/12/regulators-close-new-yorks-signature-bank-citing-systemic-risk.html) | — | 페이지 메타데이터 |
| 50 | 2023-03-12 22:25 | CoinDesk | [Crypto-Friendly Signature Bank Shut Down by State Regulators](https://www.coindesk.com/policy/2023/03/12/crypto-friendly-signature-bank-shut-down-by-state-regulators-fed) | B (`Signature Bank` + `Shut Down`) | 페이지 표시 시각(분 단위) |
| 51 | 2023-03-12 23:05 | Fortune | [NYC-based Signature Bank fails, and banking regulators invoke ‘systemic risk exception’ for all depositors being made whole](https://fortune.com/2023/03/12/nyc-based-signature-bank-fails-closed-by-regulators-fdic-treasury/) | B (`Signature Bank` + `fails`) | 페이지 메타데이터. Bloomberg 기사 전재본(Fortune 게시 시각) |
| 52 | 2023-03-12 23:46 | The Block | [Circle USDC operations will resume when U.S. banks open Monday: CEO Allaire](https://www.theblock.co/post/219133/circle-usdc-operations-will-resume-at-open-monday-allaire) | — | 페이지 메타데이터 |
| 53 | 2023-03-13 00:24 | Cointelegraph | [USDC bounces back toward $1 peg after Fed announcement](https://cointelegraph.com/news/usdc-bounces-back-towards-1-peg-after-fed-announcement) | — | 페이지 메타데이터 |
| 54 | 2023-03-13 01:55 | CoinDesk | [Circle Scrambles to Right USDC After Signature Bank Failure](https://www.coindesk.com/policy/2023/03/12/circle-scrambles-to-right-usdc-after-signature-bank-failure/) | B (`Signature Bank` + `Failure`) | 페이지 표시 시각(분 단위) |
| 55 | 2023-03-13 03:56 | Fortune | [Circle adds Cross River as banking partner and expands BNY ties, USDC peg closes](https://fortune.com/crypto/2023/03/12/circle-adds-cross-river-as-banking-partner-and-expands-bny-ties-usdc-peg-closes/) | — | 페이지 메타데이터 |
| 56 | 2023-03-13 10:00 | Circle | [$3.3 Billion of USDC Reserve Risk Removed, Dollar De-peg Closes](https://www.prnewswire.com/news-releases/3-3-billion-of-usdc-reserve-risk-removed-dollar-de-peg-closes-301769820.html) | A (`USDC` + `De-peg`) | 보도자료 배포 시각. PR Newswire 배포 시각. 같은 내용이 03:20Z쯤 이미 기사화 — 실제 공개보다 늦게 잡힘 |
| 57 | 2023-03-13 14:09 | CoinDesk | [USDC Stablecoin Regains Dollar Peg After Silicon Valley Bank-Induced Chaos](https://www.coindesk.com/business/2023/03/13/usdc-stablecoin-regains-dollar-peg-after-silicon-valley-bank-induced-chaos) | — | 페이지 표시 시각(분 단위) |
| 58 | 2023-03-13 21:28 | The Block | [Meta announces plans to stop working on NFTs](https://www.theblock.co/post/219462/meta-announces-plans-to-stop-working-on-nfts) | — | 페이지 메타데이터. 대조용(위기와 무관). |
| 59 | 2023-03-14 08:52 | CNBC | [Circle's CEO discusses the 'precautions' the company took after SVB's collapse](https://www.cnbc.com/video/2023/03/14/circle-ceo-discusses-precautions-the-company-took-after-svb-collapse.html) | A (`Circle` + `collapse`) | 페이지 메타데이터 |
| 60 | 2023-03-14 21:53 | The Block | [Biggest USDC burn on record just occurred, net redemptions since Friday reach $4.5 billion](https://www.theblock.co/post/219887/biggest-usdc-burn-on-record-just-occurred-net-redemptions-since-friday-reach-4-5-billion) | — | 페이지 메타데이터 |

## 3. 뺀 기사 — 제목이 나중에 바뀌어 발행 시각의 제목을 알 수 없는 것

이 기사들을 넣으면 "그 시각에는 없던 문장"으로 신호가 켜진다(미래 정보). 후보 파일에는 남겨 두었다.

| 발행 시각 (UTC) | 매체 | 현재 제목 | 뺀 이유 |
| --- | --- | --- | --- |
| 2023-03-10 10:50 | Bloomberg | SVB Shares Halted for Pending News After Sinking Another 69% | 거래 정지는 13:35Z. 제목은 13:48Z 수정판 |
| 2023-03-10 13:53 | Reuters | SVB is largest bank failure since 2008 financial crisis | 폐쇄 발표(16:46Z쯤) 전에 처음 발행된 실시간 수정 기사 |
| 2023-03-10 13:59 | CNN | Silicon Valley Bank collapses after failing to raise capital | 위와 같음 |
| 2023-03-11 01:52 | FXStreet | Breaking: $3.3 billion of Circle's USDC reserves stuck at Silicon Valley Bank | 33억 달러는 03:11Z에야 공개. 최초 제목은 Binance 전환 중단 기사 |
| 2023-03-11 14:27 | Decrypt | USDC Stablecoin Falls to 87 Cents After Circle Discloses Exposure to Silicon Valley Bank | 05Z쯤 '90 cents' 제목으로 처음 발행된 뒤 시각이 다시 찍힘 |

## 4. 찾지 못한 것

- **AP, WSJ, FT, NYT 원문**: 접근이 막혀 있다. AP는 Fortune 전재본, FT는 Irish Times 전재본으로 대신했다.
- **Reuters의 3/8~3/9 SVB 기사**: 아카이브에서 URL을 찾지 못했다.
- **Circle 블로그 글 "An Update on USDC and Silicon Valley Bank"(3/11)**: 주소가 블로그 목록으로 넘어가고
  아카이브도 없다. Allaire 대표의 트윗(20:15Z)으로 대신했다.
- **3/6~3/10 오전에 Circle·USDC의 SVB 노출을 다룬 기사**: 없었다. 가장 이른 것은 03-10T19:35Z CoinDesk다.
- **USDC·Circle·보관 은행 이름이 들어간 평범한 제목(대조용)**: 2건뿐이다(#8 Bloomberg, #16 CoinDesk).
  나머지 대조용 3건은 일반 암호화폐 기사다.

## 5. 승인 때 봐 주실 것

1. 60건 선정이 사건을 고르게 덮는지, 빠진 중요한 기사가 있는지
2. 3절처럼 "제목이 바뀐 기사는 뺀다"는 규칙이 맞는지
3. 웹 아카이브 시각 12건, 전재본 시각 3건을 그대로 써도 되는지 (모두 늦은 쪽 오차)
