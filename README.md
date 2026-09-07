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
