# 2023년 기사 표·은행 목록 검증 결과

최초 검증 2026-11-13 / 보관본 확인 이력 11-14 / 확인 결과 반영 2026-11-15 / 최종 재검토 수정 2차 (KST). 담당: 이원준.

기준: [SEJINKIM-git/depeg-early-warning](https://github.com/SEJINKIM-git/depeg-early-warning), main 커밋 `8ef6cac97e6b4f5f106c6ad80af1eca1955f2552`. 이번 수정은 제공된 Claude PDF와 사용자 직접 확인 결과를 반영한 문서 수정이다.

**판정: 은행 7곳 대조 완료, 일치. 기사 표 전체 승인은 보류한다.** 제목 변경 확인은 #11·24·41·43 네 건이다. #10·15는 기록 제목이 최초 발행 시각에 존재했다는 근거가 부족하다. 원 데이터·은행 코드·승인 상태·신호 파일은 이번 문서 수정으로 변경하지 않았다.

## 1. 핵심 요약과 확인 범위

- 은행 목록: 2023-01 보고서 각주 2와 2022-12 보고서 각주 10을 사용자가 직접 확인했다. 두 목록 모두 코드의 은행 7곳과 일치한다.
- 제목 변경: #11·24·41은 초기 보관본과 후판의 차이를 확인했다. #43은 매체 정정 문구로 DAI 삭제를 확인했다. #43의 정확한 최초 제목 전체와 공개 시각은 별도 미확인이다.
- #24·41은 11/14에 원 캡처가 재현되지 않았지만, 11/15에는 요청한 2023년 캡처가 재현됐다. 사용자도 초기 제목을 확인했다. 현재 판정의 '보관본 미확인'은 해제하고 과거 실패는 이력으로 남긴다.
- #11은 사용자 화면에서 두 링크 모두 60%로 열렸다. 추가 브라우저 확인에서는 초기판 50% 초과와 후기판 60%가 각각 표시됐다. 표시 차이의 원인은 미확정이며 사용자 확인과 추가 재현을 함께 기록한다.
- 누적 대조 기록상 뉴스 기사 31건은 현재 페이지 대조다. 현재 제목 확인과 최초 발행 당시 제목 확인은 구분한다. 다른 보관본 행도 캡처 시각보다 더 이른 제목 공개를 자동 보증하지 않는다.
- #33·41·46·50·54의 초 누락 외에도 소수초가 빠진 기사 10건과 SNS 4건을 추가 점검했다. 원시 정밀도 보완 대상은 총 19건이며 5-4절에 전부 적었다. #42는 판본별 시각 차이를 별도로 다룬다.
- #47은 날짜만 저장한다. 다음 날 00:00Z는 변환 로직의 결과이며 실제 공개 시각 확인값이 아니다.
- 리드타임의 기존 입력 결과는 v1 35시간, v2·v2.1 58시간이다. 잠정적인 뉴스 플래그 결과이며, 정정 입력 재계산이나 종합 점수 경보 발생 실적을 뜻하지 않는다.

## 2. 승인 전에 처리할 것

| 순서 | 처리할 일 | 대상 | 담당·상태 |
| --- | --- | --- | --- |
| 1 | 제목 판본과 available_at 정책 결정. 안 B는 최초 시각 근거가 있을 때만 사용 | #10·11·15·24·41·43 | 세진 / 결정 대기 |
| 2 | 현재 페이지 대조 기사 및 제목 시점 근거가 약한 행의 과거 판본 보강 | 뉴스 기사 31건. A/B 등급·CNBC 우선, #10·15 포함 | 원준 / 추가 검증 |
| 3 | 원시 초·소수초 보존, 현행 파서와 사용 시각 필드 매핑 결정 | 5-4절의 19건, #42 및 분 단위 행 | 세진 / 정책·데이터 반영 대기 |
| 4 | 날짜만 있는 입력의 시간대 가정과 사용 정책 또는 제외 결정 | #47 | 세진 / 결정 대기 |
| 5 | 입력과 규칙 버전 고정 후 뉴스 신호·리드타임 재계산 | 전체 | 담당자 / 미실행 |
| 6 | 남은 검증·정정 완료 후 기사 표 승인 상태 변경 PR | docs/news_2023_handpicked.md | 원준 / 아직 진행하지 않음 |

## 3. 기사 60건 대조 기록

제목 열과 기록 시각은 **원표의 입력값**이다. 잘못되거나 시점이 불확실한 제목도 비교를 위해 원표대로 남겼으며, 이 문서의 정정 제안이 원 JSON에 반영됐다는 뜻이 아니다. '일치'는 해당 대조 판본과의 일치이며 최초 제목 불변을 뜻하지 않는다.

근거 종류는 누적 기록 기준으로 2023년 3월 보관본 21건(뉴스 18, 공식 발표 #4·25·27), 2024년 보관본 1건(#47), 현재 페이지 38건(뉴스 31, SNS 4, 공식 발표 3)이다. 이번 11/15에 이 60건을 모두 새로 열었다는 뜻은 아니다.

| 행 | 원표 기록 시각 (UTC) | 매체·원표 제목 | 원문에서 확인한 시각 | 근거 판본 | 판정·조건 |
| --- | --- | --- | --- | --- | --- |
| #1 | 2023-03-07T22:44:37Z | Bloomberg: [Silvergate Is in Talks With FDIC Officials on Ways to Salvage Bank](https://www.bloomberg.com/news/articles/2023-03-07/silvergate-in-talks-with-fdic-officials-on-ways-to-salvage-bank) | 2023-03-07 22:44:37.431 UTC | [대조 근거](https://web.archive.org/web/20230308014111id_/https://www.bloomberg.com/news/articles/2023-03-07/silvergate-in-talks-with-fdic-officials-on-ways-to-salvage-bank) / 2023-03-08 01:41:11Z 캡처 | **판본 대조·소수초 보완 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #2 | 2023-03-07T23:00:41Z | CNBC: [Silvergate pops on report it's in talks with the FDIC to save the bank](https://www.cnbc.com/video/2023/03/07/silvergate-pops-on-report-its-in-talks-with-the-fdic-to-save-the-bank.html) | 2023-03-07 23:00:41+0000 | [대조 근거](https://www.cnbc.com/video/2023/03/07/silvergate-pops-on-report-its-in-talks-with-the-fdic-to-save-the-bank.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #3 | 2023-03-08T21:06:00Z | PR Newswire (SVB Financial Group press release): [SVB Financial Group Announces Proposed Offerings of Common Stock and Mandatory Convertible Preferred Stock](https://www.prnewswire.com/news-releases/svb-financial-group-announces-proposed-offerings-of-common-stock-and-mandatory-convertible-preferred-stock-301766247.html) | 2023-03-08 21:06:00 UTC | [대조 근거](https://www.prnewswire.com/news-releases/svb-financial-group-announces-proposed-offerings-of-common-stock-and-mandatory-convertible-preferred-stock-301766247.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #4 | 2023-03-08T21:30:00Z | Business Wire (Silvergate Capital press release): [Silvergate Capital Corporation Announces Intent to Wind Down Operations and Voluntarily Liquidate Silvergate Bank](https://www.businesswire.com/news/home/20230308005795/en/Silvergate-Capital-Corporation-Announces-Intent-to-Wind-Down-Operations-and-Voluntarily-Liquidate-Silvergate-Bank) | 2023-03-08 21:30:00 UTC | [대조 근거](https://web.archive.org/web/20230311223536id_/https://www.businesswire.com/news/home/20230308005795/en/Silvergate-Capital-Corporation-Announces-Intent-to-Wind-Down-Operations-and-Voluntarily-Liquidate-Silvergate-Bank) / 2023-03-11 22:35:36Z 캡처 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #5 | 2023-03-08T21:35:12Z | CNBC: [Crypto-focused bank Silvergate is shutting operations and liquidating after market meltdown](https://www.cnbc.com/2023/03/08/silvergate-shutting-down-operations-and-liquidating-bank.html) | 2023-03-08 21:35:12+0000 | [대조 근거](https://www.cnbc.com/2023/03/08/silvergate-shutting-down-operations-and-liquidating-bank.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #6 | 2023-03-08T21:41:13Z | CoinDesk: [Crypto Bank Silvergate Announces 'Voluntary Liquidation'](https://www.coindesk.com/policy/2023/03/08/crypto-bank-silvergate-announces-voluntary-liquidation) | 2023-03-08 21:41:13.841 UTC | [대조 근거](https://web.archive.org/web/20230308223442id_/https://www.coindesk.com/policy/2023/03/08/crypto-bank-silvergate-announces-voluntary-liquidation/) / 2023-03-08 22:34:42Z 캡처 | **과거 시각 확인**. 보관본의 03/08 21:41:13.841Z는 기존 값과 일치한다. 현재 CoinDesk 표시 시각과 다르므로 과거 메타데이터를 근거로 보존. 기존 값이 틀렸다고 판단할 근거는 아니다. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #7 | 2023-03-09T03:49:15Z | CoinDesk: [Crypto Stakeholders Say No Exposure to Shuttered Silvergate](https://www.coindesk.com/business/2023/03/09/crypto-stakeholders-say-no-exposure-to-shuttered-silvergate) | 2023-03-09 03:49:15.898 UTC | [대조 근거](https://web.archive.org/web/20230310165725id_/https://www.coindesk.com/business/2023/03/09/crypto-stakeholders-say-no-exposure-to-shuttered-silvergate/) / 2023-03-10 16:57:25Z 캡처 | **판본 대조·소수초 보완 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #8 | 2023-03-09T10:00:36Z | Bloomberg: [‘Transactions at The Speed of The Internet’: Circle CEO Jeremy Allaire on Stablecoins](https://www.bloomberg.com/news/articles/2023-03-09/circle-ceo-jeremy-allaire-on-us-crypto-regulation-stablecoins-usdc) | 2023-03-09 10:00:36.436 UTC | [대조 근거](https://web.archive.org/web/20230309195802id_/https://www.bloomberg.com/news/articles/2023-03-09/circle-ceo-jeremy-allaire-on-us-crypto-regulation-stablecoins-usdc) / 2023-03-09 19:58:02Z 캡처 | **판본 대조·소수초 보완 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #9 | 2023-03-09T12:35:11Z | CNBC: [Bitcoin, ether fall after go-to crypto bank Silvergate announces liquidation](https://www.cnbc.com/2023/03/09/bitcoin-ether-fall-after-go-to-crypto-bank-silvergate-announces-liquidation.html) | 2023-03-09 12:35:11+0000 | [대조 근거](https://www.cnbc.com/2023/03/09/bitcoin-ether-fall-after-go-to-crypto-bank-silvergate-announces-liquidation.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #10 | 2023-03-09T16:08:06Z | Bloomberg: [SVB Drops Most on Record as Startup Clients Face Cash Crunch](https://www.bloomberg.com/news/articles/2023-03-09/svb-plunges-most-since-1998-on-stock-offering-securities-sales) | 2023-03-09 16:08:06.143 UTC | [대조 근거](https://web.archive.org/web/20230310002958id_/https://www.bloomberg.com/news/articles/2023-03-09/svb-plunges-most-since-1998-on-stock-offering-securities-sales?cmpId=google) / 2023-03-10 00:29:58Z 캡처 | **제목 시점 근거 부족**. 제목은 03/10 00:29:58Z 보관본에서 확인. 최초 발행은 03/09 16:08:06.143Z, 판본 수정은 21:10:32.707Z. 이 자료만으로 제목 변경 시각을 확정할 수 없다. 안전한 사용 시각으로 캡처 시각을 제안한다. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #11 | 2023-03-09T19:33:04Z | CNBC: [Shares of SVB Financial fall 60% as tech-focused bank looks to raise more cash](https://www.cnbc.com/2023/03/09/svb-financial-falls-more-than-50percent-as-tech-bank-looks-to-raise-more-cash.html) | 2023-03-09 19:33:04 UTC | [대조 근거](https://web.archive.org/web/20230309194413id_/https://www.cnbc.com/2023/03/09/svb-financial-falls-more-than-50percent-as-tech-bank-looks-to-raise-more-cash.html) / 2023-03-09 19:44:13Z 캡처 | **제목 변경 확인**. 19:44:13Z 및 20:52:28Z 보관본은 more than 50%, 22:14:41Z는 60%. 11/15 브라우저에서도 두 제목을 각각 확인했다. 사용자 화면에서는 둘 다 60%로 열렸다는 이력을 함께 남긴다. 최초 발행 시각에 초기 제목을 소급하는 안 B는 별도 근거가 필요하다. |
| #12 | 2023-03-09T20:00:20Z | TechCrunch: [Silvergate’s shiny hinges have rusted as the crypto bank plans to shut down](https://techcrunch.com/2023/03/09/silvergates-shiny-hinges-have-rusted-as-the-crypto-bank-plans-to-shut-down/) | 2023-03-09 20:00:20+00:00 | [대조 근거](https://techcrunch.com/podcast/silvergates-shiny-hinges-have-rusted-as-the-crypto-bank-plans-to-shut-down/) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #13 | 2023-03-09T20:14:01Z | CoinDesk: [MakerDAO Founder Calls for Rebranding of DAI Stablecoin](https://www.coindesk.com/business/2023/03/09/makerdao-founder-calls-for-rebranding-of-dai-stablecoin/) | 2023-03-09 20:14:01.808 UTC | [대조 근거](https://web.archive.org/web/20230311145327id_/https://www.coindesk.com/business/2023/03/09/makerdao-founder-calls-for-rebranding-of-dai-stablecoin/) / 2023-03-11 14:53:27Z 캡처 | **판본 대조·소수초 보완 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #14 | 2023-03-09T20:40:55Z | TechCrunch: [Venture firms are advising portfolio companies to move money out of SVB](https://techcrunch.com/2023/03/09/silicon-valley-bank-firms-reactions/) | 2023-03-09 20:40:55+00:00 | [대조 근거](https://techcrunch.com/2023/03/09/silicon-valley-bank-firms-reactions/) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #15 | 2023-03-09T20:53:52Z | Bloomberg: [Thiel Fund, Venture Firms Advise Companies to Pull Money From SVB](https://www.bloomberg.com/news/articles/2023-03-09/svb-ceo-becker-asks-silicon-valley-bank-clients-to-stay-calm) | 2023-03-09 20:53:52.443 UTC | [대조 근거](https://web.archive.org/web/20230310005643id_/https://www.bloomberg.com/news/articles/2023-03-09/svb-ceo-becker-asks-silicon-valley-bank-clients-to-stay-calm) / 2023-03-10 00:56:43Z 캡처 | **제목 시점 보류**. 기록된 제목은 03/10 00:56:43Z 스냅샷에서 확인. 그 페이지의 수정 시각은 00:01:36.382Z. 최초 발행 03/09 20:53:52Z에 소급 적용할 수 없음. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #16 | 2023-03-09T21:39:47Z | CoinDesk: [Voyager Continues Liquidating Crypto Assets for Circle’s USDC Stablecoin](https://www.coindesk.com/business/2023/03/09/voyager-continues-liquidating-crypto-assets-for-circles-usdc-stablecoin/) | 2023-03-09 21:39:47.143 UTC | [대조 근거](https://web.archive.org/web/20230310002300id_/https://www.coindesk.com/business/2023/03/09/voyager-continues-liquidating-crypto-assets-for-circles-usdc-stablecoin/) / 2023-03-10 00:23:00Z 캡처 | **판본 대조·소수초 보완 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #17 | 2023-03-09T22:11:27Z | Bloomberg: [Peter Thiel’s Founders Fund Advises Companies to Withdraw Money From SVB](https://www.bloomberg.com/news/articles/2023-03-09/founders-fund-advises-companies-to-withdraw-money-from-svb) | 2023-03-09 22:11:27.741 UTC | [대조 근거](https://web.archive.org/web/20230309223412id_/https://www.bloomberg.com/news/articles/2023-03-09/founders-fund-advises-companies-to-withdraw-money-from-svb) / 2023-03-09 22:34:12Z 캡처 | **판본 대조·소수초 보완 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #18 | 2023-03-10T02:56:29Z | The Block: [Crypto VCs urge portfolio companies to pull funds from Silicon Valley Bank](https://www.theblock.co/post/218664/crypto-vcs-urge-portfolio-companies-to-pull-funds-from-silicon-valley-bank) | 2023-03-10 02:56 UTC | [대조 근거](https://www.theblock.co/post/218664/crypto-vcs-urge-portfolio-companies-to-pull-funds-from-silicon-valley-bank) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #19 | 2023-03-10T03:54:18Z | CNN (Reuters 전재): [Silicon Valley Bank scrambles to reassure clients after 60% stock wipe-out](https://www.cnn.com/2023/03/09/investing/silicon-valley-bank/index.html) | 2023-03-10 03:54:18 UTC | [대조 근거](https://web.archive.org/web/20230310041856id_/https://www.cnn.com/2023/03/09/investing/silicon-valley-bank/index.html) / 2023-03-10 04:18:56Z 캡처 | **수정판 시각 확인**. 접근 불가 판정을 해제한다. CNN 보관본의 제목은 일치하며 본문 출처는 Reuters다. 메타데이터는 03/10 03:54:18Z, 화면은 03/09 10:54PM ET Updated로 표시한다. 이는 이 판본의 수정 시각 근거이며 최초 발행 시각의 확정은 아니다. |
| #20 | 2023-03-10T10:29:41Z | The Irish Times (Financial Times syndication): [Startup world spooked as Silicon Valley Bank races to prevent bank run](https://www.irishtimes.com/business/financial-services/2023/03/10/startup-world-spooked-as-silicon-valley-bank-races-to-prevent-bank-run) | 2023-03-10 10:29:41.969 UTC | [대조 근거](https://www.irishtimes.com/business/financial-services/2023/03/10/startup-world-spooked-as-silicon-valley-bank-races-to-prevent-bank-run/) / 현재 페이지 | **판본 대조·소수초 보완 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #21 | 2023-03-10T13:08:00Z | CoinDesk: [Cathie Wood's Ark Invest Buys $22M in Coinbase Shares](https://www.coindesk.com/business/2023/03/10/cathie-woods-ark-purchases-over-350k-coinbase-shares-in-biggest-buy-of-2023) | 2023-03-10 13:08 UTC | [대조 근거](https://www.coindesk.com/business/2023/03/10/cathie-woods-ark-purchases-over-350k-coinbase-shares-in-biggest-buy-of-2023) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #22 | 2023-03-10T14:56:03Z | The Block: [Silicon Valley Bank plunges 60% before halt, Signature trading stopped shortly after open](https://www.theblock.co/post/218783/silicon-valley-bank-plunges-60-before-halt-signature-trading-stopped-shortly-after-open) | 2023-03-10 14:56 UTC | [대조 근거](https://www.theblock.co/post/218783/silicon-valley-bank-plunges-60-before-halt-signature-trading-stopped-shortly-after-open) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #23 | 2023-03-10T16:01:46Z | CNBC: [Crypto bank Signature slides on Friday amid troubles at Silicon Valley Bank, Silvergate](https://www.cnbc.com/2023/03/10/crypto-bank-signature-slides-on-friday-amid-troubles-at-silicon-valley-bank-silvergate.html) | 2023-03-10 16:01:46+0000 | [대조 근거](https://www.cnbc.com/2023/03/10/crypto-bank-signature-slides-on-friday-amid-troubles-at-silicon-valley-bank-silvergate.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #24 | 2023-03-10T16:46:09Z | CNBC: [Silicon Valley Bank is shut down by regulators in biggest bank failure since global financial crisis](https://www.cnbc.com/2023/03/10/silicon-valley-bank-is-shut-down-by-regulators-fdic-to-protect-insured-deposits.html) | 2023-03-10 16:46:09 UTC | [대조 근거](https://web.archive.org/web/20230310164812id_/https://www.cnbc.com/2023/03/10/silicon-valley-bank-is-shut-down-by-regulators-fdic-to-protect-insured-deposits.html) / 2023-03-10 16:48:12Z 캡처 | **제목 변경 확인**. 16:48:12Z 초기 캡처 제목은 FDIC to protect insured deposits 형태. 11/15 원 캡처 재현 및 사용자 제목 확인 완료. 11/14에 다른 캡처가 열렸던 일은 확인 이력으로 보존한다. 초기 제목 사용 시 안 A는 캡처 시각이다. |
| #25 | 2023-03-10T16:46:33Z | FDIC (press release): [FDIC Creates a Deposit Insurance National Bank of Santa Clara to Protect Insured Depositors of Silicon Valley Bank, Santa Clara, California](https://www.fdic.gov/news/press-releases/2023/pr23016.html) | 2023-03-10 16:46:33 UTC (공개 확인 상한) | [대조 근거](https://web.archive.org/web/20230310164633id_/https://www.fdic.gov/news/press-releases/2023/pr23016.html) / 2023-03-10 16:46:33Z 캡처 | **공개 확인 시각으로 사용 가능**. 16:46:33Z 스냅샷에서 제목과 내용을 확인했다. 정확한 발행 시각은 아니지만 해당 내용의 공개 확인 상한으로 사용할 수 있다. 이는 원 JSON note에도 이미 적혀 있다. 가장 이른 캡처 여부는 별도 보증하지 않는다. |
| #26 | 2023-03-10T16:50:00Z | CoinDesk: [Silicon Valley Bank Shuttered by State Regulators](https://www.coindesk.com/policy/2023/03/10/silicon-valley-bank-shuttered-by-state-regulators) | 2023-03-10 16:50 UTC | [대조 근거](https://www.coindesk.com/policy/2023/03/10/silicon-valley-bank-shuttered-by-state-regulators) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #27 | 2023-03-10T16:51:47Z | California DFPI (press release): [California Financial Regulator Takes Possession of Silicon Valley Bank](https://dfpi.ca.gov/2023/03/10/california-financial-regulator-takes-possession-of-silicon-valley-bank/) | 2023-03-10 16:51:47 UTC (공개 확인 상한) | [대조 근거](https://web.archive.org/web/20230310165147id_/https://dfpi.ca.gov/2023/03/10/california-financial-regulator-takes-possession-of-silicon-valley-bank/) / 2023-03-10 16:51:47Z 캡처 | **공개 확인 시각으로 사용 가능**. 16:51:47Z 스냅샷에서 제목과 내용을 확인했다. 정확한 발행 시각은 아니지만 공개 확인 상한으로 사용할 수 있다. 원 JSON note가 이미 상한임을 설명한다. 가장 이른 캡처 여부는 별도 보증하지 않는다. |
| #28 | 2023-03-10T16:55:48Z | Fortune (AP wire copy, byline The Associated Press / Ken Sweet): [Silicon Valley Bank has officially failed after less than a day of panicked selling as the federal government takes it over](https://fortune.com/2023/03/10/silicon-valley-bank-seized-regulators-bank-failure/) | 2023-03-10 16:55:48-00:00 | [대조 근거](https://fortune.com/2023/03/10/silicon-valley-bank-seized-regulators-bank-failure/) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #29 | 2023-03-10T16:56:10Z | The Block: [Silicon Valley Bank closed by California regulator](https://www.theblock.co/post/218838/silicon-valley-bank-closed-by-california-regulator) | 2023-03-10 16:56 UTC | [대조 근거](https://www.theblock.co/post/218838/silicon-valley-bank-closed-by-california-regulator) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #30 | 2023-03-10T17:04:52Z | Cointelegraph: [Silicon Valley Bank shut down by California regulator](https://cointelegraph.com/news/silicon-valley-bank-shut-down-by-california-regulator) | 2023-03-10 17:04:52.000 UTC | [대조 근거](https://cointelegraph.com/news/silicon-valley-bank-shut-down-by-california-regulator) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #31 | 2023-03-10T19:35:00Z | CoinDesk: [Scrutiny Falls on $43B USDC Stablecoin’s Cash Reserves at Failed Silicon Valley Bank](https://www.coindesk.com/markets/2023/03/10/scrutiny-falls-on-43b-usdc-stablecoins-cash-reserves-at-failed-silicon-valley-bank) | 2023-03-10 19:35 UTC | [대조 근거](https://www.coindesk.com/markets/2023/03/10/scrutiny-falls-on-43b-usdc-stablecoins-cash-reserves-at-failed-silicon-valley-bank) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #32 | 2023-03-10T20:53:13Z | TechCrunch: [Uncertainty stands around multibillion USDC empire as issuer Circle held reserves at Silicon Valley Bank](https://techcrunch.com/2023/03/10/uncertainty-stands-around-multi-billion-usdc-empire-as-issuer-circle-held-reserves-at-silicon-valley-bank/) | 2023-03-10 20:53:13+00:00 | [대조 근거](https://techcrunch.com/2023/03/10/uncertainty-stands-around-multi-billion-usdc-empire-as-issuer-circle-held-reserves-at-silicon-valley-bank/) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #33 | 2023-03-11T00:01:00Z | CoinDesk: [USDC Stablecoin Depegs From $1; Circle Says Operations Are Normal](https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-depegs-from-1-circle-says-operations-are-normal) | 2023-03-11 00:01:50.050 UTC | [대조 근거](https://web.archive.org/web/20230311002915id_/https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-depegs-from-1-circle-says-operations-are-normal/) / 2023-03-11 00:29:15Z 캡처 | **제목 대조·시각 정정 필요**. 00:29:15Z 보관본의 제목이 기존 표와 같다. 발행 메타데이터는 00:01:50.050Z다. 02:54Z 업데이트 전에도 같은 제목이 존재했으므로, 지난 보고서의 그 업데이트를 근거로 한 제목 변경 의심은 해제한다. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #34 | 2023-03-11T00:05:00Z | CoinDesk: [USDC Issuer Circle Says It 'Awaits Clarity' From FDIC on Silicon Valley Bank Collapse](https://www.coindesk.com/business/2023/03/11/usdc-issuer-circle-says-it-awaits-clarity-from-fdic-on-silicon-valley-bank-collapse) | 2023-03-11 00:05 UTC | [대조 근거](https://www.coindesk.com/business/2023/03/11/usdc-issuer-circle-says-it-awaits-clarity-from-fdic-on-silicon-valley-bank-collapse) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #35 | 2023-03-11T01:12:14Z | Binance (tweet, @binance): [Binance has temporarily suspended auto-conversion of USDC to BUSD due to current market conditions, specifically related to high inflows & the increasing burden to support the conversion. This is a normal risk-management procedural step to take while we monitor the situation.](https://twitter.com/binance/status/1634361554543030273) | 2023-03-11 01:12:14.229 UTC (ID 생성) | [대조 근거](https://x.com/binance/status/1634361554543030273) / 현재 페이지 | **SNS 전문 일치**. 게시자 Binance와 01:12:14Z 확인. 문서의 표시만 줄였고 JSON에는 게시글 전문이 있다. 원문과 JSON 전문의 문구가 일치함. 페이지 메타데이터는 2023-03-11 01:12:14.000 UTC처럼 초 단위로 표시한다. 별도로 ID에서 계산한 생성 시각의 밀리초를 보완했으며, 이를 실제 응답의 공개 확인 시각과 구분한다. 원표의 초 단위 값과 ID 정밀도를 함께 보존하고 사용 정책을 결정한다. |
| #36 | 2023-03-11T03:11:15Z | Circle (tweet, @circle): [1/ Following the confirmation at the end of today that the wires initiated on Thursday to remove balances were not yet processed, $3.3 billion of the ~$40 billion of USDC reserves remain at SVB.](https://twitter.com/circle/status/1634391505988206592) | 2023-03-11 03:11:15.210 UTC (ID 생성) | [대조 근거](https://x.com/circle/status/1634391505988206592) / 현재 페이지 | **SNS 전문 일치**. 게시자 Circle과 03:11:15Z 확인. 문서의 표시만 줄였고 JSON 전문에는 USDC·SVB 맥락도 들어 있다. 원문과 JSON 전문의 문구가 일치함. 페이지 메타데이터는 2023-03-11 03:11:15.000 UTC처럼 초 단위로 표시한다. 별도로 ID에서 계산한 생성 시각의 밀리초를 보완했으며, 이를 실제 응답의 공개 확인 시각과 구분한다. 원표의 초 단위 값과 ID 정밀도를 함께 보존하고 사용 정책을 결정한다. |
| #37 | 2023-03-11T03:26:00Z | The Block: [Circle says $3.3 billion of USDC reserves are with Silicon Valley Bank](https://www.theblock.co/post/218971/circle-says-3-3-billion-of-usdc-reserves-are-with-silicon-valley-bank) | 2023-03-11 03:26 UTC | [대조 근거](https://www.theblock.co/post/218971/circle-says-3-3-billion-of-usdc-reserves-are-with-silicon-valley-bank) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #38 | 2023-03-11T03:41:09Z | Coinbase (tweet, @coinbase): [We are temporarily pausing USDC:USD conversions over the weekend while banks are closed. During periods of heightened activity, conversions rely on USD transfers from the banks that clear during normal banking hours. When banks open on Monday, we plan to re-commence conversions.](https://twitter.com/coinbase/status/1634399032767307776) | 2023-03-11 03:41:09.734 UTC (ID 생성) | [대조 근거](https://x.com/coinbase/status/1634399032767307776) / 현재 페이지 | **SNS 전문 일치**. 게시자 Coinbase와 03:41:09Z 확인. 문서의 표시만 줄였고 JSON에는 게시글 전문이 있다. 원문과 JSON 전문의 문구가 일치함. 페이지 메타데이터는 2023-03-11 03:41:09.000 UTC처럼 초 단위로 표시한다. 별도로 ID에서 계산한 생성 시각의 밀리초를 보완했으며, 이를 실제 응답의 공개 확인 시각과 구분한다. 원표의 초 단위 값과 ID 정밀도를 함께 보존하고 사용 정책을 결정한다. |
| #39 | 2023-03-11T03:52:00Z | CoinDesk: [Circle Confirms $3.3B of USDC's Cash Reserves Stuck at Failed Silicon Valley Bank](https://www.coindesk.com/business/2023/03/11/circle-confirms-33b-of-usdcs-cash-reserves-stuck-at-failed-silicon-valley-bank) | 2023-03-11 03:52 UTC | [대조 근거](https://www.coindesk.com/business/2023/03/11/circle-confirms-33b-of-usdcs-cash-reserves-stuck-at-failed-silicon-valley-bank) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #40 | 2023-03-11T05:05:14Z | Cointelegraph: [USDC depegs as Circle confirms $3.3B stuck with Silicon Valley Bank](https://cointelegraph.com/news/usdc-depegs-as-circle-confirms-3-3b-stuck-with-silicon-valley-bank) | 2023-03-11 05:05:14.000 UTC | [대조 근거](https://cointelegraph.com/news/usdc-depegs-as-circle-confirms-3-3b-stuck-with-silicon-valley-bank) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #41 | 2023-03-11T05:51:00Z | CoinDesk: [USDC Stablecoin Depegs, Crypto Market Goes Haywire After Silicon Valley Bank Collapses](https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-and-crypto-market-go-haywire-after-silicon-valley-bank-collapses) | 2023-03-11 05:51:23.756 UTC | [대조 근거](https://web.archive.org/web/20230311071031id_/https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-and-crypto-market-go-haywire-after-silicon-valley-bank-collapses/) / 2023-03-11 07:10:31Z 캡처 | **제목 변경·시각 정정 필요**. 07:10:31Z 초기 캡처는 and Crypto Market Go Haywire 형태이며 현재 원표 제목과 다르다. 11/15 원 캡처 재현 및 사용자 제목 확인 완료. 원문 발행 05:51:23.756Z도 보존해야 한다. 초기 제목의 v2.1 등급은 B이며, 원표의 후판 제목 등급 A와 구분한다. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #42 | 2023-03-11T07:26:23Z | Reuters: [Crypto firm Circle reveals $3.3 bln exposure to Silicon Valley Bank](https://www.reuters.com/business/crypto-firm-circle-reveals-33-bln-exposure-silicon-valley-bank-2023-03-11/) | 2023-03-11 07:25:40 UTC | [대조 근거](https://web.archive.org/web/20230311080308id_/https://www.reuters.com/business/crypto-firm-circle-reveals-33-bln-exposure-silicon-valley-bank-2023-03-11/) / 2023-03-11 08:03:08Z 캡처 | **초기 제목 확인·시각 필드 차이**. 08:03:08Z 초기 Reuters 캡처에서 제목을 확인했다. 초기 published_time은 07:25:40Z, 후판 내부 값은 07:26:23.713Z다. 기존 07:26:23Z는 초기 값보다 늦지만 후판 값의 소수초를 버렸다. 필드 선택과 정밀도를 함께 기록한다. |
| #43 | 2023-03-11T10:10:40Z | The Block: [USDC remains at about $0.90 following Circle's disclosure of funds at SVB](https://www.theblock.co/post/218993/usdc-and-dai-remain-at-about-0-90-following-circles-disclosure-of-funds-at-svb) | 2023-03-11 10:10 UTC | [대조 근거](https://www.theblock.co/news/markets/2023-03-11-usdc-and-dai-remain-at-about-0-90-following-circles-disclosure-of-funds-at-svb-218993) / 현재 페이지 | **제목 정정 확인·초기 시각 보류**. 기사 하단 정정 문구가 제목에서 DAI를 제거했다고 밝힌다. 사용자도 확인했다. 최초 제목의 정확한 전체 문구와 공개 시각은 아직 확정하지 못했다. URL로 복원한 제목에 10:10:40Z를 붙여 확정하지 않는다. |
| #44 | 2023-03-11T16:03:23Z | CNBC: [Stablecoin USDC breaks dollar peg after firm reveals it has $3.3 billion in SVB exposure](https://www.cnbc.com/2023/03/11/stablecoin-usdc-breaks-dollar-peg-after-firm-reveals-it-has-3point3-billion-in-svb-exposure.html) | 2023-03-11 16:03:23+0000 | [대조 근거](https://www.cnbc.com/2023/03/11/stablecoin-usdc-breaks-dollar-peg-after-firm-reveals-it-has-3point3-billion-in-svb-exposure.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #45 | 2023-03-11T20:15:49Z | Circle (CEO Jeremy Allaire tweet announcing Circle blog post 'An Update on USDC and Silicon Valley Bank'): [Sharing an Update on USDC and Silicon Valley Bank.](https://twitter.com/jerallaire/status/1634649346535833601) | 2023-03-11 20:15:49.187 UTC (ID 생성) | [대조 근거](https://x.com/jerallaire/status/1634649346535833601) / 현재 페이지 | **출처 표기 보완 권장**. 문구와 20:15:49Z는 확인됐다. 게시 계정은 @jerallaire이므로 Circle CEO 개인 계정으로 구체화하면 좋다. 제목·시간 오류는 아니다. 페이지 메타데이터는 2023-03-11 20:15:49 UTC처럼 초 단위로 표시한다. 별도로 ID에서 계산한 생성 시각의 밀리초를 보완했으며, 이를 실제 응답의 공개 확인 시각과 구분한다. 원표의 초 단위 값과 ID 정밀도를 함께 보존하고 사용 정책을 결정한다. |
| #46 | 2023-03-11T20:58:00Z | CoinDesk: [Circle to ‘Cover Any Shortfall’ in USDC Reserves, Sparking Stablecoin Rally](https://www.coindesk.com/business/2023/03/11/circle-to-cover-any-shortfall-in-usdc-reserves-sparking-stablecoin-rally) | 2023-03-11 20:58:36.640 UTC | [대조 근거](https://web.archive.org/web/20230312012118id_/https://www.coindesk.com/business/2023/03/11/circle-to-cover-any-shortfall-in-usdc-reserves-sparking-stablecoin-rally/) / 2023-03-12 01:21:18Z 캡처 | **제목 대조·시각 정정 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #47 | 2023-03-12 | New York DFS (press release): [Superintendent Adrienne A. Harris Announces New York Department of Financial Services Takes Possession of Signature Bank](https://www.dfs.ny.gov/reports_and_publications/press_releases/pr20230312) | 2023-03-12 (날짜만; UTC 시각 미확인) | [대조 근거](https://web.archive.org/web/20240113192024id_/https://www.dfs.ny.gov/reports_and_publications/press_releases/pr20230312) / 2024-01-13 19:20:24Z 캡처 | **날짜만 확인**. 원 JSON의 published_at은 2023-03-12라는 날짜다. 03/13 00:00Z는 usable_from()의 변환 결과이며 확인된 발행 시각이 아니다. 뉴욕 현지 날짜라는 가정이면 그날 종료는 03/13 04:00Z. 가정을 명시한 사용 정책 또는 제외를 결정해야 한다. |
| #48 | 2023-03-12T22:15:00Z | Federal Reserve Board (joint press release): [Joint Statement by Treasury, Federal Reserve, and FDIC](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230312b.htm) | 2023-03-12 22:15 UTC | [대조 근거](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230312b.htm) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #49 | 2023-03-12T22:24:20Z | CNBC: [Regulators close crypto-focused Signature Bank, citing systemic risk](https://www.cnbc.com/2023/03/12/regulators-close-new-yorks-signature-bank-citing-systemic-risk.html) | 2023-03-12 22:24:20+0000 | [대조 근거](https://www.cnbc.com/2023/03/12/regulators-close-new-yorks-signature-bank-citing-systemic-risk.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #50 | 2023-03-12T22:25:00Z | CoinDesk: [Crypto-Friendly Signature Bank Shut Down by State Regulators](https://www.coindesk.com/policy/2023/03/12/crypto-friendly-signature-bank-shut-down-by-state-regulators-fed) | 2023-03-12 22:25:41.430 UTC | [대조 근거](https://web.archive.org/web/20230312224421id_/https://www.coindesk.com/policy/2023/03/12/crypto-friendly-signature-bank-shut-down-by-state-regulators-fed/) / 2023-03-12 22:44:21Z 캡처 | **제목 대조·시각 정정 필요**. 22:44:21Z 보관본 제목이 기존 표와 같다. 발행 메타데이터는 22:25:41.430Z다. URL 끝 -fed만으로 제목이 축약됐다고 의심한 지난 판단을 해제한다. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #51 | 2023-03-12T23:05:51Z | Fortune (Bloomberg syndicated): [NYC-based Signature Bank fails, and banking regulators invoke ‘systemic risk exception’ for all depositors being made whole](https://fortune.com/2023/03/12/nyc-based-signature-bank-fails-closed-by-regulators-fdic-treasury/) | 2023-03-12 23:05:51-00:00 | [대조 근거](https://fortune.com/2023/03/12/nyc-based-signature-bank-fails-closed-by-regulators-fdic-treasury/) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #52 | 2023-03-12T23:46:43Z | The Block: [Circle USDC operations will resume when U.S. banks open Monday: CEO Allaire](https://www.theblock.co/post/219133/circle-usdc-operations-will-resume-at-open-monday-allaire) | 2023-03-12 23:46 UTC | [대조 근거](https://www.theblock.co/post/219133/circle-usdc-operations-will-resume-at-open-monday-allaire) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #53 | 2023-03-13T00:24:00Z | Cointelegraph: [USDC bounces back toward $1 peg after Fed announcement](https://cointelegraph.com/news/usdc-bounces-back-towards-1-peg-after-fed-announcement) | 2023-03-13 00:24:00.000 UTC | [대조 근거](https://cointelegraph.com/news/usdc-bounces-back-towards-1-peg-after-fed-announcement) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #54 | 2023-03-13T01:55:00Z | CoinDesk: [Circle Scrambles to Right USDC After Signature Bank Failure](https://www.coindesk.com/policy/2023/03/12/circle-scrambles-to-right-usdc-after-signature-bank-failure/) | 2023-03-13 01:55:18.818 UTC | [대조 근거](https://web.archive.org/web/20230313174111id_/https://www.coindesk.com/policy/2023/03/12/circle-scrambles-to-right-usdc-after-signature-bank-failure/) / 2023-03-13 17:41:11Z 캡처 | **제목 대조·시각 정정 필요**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. 원표 시각은 원시 초·소수초를 버렸다. 정밀도는 5-4절의 19건 표와 같이 보존하고 사용 시각 변환을 별도로 결정한다. |
| #55 | 2023-03-13T03:56:37Z | Fortune: [Circle adds Cross River as banking partner and expands BNY ties, USDC peg closes](https://fortune.com/crypto/2023/03/12/circle-adds-cross-river-as-banking-partner-and-expands-bny-ties-usdc-peg-closes/) | 2023-03-13 03:56:37-00:00 | [대조 근거](https://fortune.com/crypto/2023/03/12/circle-adds-cross-river-as-banking-partner-and-expands-bny-ties-usdc-peg-closes/) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #56 | 2023-03-13T10:00:00Z | Circle (press release via PR Newswire): [$3.3 Billion of USDC Reserve Risk Removed, Dollar De-peg Closes](https://www.prnewswire.com/news-releases/3-3-billion-of-usdc-reserve-risk-removed-dollar-de-peg-closes-301769820.html) | 2023-03-13 10:00:00 UTC | [대조 근거](https://www.prnewswire.com/news-releases/3-3-billion-of-usdc-reserve-risk-removed-dollar-de-peg-closes-301769820.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #57 | 2023-03-13T14:09:00Z | CoinDesk: [USDC Stablecoin Regains Dollar Peg After Silicon Valley Bank-Induced Chaos](https://www.coindesk.com/business/2023/03/13/usdc-stablecoin-regains-dollar-peg-after-silicon-valley-bank-induced-chaos) | 2023-03-13 14:09 UTC | [대조 근거](https://www.coindesk.com/business/2023/03/13/usdc-stablecoin-regains-dollar-peg-after-silicon-valley-bank-induced-chaos) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #58 | 2023-03-13T21:28:51Z | The Block: [Meta announces plans to stop working on NFTs](https://www.theblock.co/post/219462/meta-announces-plans-to-stop-working-on-nfts) | 2023-03-13 21:28 UTC | [대조 근거](https://www.theblock.co/post/219462/meta-announces-plans-to-stop-working-on-nfts) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #59 | 2023-03-14T08:52:29Z | CNBC (video): [Circle's CEO discusses the 'precautions' the company took after SVB's collapse](https://www.cnbc.com/video/2023/03/14/circle-ceo-discusses-precautions-the-company-took-after-svb-collapse.html) | 2023-03-14 08:52:29+0000 | [대조 근거](https://www.cnbc.com/video/2023/03/14/circle-ceo-discusses-precautions-the-company-took-after-svb-collapse.html) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |
| #60 | 2023-03-14T21:53:45Z | The Block: [Biggest USDC burn on record just occurred, net redemptions since Friday reach $4.5 billion](https://www.theblock.co/post/219887/biggest-usdc-burn-on-record-just-occurred-net-redemptions-since-friday-reach-4-5-billion) | 2023-03-14 21:53 UTC | [대조 근거](https://www.theblock.co/post/219887/biggest-usdc-burn-on-record-just-occurred-net-redemptions-since-friday-reach-4-5-billion) / 현재 페이지 | **기재값 일치**. 원문/보관본의 제목·매체와 분 단위 시각까지 일치. 최초 제목 불변을 별도로 입증한 판정은 아님. |

## 4. URL 주소와 제목 차이 - 단서와 확정 구분

URL과 제목의 차이는 변경 단서이며, 그 자체로 최초 제목이나 공개 시각을 입증하지 않는다. #11·24·41은 초기 판본으로, #43은 정정 문구로 제목 변경 사실을 확인했다.

| 행 | URL 또는 초기판의 단서 | 기록 제목과의 차이 | 판정 |
| --- | --- | --- | --- |
| #10 | svb-plunges-most-since-1998-on-stock-offering-securities-sales | SVB Drops Most on Record as Startup Clients Face Cash Crunch | 제목 시점 근거 부족. URL로 최초 제목을 확정하지 않음 |
| #15 | svb-ceo-becker-asks-silicon-valley-bank-clients-to-stay-calm | Thiel Fund, Venture Firms Advise Companies to Pull Money From SVB | 진정 요청과 인출 권고는 의미가 달라 시점 근거 중요 |
| #11 | 초기 more than 50% / 후기 60% | 초기판과 원표 제목 차이 | 변경 확인. 사용 시각은 정정 제안서 참조 |
| #24 | 초기 FDIC to protect insured deposits | 후기 biggest bank failure since global financial crisis | 변경 확인. 11/15 사용자 재현 완료 |
| #41 | 초기 and Crypto Market Go Haywire | 후기 Depegs, Crypto Market Goes Haywire | 변경 확인. 초기 제목 v2.1 B / 원표 후판 A |
| #43 | URL에는 USDC and DAI remain | 현재 USDC remains | DAI 삭제 정정 확인. 최초 제목 전체·시각 미확정 |
| #49·5 | 어휘·표현 길이 차이 | 은행 폐쇄·청산 핵심 표현은 유사 | 단서만으로 제목 변경을 확정하지 않음 |
| #21·8 | 주소와 표시 제목 표현 차이 | 투자·인터뷰 기사 | 단서와 실제 변경 확인을 구분 |

#52·53은 주소와 제목의 차이가 표기 수준이어서 위 문제 목록에 추가하지 않았다.

## 5. 원 기사 표 5장의 세 가지 질문

### 5-1. 빠진 중요한 기사가 있는가

SVB 증자 원 발표(#3), Silvergate 청산 원 발표(#4), SVB 폐쇄, Circle의 33억 달러 공개, 예금 보호와 USDC 회복 흐름은 들어 있다. 3/8 발표 두 건은 표 누락과 규칙의 탐지 누락을 구분해야 한다. 기존 v2.1은 #4·5·6에 B를 주지만 #3에는 여전히 등급을 주지 않는다.

추가 후보는 Circle의 2023-03-10 23:50:35Z 공식 게시글이다. SVB가 현금 준비금을 관리하는 은행 여섯 곳 중 하나라는 내용이며 #34가 인용한 발표다. 추가한다면 같은 사건 중복으로 표시한다. [Circle 공식 게시글](https://twitter.com/circle/status/1634341007306248199)

이 표가 당시 보도를 빠짐없이 포괄한다고 주장하지 않는다.

### 5-2. 제목이 바뀐 기사는 모두 제외해야 하는가

현재 제목을 과거 시각에 소급하지 않는 원칙이 중요하다. 기사를 통째로 제외하는 대신 source_published_at(원문 발행 시각), headline(판본 제목), available_at(그 제목을 확인한 시각), 근거 URL을 구분하도록 제안한다. 제안 정책을 적용하면 시간창은 t-24h 이상, t 미만의 사용 시각을 기준으로 한다.

안 A는 해당 제목을 확인한 가장 이른 확보 캡처 시각을 사용한다. 원문 발행보다 늦어질 수 있다. 안 B는 최초 제목이 발행 시점부터 같았다는 독립 근거가 있을 때만 가능하다. #11 안 B와 #43의 URL 복원 제목은 현재 승인하지 않는다. 기사 전체 수정 시각인 dateModified만으로 제목 변경 순간을 정하지 않는다.

현재 구현과 이 제안은 구분해야 한다. 기준 커밋의 엔진은 `available_at`이나 `source_published_at`을 읽지 않고 기존 `published_at`만 사용한다. 그 값은 날짜 또는 정수 초 UTC 형식이며 소수초 문자열을 그대로 넣으면 현재 파서가 거부한다. 원시 정밀도는 근거 자료·별도 필드에 보존하고, 현재 엔진을 유지해 적용한다면 결정한 사용 시각을 정수 초로 올려 신호용 `published_at`에 매핑해야 한다. 새 필드를 엔진이 직접 읽게 하려면 별도 코드 변경·검증이 필요하다. 이번 문서에서는 코드와 입력을 바꾸지 않았다. 현행 시간창은 `t-24h <= published_at < t`여서 t와 정확히 같은 시각의 입력도 제외한다. [현재 시각 처리 코드](https://github.com/SEJINKIM-git/depeg-early-warning/blob/8ef6cac97e6b4f5f106c6ad80af1eca1955f2552/src/intelligence/news_signal.py)

### 5-3. 웹 아카이브·전재본 시각을 사용해도 되는가

원 JSON의 time_confidence가 archive인 12건은 **#1·6·7·8·10·13·15·16·17·25·27·42**다. 그중 #25·27은 캡처 시각을 '늦어도 이때 공개돼 있었음'의 확인 시각으로 쓴다. 나머지는 보관본에서 읽은 발행 메타데이터다. 이 12건과, 검토 과정에서 추가로 보관본을 확보한 총 21건은 다른 집계다.

전재본은 네 건이다: #19 CNN/Reuters, #20 Irish Times/FT, #28 Fortune/AP, #51 Fortune/Bloomberg. 전재 매체 제목과 그 매체의 게시·수정 시각을 한 쌍으로 사용한다. 원 매체의 더 이른 시각을 자동으로 붙이지 않는다.

#47의 원 JSON 값은 `published_at: "2023-03-12"`다. 03/13 00:00Z는 usable_from()의 변환 결과다. 뉴욕 현지 3/12라는 가정이면 당일 종료는 서머타임 기준 03/13 04:00Z다. 해당 가정과 데이터 사용 정책을 명시하거나 제외한다. 실제 웹 공개 시각을 확인했다는 뜻은 아니다. 같은 사건의 #48·49도 있다.

### 5-4. 초·소수초 정밀도

| 행 | 원표 시각 | 확인한 원시 시각 (UTC) | 정수 초로 올린 시각 예 |
| --- | --- | --- | --- |
| #1 | 2023-03-07T22:44:37Z | 2023-03-07T22:44:37.431Z | 2023-03-07T22:44:38Z |
| #6 | 2023-03-08T21:41:13Z | 2023-03-08T21:41:13.841Z | 2023-03-08T21:41:14Z |
| #7 | 2023-03-09T03:49:15Z | 2023-03-09T03:49:15.898Z | 2023-03-09T03:49:16Z |
| #8 | 2023-03-09T10:00:36Z | 2023-03-09T10:00:36.436Z | 2023-03-09T10:00:37Z |
| #10 | 2023-03-09T16:08:06Z | 2023-03-09T16:08:06.143Z | 2023-03-09T16:08:07Z |
| #13 | 2023-03-09T20:14:01Z | 2023-03-09T20:14:01.808Z | 2023-03-09T20:14:02Z |
| #15 | 2023-03-09T20:53:52Z | 2023-03-09T20:53:52.443Z | 2023-03-09T20:53:53Z |
| #16 | 2023-03-09T21:39:47Z | 2023-03-09T21:39:47.143Z | 2023-03-09T21:39:48Z |
| #17 | 2023-03-09T22:11:27Z | 2023-03-09T22:11:27.741Z | 2023-03-09T22:11:28Z |
| #20 | 2023-03-10T10:29:41Z | 2023-03-10T10:29:41.969Z | 2023-03-10T10:29:42Z |
| #33 | 2023-03-11T00:01:00Z | 2023-03-11T00:01:50.050Z | 2023-03-11T00:01:51Z |
| #35 | 2023-03-11T01:12:14Z | 2023-03-11T01:12:14.229Z | 2023-03-11T01:12:15Z |
| #36 | 2023-03-11T03:11:15Z | 2023-03-11T03:11:15.210Z | 2023-03-11T03:11:16Z |
| #38 | 2023-03-11T03:41:09Z | 2023-03-11T03:41:09.734Z | 2023-03-11T03:41:10Z |
| #41 | 2023-03-11T05:51:00Z | 2023-03-11T05:51:23.756Z | 2023-03-11T05:51:24Z |
| #45 | 2023-03-11T20:15:49Z | 2023-03-11T20:15:49.187Z | 2023-03-11T20:15:50Z |
| #46 | 2023-03-11T20:58:00Z | 2023-03-11T20:58:36.640Z | 2023-03-11T20:58:37Z |
| #50 | 2023-03-12T22:25:00Z | 2023-03-12T22:25:41.430Z | 2023-03-12T22:25:42Z |
| #54 | 2023-03-13T01:55:00Z | 2023-03-13T01:55:18.818Z | 2023-03-13T01:55:19Z |

위 시각 예는 원시 시각만 정수 초로 올린 것으로 최종 available_at 승인값이 아니다. #10·11·15·24·41·43 같은 제목 시점 문제와 캡처 조건도 별도로 충족해야 한다. SNS #35·36·38·45의 밀리초는 ID 생성 시각 계산값이며 실제 응답으로 공개를 확인한 시각을 뜻하지 않는다. 계산식은 (ID >> 22) + 1288834974657 밀리초다. [Twitter 원 Snowflake 구현](https://github.com/twitter-archive/snowflake/blob/snowflake-2010/src/main/scala/com/twitter/service/snowflake/IdWorker.scala)

정확한 원시 시각을 보존하는 것이 우선이지만 소수초를 현행 published_at에 그대로 넣지는 않는다. 정수 초 사용 시각은 올림하고, 분 단위만 쓰면 다음 분으로 올릴 수 있다. #21·26·31·34·37·39·57처럼 초가 00인 분 단위 행은 정밀도 표시를 통일한다. #42는 초기·후기 판본의 값이 달라 3장에 따로 기록했다.

## 6. 은행 목록 확인 - 대조 완료

| 은행 | 2023-01 보고서 각주 2 | 2022-12 보고서 각주 10 | 코드의 2023-01 목록 |
| --- | --- | --- | --- |
| Bank of New York Mellon | 있음 | 있음 | 일치 |
| Citizens Trust Bank | 있음 | 있음 | 일치 |
| Customers Bank | 있음 | 있음 | 일치 |
| New York Community Bank | 있음 | 있음 | 일치 |
| Signature Bank | 있음 | 있음 | 일치 |
| Silicon Valley Bank | 있음 | 있음 | 일치 |
| Silvergate Bank | 있음 | 있음 | 일치 |

- [2023-01 보고서 원본](https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/USDCAttestationReports/2023%20USDC_Circle%20Examination%20Report%20January%202023.pdf): 문서 날짜 2023-03-02, PDF 5쪽 각주 2. SHA-256: `6dbd9dffe1a399ee4f2cbc11a41824e99df04f8b65ff0b279aa09a30d5fb77c6`.
- [2022-12 보고서 원본](https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/USDCAttestationReports/2022/2022%20USDC%20Circle%20Grant%20Thornton%20Report%20December.pdf): 문서 날짜 2023-01-25, PDF 6쪽 각주 10. SHA-256: `ed20b46f081b0cdd9de226611cfdcc586ee3ac6736c35d7822174fb89053c40a`.

사용자가 두 각주를 직접 확인했다. 파일 해시 일치는 이전 대조 기록의 결과다. Flagstar는 New York Community Bank의 부연으로 적혀 있으며 별도 여덟 번째 은행으로 세지 않는다. 문서 날짜와 실제 웹 공개 시각을 구분한다.

## 7. 규칙 버전·리드타임 - 기존 입력의 잠정 결과

같은 기준 커밋은 v1 35시간, v2·v2.1 58시간을 이미 구분한다. 실제 대시보드·엔진의 운영 배포 버전은 이 기록만으로 확인하지 않는다.

| 계산 기준 | 연속 뉴스 신호 시작 (UTC) | 최저점 전 | 시작 근거 |
| --- | --- | --- | --- |
| v1 (기존 등급) | 2023-03-09 21:00 | 35시간 | #12 TechCrunch |
| v2·v2.1 | 2023-03-08 22:00 | 58시간 | #4·5·6 Silvergate 청산 |
| v2.1에서 Silvergate 제목 제외 | 2023-03-09 20:00 | 36시간 | #11 SVB 주가 기사 |

가격만의 비교값은 -50bps 기준 이탈 03/11 05:00부터 최저점 08:00까지 3시간이다. 위 뉴스 수치는 기존 입력의 플래그 기준이며 전체 위험 점수가 실제 경보 임계값을 넘었다는 뜻이 아니다. 제목·시각 정정 후 다시 계산하기 전까지 잠정값이다. [원 리드타임 기록](https://github.com/SEJINKIM-git/depeg-early-warning/blob/8ef6cac97e6b4f5f106c6ad80af1eca1955f2552/docs/news_leadtime_2023.md)

기존 표와 v2.1의 등급 차이는 27건, A/B 플래그 차이는 24건이다. 원문 오류 27건이나 오탐 27건을 뜻하지 않는다.

| 행 | 원표 등급 | v2.1 원표 제목 등급 | A/B 플래그도 변함 |
| --- | --- | --- | --- |
| #1 | B | - | 예 |
| #2 | B | - | 예 |
| #4 | - | B | 예 |
| #5 | - | B | 예 |
| #6 | - | B | 예 |
| #7 | - | B | 예 |
| #9 | - | B | 예 |
| #11 | - | B | 예 |
| #14 | - | B | 예 |
| #15 | - | B | 예 |
| #17 | - | B | 예 |
| #18 | - | B | 예 |
| #25 | B | - | 예 |
| #26 | - | B | 예 |
| #27 | - | B | 예 |
| #29 | - | B | 예 |
| #32 | - | B | 예 |
| #34 | A | B | 아니오 |
| #35 | - | A | 예 |
| #37 | - | B | 예 |
| #39 | A | B | 아니오 |
| #42 | - | B | 예 |
| #43 | A | - | 예 |
| #44 | - | A | 예 |
| #47 | - | B | 예 |
| #56 | A | C | 예 |
| #59 | A | B | 아니오 |

위 등급 표는 **원표 제목**에 적용한 결과다. #41의 초기 제목을 쓰면 B이므로 표의 후판 A와 혼동하지 않는다. #25가 B에서 해당 없음으로 바뀐 것은 FDIC 단독 매칭 제거라는 버전 변경과 연결된다. Silvergate 청산 #4·5·6은 B, 회복 발표 #56은 C다.

## 8. 완료 범위와 확인 이력

| 작업 | 현재 상태 |
| --- | --- |
| 60건 대조 기록 | 누적 기록 보존. 현재 페이지 뉴스 31건의 당시 제목과 일부 사용 시각 추가 검증 필요 |
| #11·24·41 | 제목 판본 차이 확인. #11의 사용자 화면 재현 차이는 이력으로 남김 |
| #43 | DAI 삭제 정정 확인. 정확한 최초 제목 전체·공개 시각 미확정 |
| 은행 7곳 | 두 보고서 각주와 코드 대조 완료, 일치 |
| 평상시 기사 | 본표 21건 + 추가 후보 4건 유지. 라벨 최종 승인 대기 |
| 정정안·원 데이터 | 문서 수정 완료. 원 JSON·코드·신호 파일은 수정하지 않음 |
| 리드타임 | 버전 구분 확인. 정정 입력 재계산 미실행, 숫자 잠정 |
| 공유·승인 PR | 문안만 준비. 전송·승인 상태 변경·PR 생성하지 않음 |

11/14에는 #24·41의 원 캡처 재현이 실패했다. 11/15에는 정확한 캡처가 재현됐고 사용자도 초기 제목을 확인했다. #11은 추가 브라우저에서 19:44:13Z의 50% 초과와 22:14:41Z의 60%가 재현됐다. 원문 발행 시각까지 제목을 소급할 수 있는지는 별도 판정이다.

## 9. 단톡방 공유 문안 - 초안, 미전송

2023년 기사 60건·은행 목록 검증 결과입니다. 기준 커밋은 8ef6cac입니다.

- 은행 7곳은 2023-01·2022-12 보고서 각주 및 코드와 일치하며 직접 확인을 마쳤습니다.
- 제목 변경은 #11·24·41·43에서 확인했습니다. #24·41의 초기 보관본은 11/15 재현됐습니다. #11은 사용자 화면에서 두 링크가 같게 열린 이력을 남겼으며 추가 브라우저에서는 초기 50% 초과와 후기 60%가 확인됐습니다.
- #43은 DAI 삭제 사실만 확정이며 최초 제목 전체와 시각은 미확정입니다. #10·15도 최초 제목의 사용 시각 근거를 보강하거나 확보 캡처부터 사용해야 합니다.
- 초 누락 5건 외에 기사 소수초 10건과 SNS 생성 시각의 밀리초 4건을 더 확인했습니다. 총 19건과 #42의 판본 시각, #47의 날짜·시간대 정책을 정리해야 합니다. 현재 엔진은 새 시간 필드를 직접 읽거나 소수초를 파싱하지 못하므로 매핑·구현 검토도 필요합니다. 전재본은 #19·20·28·51 네 건입니다.
- v1 35시간, v2·v2.1 58시간은 기존 입력의 잠정 뉴스 플래그 결과입니다. 입력 정정 후 재계산이 필요하며 종합 경보 발생 실적은 아닙니다.
- 기사 표 전체 승인은 남은 검증과 정정이 완료된 뒤 진행하겠습니다. 평상시 자료는 본표 21건과 추가 후보 4건이며 라벨 최종 확인이 남아 있습니다.

## 부록. 이번 수정에서 반영한 내용

- #24·41 보관본 미확인 상태를 갱신하고 과거 접근 실패는 이력으로 보존했다.
- #11의 사용자 재현 차이와 추가 브라우저 확인을 함께 적었다. #11 안 B·#43 초기 제목 복원은 조건부로 남겼다.
- 원 JSON의 archive 12건과 검토 근거의 보관본 21건을 구분했다.
- #47의 원 JSON 날짜와 변환 결과를 구분하고, 소수초 보존·올림 예를 추가했다.
- 리드타임 버전과 근거 기사 번호를 명시했다. 은행 확인 완료를 반영했다.
- 평상시 기사 21건과 반례 4건을 보존했다. 취소선·None 및 표의 가독성 문제를 정리했다.
- 최종 재검토에서 소수초 점검 누락 14건과 제안 필드·현행 구현의 차이를 보완했다. 현행 창의 상한은 t 이하가 아니라 t 미만으로 바로잡았다.
- 리드타임 문서의 A등급 첫 근거 설명, 다음 버전 표기, 시간 종가의 관측 한계를 정리했다. 기존 입력의 35·58시간은 재현됐고 v2.1 플래그 120개는 저장값과 모두 같았다. 원시 가격 응답 파일은 로컬에 없어 가격 수집 원본까지 새로 검증한 것은 아니다.
