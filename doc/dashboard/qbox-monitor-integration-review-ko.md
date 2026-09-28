# QBox monitor 연동 계획 검토

검토일: 2026-09-28

방식: 현재 소스와 구현계획을 대조한 자체 검토. 독립 외부 검토나 신규 런타임
qualification은 수행하지 않았다.

판정: **P0 구현 착수 가능한 계획**. P1/P2는 아래 선행 조건을 만족한 뒤 진행한다.
이는 구현 완료나 전체 기능 PASS 판정이 아니다.

## 검토 결과와 반영 사항

| ID | 중요도 | 발견 사항 | 계획 반영 |
|---|---|---|---|
| R01 | 높음 | debug read가 URL 주소를 무시하고 주소 0에 접근 | P2 전용으로 분리, 주소·TLM 상태·실행 문맥 검사 추가 |
| R02 | 높음 | object 조회도 debug socket 발견 과정에서 MMIO를 읽음 | P0 자동 탐색 제외, metadata-only API를 Inspector 선행 조건으로 지정 |
| R03 | 높음 | mutation 비활성은 pause/biflow까지 보호하지 않음 | dashboard proxy allowlist, loopback, 기존 CSRF/Origin 검사 유지 |
| R04 | 높음 | QBox Pause API 존재만으로 full-system 재개를 보증할 수 없음 | 최소 10회 반복 및 HIPC/watchdog 후검증 gate 추가 |
| R05 | 높음 | AP reset과 SI 유지, process restart가 서로 다른 수명주기 | run ID·도메인 epoch·Guest boot ID·injection generation 분리 |
| R06 | 높음 | AutoSD launcher가 monitor 옵션을 명시적으로 전달하지 않음 | CLI→하위 runner→manifest→dashboard 연결을 P0 첫 작업으로 배치 |
| R07 | 중간 | mutation off에서 capability GET도 403 | injection 비활성으로만 처리, simulator offline과 구분 |
| R08 | 중간 | QMP 컴포넌트 존재와 Apollo 도메인 연결은 별개 | P2에서 실제 구성·biflow 확인, 미지원 상태 명시 |
| R09 | 높음 | RT tracing 중 관측이 측정 결과를 바꿀 수 있음 | 기존 measurement barrier 공유, collector off/on 비교 및 주기 기록 |
| R10 | 중간 | 기본 HTTP 서버에는 일반 WebSocket proxy 기능이 없음 | P0는 cached polling, 스트림 transport는 P2 별도 설계 |
| R11 | 높음 | HTTP timeout/요청 cancel이 모델 동작 취소·fault 해제를 의미하지 않음 | UNKNOWN 상태, 재전송 금지, 시나리오별 release·후조건 검증 |
| R12 | 중간 | 세 가지 clock 및 QK 시간 의미가 섞일 위험 | 출처·단위·epoch 보존, 변환 정밀도 제한, CPU 사용률 분리 |
| R13 | 중간 | 기존 API만으로 모든 hardware transition 관측은 불가능 | 로그 기반 관측과 모델 structured event 추가를 구분 |
| R14 | 높음 | 저수준 collector가 멈추면 dashboard도 묶일 위험 | 별도 worker, I/O 중 전역 lock 금지, timeout/backoff/queue 상한 |

소스 근거:

- [monitor.cc](../../hsoc-stack/tools/qbox/systemc-components/monitor/src/monitor.cc):
  `json_object`, `/transport_dbg`, `/pause`, `/continue`, injection guard.
- [monitor.h](../../hsoc-stack/tools/qbox/systemc-components/monitor/include/monitor.h):
  biflow 연결 시 최근 출력 replay.
- [server.py](../../scripts/autosd_dashboard/server.py): `safe_request`, `monitor`,
  `boot_command`, 기존 measurement/control barrier.
- [Apollo runtime injection](../../hsoc-stack/tools/qbox-platform/systemc-components/apollo_runtime_injection/src/apollo_runtime_injection.cc):
  capability 대상, generation 검사, reset 정리 정책.

## 구현 전·중·후 검토 gate

1. P0 PR: 기존 Guest schema 호환, marker 기반 domain 상태와 simulator 관측의 출처,
   manifest 소유권, port 충돌, stale 응답 거부, sampler 수를 확인한다.
2. P1 PR: allowlist, 시나리오 사전조건·후조건, 실패 후 fault 잔류, event 손실 및
   clock 상관관계의 한계를 확인한다. 임의 MMIO/GIC 주입을 일반 UI로 노출하지 않는다.
3. P2 PR: metadata-only 계약, debug register read의 side effect, QMP 응답 ID/replay,
   전체 SystemC 정지와 개별 QEMU 정지의 차이를 검증한다.
4. 각 단계의 런타임 결과를 단계별로 기록한다. 선행 단계 PASS를 다른 backend나
   물리 타이밍 정확성의 PASS로 확대하지 않는다.

## 남은 검증 항목

- QK/MCIPS producer 동시 접근 안전성과 단위 의미: P0 구현 시 확인.
- 종료·pause 중 `run_on_sysc`의 완료 및 대기 해제: P0/P2에서 각각 확인.
- AP-only monitor의 객체 구성·port 수명주기: full-system P0 완료 후 확인.
- 도메인별 QMP와 full-system pause 재개 안정성: P2에서 확인.
- sampling overhead 수용 기준: collector off/on 실측을 보고 설정.

따라서 우선 범위는 **launcher/manifest → bounded read-only collector → 도메인/CPU
표시 → 세션별 증거**로 확정한다. 기능 활성화는 각 gate의 실제 검증 결과에 따른다.
