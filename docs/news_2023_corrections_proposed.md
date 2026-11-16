# 기사 표 정정 제안 - 원 데이터는 수정하지 않음

작성 2026-11-13 / 확인 결과 반영 2026-11-15 / 최종 재검토 수정 2차. 담당: 이원준. 기준 커밋: 8ef6cac.

**상태: 제안, 원 데이터 반영 대기.** #11·24·41은 제목 판본 차이 확인, #43은 DAI 삭제 정정 확인이다. #10·15와 #43 최초 제목의 공개 시각은 미확정이다. 기사 표 전체 승인 상태는 바꾸지 않았다.

## 1. 먼저 정할 것

- source_published_at: 원문에 적힌 발행 시각. 초·소수초 원시값을 보존한다.
- headline: 사용할 판본의 제목.
- available_at: 해당 제목이 공개돼 있었음을 확인한 사용 시각. 도입할 신호 기준 시각으로 제안한다.
- 근거 URL: 요청 주소, 실제 열린 주소, 캡처 시각, 읽은 제목을 함께 기록한다.

**안 A:** 그 제목을 직접 확인한 가장 이른 확보 캡처 시각을 사용한다. 확보한 캡처가 최초 웹 공개 순간이라는 뜻은 아니며 실제보다 늦어질 수 있다. 캡처의 본문·제목·실제 시각이 일치하는지 확인한다.

**안 B:** 초기 제목이 최초 발행 시각부터 같았다는 독립 근거를 직접 확보했을 때만 발행 시각을 사용한다. URL 주소·검색 결과·기사 전체 dateModified만으로 승인하지 않는다. 현재 #11의 안 B는 사용 보류다.

현재 구현과 이 제안은 구분해야 한다. 기준 커밋의 엔진은 `available_at`이나 `source_published_at`을 읽지 않고 기존 `published_at`만 사용한다. 그 값은 날짜 또는 정수 초 UTC 형식이며 소수초 문자열을 그대로 넣으면 현재 파서가 거부한다. 원시 정밀도는 근거 자료·별도 필드에 보존하고, 현재 엔진을 유지해 적용한다면 결정한 사용 시각을 정수 초로 올려 신호용 `published_at`에 매핑해야 한다. 새 필드를 엔진이 직접 읽게 하려면 별도 코드 변경·검증이 필요하다. 이번 문서에서는 코드와 입력을 바꾸지 않았다. 현행 시간창은 `t-24h <= published_at < t`여서 t와 정확히 같은 시각의 입력도 제외한다. [현재 시각 처리 코드](https://github.com/SEJINKIM-git/depeg-early-warning/blob/8ef6cac97e6b4f5f106c6ad80af1eca1955f2552/src/intelligence/news_signal.py)

## 2. 행별 제안

| 행 | 사용할 제목·판본 | source_published_at (UTC) | 안 A available_at (UTC) | 안 B·등급 |
| --- | --- | --- | --- | --- |
| #11 | Shares of SVB Financial fall more than 50% as tech-focused bank looks to raise more cash | 2023-03-09 19:33:04Z | 2023-03-09 19:44:13Z | 안 B 사용 보류 / 초기 제목 v2.1 B |
| #24 | Silicon Valley Bank is shut down by regulators, FDIC to protect insured deposits | 2023-03-10 16:46:09Z | 2023-03-10 16:48:12Z | 최초 시각 소급은 별도 근거 필요 / 초기 B |
| #41 | USDC Stablecoin and Crypto Market Go Haywire After Silicon Valley Bank Collapses | 2023-03-11 05:51:23.756Z | 2023-03-11 07:10:31Z | 최초 시각 소급은 별도 근거 필요 / 초기 B, 원표 후판 A |
| #10 | SVB Drops Most on Record as Startup Clients Face Cash Crunch | 2023-03-09 16:08:06.143Z | 2023-03-10 00:29:58Z | 안 B 근거 미충족 / 해당 없음 |
| #15 | Thiel Fund, Venture Firms Advise Companies to Pull Money From SVB | 2023-03-09 20:53:52.443Z | 2023-03-10 00:56:43Z | 안 B 근거 미충족 / B |
| #43 | 현재 제목 또는 초기 판본을 추가 확보해 선택 | 원표는 2023-03-11 10:10:40Z, 독립 대조는 분 단위 | 정확한 제목이 확인된 과거 판본 확보 필요 | URL 복원 제목에 최초 시각 사용 보류 / 현재 제목 해당 없음 |

## 3. 행별 근거와 확인 이력

### #11 - 초기판 50% 초과, 후기판 60%

[03/09 19:44:13Z 보관본](https://web.archive.org/web/20230309194413id_/https://www.cnbc.com/2023/03/09/svb-financial-falls-more-than-50percent-as-tech-bank-looks-to-raise-more-cash.html)과 [20:52:28Z 보관본](https://web.archive.org/web/20230309205228id_/https://www.cnbc.com/2023/03/09/svb-financial-falls-more-than-50percent-as-tech-bank-looks-to-raise-more-cash.html)은 초기 제목이며 [22:14:41Z 보관본](https://web.archive.org/web/20230309221441id_/https://www.cnbc.com/2023/03/09/svb-financial-falls-more-than-50percent-as-tech-bank-looks-to-raise-more-cash.html)은 60% 제목이다. 11/15 추가 브라우저에서도 초기·후기 제목을 각각 확인했다. 사용자는 두 링크 모두 60%로 열렸다고 보고했으며, 원인은 확정하지 않고 이력을 함께 남긴다.

안 B의 보강 근거인 [CNBC 전재 후보 페이지](https://business.dptribune.com/dptribune/news/read/43213603/shares_of_svb_financial_fall_more_than_50_as_tech)는 이전 검토에서 본문 직접 확인을 마치지 못했다. 초기 제목·전재 시각·출처를 직접 확인하기 전에는 안 B를 승인하지 않는다. 60% 제목을 사용하려면 현재 확보 근거상 22:14:41Z부터가 안 A다.

### #24 - 초기 캡처 재현 완료

[03/10 16:48:12Z 보관본](https://web.archive.org/web/20230310164812id_/https://www.cnbc.com/2023/03/10/silicon-valley-bank-is-shut-down-by-regulators-fdic-to-protect-insured-deposits.html)에서 FDIC 예금 보호를 언급한 제목을 확인했다. 11/15 요청한 원 캡처가 재현됐고 사용자도 같은 제목을 확인했다. 11/14 다른 캡처가 열렸던 실패 이력은 남기되, 현재의 미확인 상태는 해제한다. 안 A는 16:48:12Z다.

### #41 - 초기 캡처 재현 완료

[03/11 07:10:31Z 보관본](https://web.archive.org/web/20230311071031id_/https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-and-crypto-market-go-haywire-after-silicon-valley-bank-collapses/)의 제목은 and Crypto Market Go Haywire 형태다. 원시 발행 시각 05:51:23.756Z, 수정 시각 06:32:01.956Z를 보존한다. 11/15 원 캡처와 사용자 제목 확인이 일치했다. 초기 제목은 v2.1 B, 원표의 후판 제목은 A다. 둘 다 플래그 1이라는 사실과 제목을 언제 사용할 수 있는지는 별개다.

### #10·15 - 제목을 확인한 캡처부터 사용하는 안 A

[#10 보관본](https://web.archive.org/web/20230310002958id_/https://www.bloomberg.com/news/articles/2023-03-09/svb-plunges-most-since-1998-on-stock-offering-securities-sales?cmpId=google)은 03/10 00:29:58Z, [#15 보관본](https://web.archive.org/web/20230310005643id_/https://www.bloomberg.com/news/articles/2023-03-09/svb-ceo-becker-asks-silicon-valley-bank-clients-to-stay-calm)은 00:56:43Z다. dateModified는 기사 전체 수정 시각이며 제목 변경 순간으로 쓰지 않는다. URL만으로 최초 제목을 복원해 더 이른 발행 시각에 붙이지 않는다.

### #43 - DAI 삭제 사실과 최초 제목 복원을 분리

[The Block 현재 기사](https://www.theblock.co/news/markets/2023-03-11-usdc-and-dai-remain-at-about-0-90-following-circles-disclosure-of-funds-at-svb-218993) 하단의 정정 문구가 DAI 삭제를 확인해 주며 사용자도 이를 확인했다. 그러나 최초 제목 전체 문구와 그 공개 시각까지 증명하지 않는다. URL로 추정한 제목은 후보로만 두고, 해당 초기 제목과 시각이 확인된 판본을 확보하거나 현재 제목이 확인된 판본 시각을 사용한다. 현재 제목에 최초 시각을 자동으로 붙이지 않는다.

## 4. 함께 고칠 것

- #42 Reuters: 초기 07:25:40Z와 후판 07:26:23.713Z의 시각 필드 차이를 적는다. 원표 07:26:23Z가 어느 판본을 뜻하는지와 소수초 처리도 통일한다.
- #47 NY DFS: 원 JSON은 2023-03-12라는 날짜만 저장한다. 현재 로직의 03/13 00:00Z는 확인된 발행 시각이 아니다. 뉴욕 현지 날짜라는 가정이면 종료는 03/13 04:00Z다. 가정을 명시한 정책을 정하거나 제외한다. 같은 사건을 #48·49가 보도한다.
- #33·41·46·50·54: 원시값 00:01:50.050Z, 05:51:23.756Z, 20:58:36.640Z, 22:25:41.430Z, 01:55:18.818Z를 보존한다. 정수 초 사용 시 각각 51·24·37·42·19초로 올린다. 다음 분으로 올리는 정책도 가능하다. 제목 available_at 조건은 별도로 적용한다.
- 위 5건 외에도 #1·6·7·8·10·13·15·16·17·20의 소수초와 SNS #35·36·38·45의 ID 생성 밀리초를 보완한다. 전체 19건의 원시값·정수 초 올림 예는 검증 결과 5-4절에 있다. SNS 값은 ID 생성 시각이라는 근거 성격을 표시한다.
- #45: 출처를 Circle CEO 개인 계정(@jerallaire)으로 구체화한다.
- 원 JSON archive 12건과 검토 과정에서 확보한 보관본 근거 전체를 구분한다. 전재본은 #19·20·28·51 네 건이다.

## 5. 리드타임에 대해

기존 기록의 v1 연속 신호 시작은 03/09 21:00Z, 최저점 전 35시간이며 근거는 #12 TechCrunch다. v2·v2.1은 03/08 22:00Z, 58시간이며 #4·5·6 Silvergate 청산 보도가 시작 근거다. Silvergate 제목을 제외한 v2.1은 36시간이다. [기준 커밋의 리드타임 기록](https://github.com/SEJINKIM-git/depeg-early-warning/blob/8ef6cac97e6b4f5f106c6ad80af1eca1955f2552/docs/news_leadtime_2023.md)

모두 기존 입력의 잠정 뉴스 신호 수치다. 이번에 입력 정정 후의 숫자를 다시 계산한 것은 아니다. 제목·시각 정책과 규칙 버전을 확정한 뒤 재계산해야 한다.

- #11 안 A와 최초 발행 시각의 차이는 같은 19시대 안에 있지만 다른 입력의 사용 시각 이동과 함께 계산해야 한다.
- #24·41은 확보 캡처 기준 안 A를 사용할 수 있게 됐으나 적용 결정은 남아 있다.
- #10은 3월 9일 16시부터 21시, #15는 같은 날 20시 이후 구간의 제목 시점 판단과 관련된다.
- #41은 3월 11일 07시부터 08시 구간의 입력과 관련된다. 다른 기사와 24시간 창이 있으므로 변경된 제목 한 건만으로 전체 리드타임 변화를 단정하지 않는다.
