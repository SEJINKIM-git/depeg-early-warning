# 대응 매트릭스 (초안 자리)

> 담당: 대응 설계 (3인 체제: 전원 공동 / 4인 체제: 학생 B)
> ScoreEvent(schemas/score_event.schema.json)의 threshold_breached 가 true일 때의 대응을 정의하는 문서임

| risk_score 구간 | 운영자 | 일반 사용자 |
|---|---|---|
| 70~85 | TODO: 모니터링 강화 지침 | TODO: 안내 없음 or 주의 안내 |
| 85~100 | TODO: 승인 요청 발송 (승인/반려/만료) | TODO: 환매 관련 안내 |

- 원칙: 무응답(만료)도 하나의 결과 — 재알림 규칙을 반드시 정의할 것
