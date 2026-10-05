# depeg-early-warning

스테이블코인 디페그(1달러 페그 붕괴) 리스크를 온체인·오프체인 데이터로 조기 탐지하고,
이해관계자 역할별 대응을 자동화하는 시스템 — 랩 학기 프로젝트임

## 시작하기

- 개발 환경 준비: `docs/개발환경_세팅_가이드.md` 를 따라 세팅할 것
- 프로젝트 배경: `docs/랩_OT_자료.md`, `docs/스테이블코인_배경지식_온보딩.md` 필독
- 시스템 연결 구조: `docs/코드_통합_설계.md` — 이 저장소가 ThreatWatch와 어떻게 결합되는지

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py            # mock 데이터로 파이프라인 관통
python -m pytest -q       # 계약 테스트
```

## Bitstamp hourly 수집

USDC/USD의 완료된 hourly candle만 Signal v1 JSON으로 표준 출력한다. 모든 시각은
UTC이며 `--start`와 `--end`는 **Bitstamp 캔들 시작 시각**의 반열린 구간
`[start, end)`를 뜻한다. Signal의 `observed_at`은 종가가 확정된 캔들 종료 시각이므로
반환 범위는 `(start, end]`다. 예를 들어 아래 요청의 첫 Signal은
`2023-03-09T01:00:00Z`, 마지막 Signal은 `2023-03-14T00:00:00Z`다.

긴 기간은 Bitstamp 요청 제한에 맞춰 자동으로 나눈다. 성공한 각 chunk의 원본 HTTP
body는 변형 없이 `data/raw/bitstamp/usdcusd/`에 저장하며, `--end`는 실행 시점의 현재
UTC hour boundary보다 늦을 수 없다.

```bash
python -m scripts.collect_bitstamp_usdc --start 2023-03-09T00:00:00Z --end 2023-03-14T00:00:00Z
```

`--request-delay`는 정상 chunk 요청 사이의 대기 시간이다. 재시도 가능한 연결 오류,
timeout, HTTP 408·429·5xx 뒤에는 이 값과 무관하게 `--retry-delay`부터 시작하는 지수
백오프를 적용하고 자체 계산한 대기만 `--max-retry-delay`로 제한한다. 유효한
`Retry-After`(초 또는 HTTP 날짜)나 `X-RateLimit-Reset`이 있으면 서버 값을 우선하며
최소 대기는 보장하되 자체 백오프의 최대치로 줄이지 않는다. 그 밖의 HTTP 4xx는 즉시
실패한다.

Raw 파일명은
`bitstamp_usdcusd_<chunk-start>_<chunk-end>.json`이고 Windows 호환을 위해 시각의
`:`를 `-`로 바꾼다. `data/raw/`는 API 원본 증거이고 `data/historical/`은 Signal v1
변환 결과다. 같은 요청을 다시 실행했을 때 raw bytes가 같으면 기존 파일을 재사용하고,
다르면 덮어쓰지 않고 오류로 중단한다. 저장 위치는 `--raw-directory`로 바꿀 수 있다.

## 구조

```text
schemas/     데이터 계약 (팀 간 인터페이스 — 변경은 반드시 리뷰 미팅에서)
data/mock/   mock 시그널 (2023 USDC 사태 기반 샘플)
src/
  collectors/     역할 1: 온체인 수집기
  intelligence/   역할 2: 오프체인 attestation 파서
  engine/         역할 3: 리스크 스코어 엔진 + 백테스트
  adapters/       score_event → ThreatWatch 경보(AlertRequest) 변환 (docs/코드_통합_설계.md 참고)
  response/       대응 설계: 대응 매트릭스 문서
tests/       계약 테스트 — 모든 모듈 출력이 스키마를 지키는지 검증
main.py      로컬 러너 (I/O는 전부 여기서, src/ 는 순수 함수만)
docs/        온보딩·OT·세팅 가이드
```

## 규칙 (전문은 CONTRIBUTING.md)

- 모든 모듈은 **순수 함수** — 파일/네트워크 I/O는 `main.py`(로컬) 또는 Lambda 핸들러(운영)가 담당함
- 팀 간 연결은 **schemas/ 의 계약으로만** — 스키마 변경은 리뷰 미팅 안건임
- main 직접 push 금지 — 브랜치 → PR → CI → 랩장 리뷰 → 머지
- `requirements.txt` 는 정확한 버전 고정(`==`) 유지
- AWS 배포·인프라는 랩장 전담 — 학생 코드는 이 저장소의 로컬 실행 가능 상태만 유지하면 됨
