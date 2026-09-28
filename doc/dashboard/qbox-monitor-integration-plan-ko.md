# QBox monitor와 AutoSD dashboard 연동 구현계획

작성일: 2026-09-28

상태: 구현 진행 및 검증 결과는 [구현·검증 보고서](qbox-monitor-implementation-ko.md)를 참조한다.
아래는 최초 설계 기준이며 개별 기능의 완료 판정은 보고서의 증거를 따른다.

## 1. 목표와 범위

기존 AutoSD dashboard에 QBox의 시뮬레이터 관측 정보를 결합한다. AP Linux의
SSH가 준비되기 전에도 RSE, SI CL0, SI CL1, AP의 진행 상태를 표시하고,
watchdog·mixed-criticality 시나리오의 원인과 복구 과정을 증거로 남긴다.

- QBox full-system을 먼저 구현·검증하고 AP-only를 뒤따라 지원한다.
- QEMU 기존 부팅·제어·Guest telemetry는 유지한다.
- 로그인 없는 내부망 사용과 localhost 직접 접속을 유지한다.
- 로그 탭은 Host log / Guest log 두 개를 유지한다. Guest log 안에서 도메인과
  서비스 출처를 선택하고, 이전 실행은 세션 dropdown에서 조회한다.
- 이번 범위에 물리 전력·온도·실제 하드웨어 WCET/FTTI 인증은 포함하지 않는다.
- 본 문서 작성 작업은 실행 중인 VM 변경, monitor 활성화 또는 코드 수정을 하지 않는다.

## 2. 현재 구현과 격차

| 항목 | 확인된 현재 상태 | 필요한 작업 |
|---|---|---|
| Guest telemetry | SSH의 `/proc/stat`, cgroup, systemd, podman 정보 | 기존 collector를 유지하고 별도 simulator collector 추가 |
| Full-system monitor | Lua에서 환경변수로 생성 가능 | AutoSD launcher 옵션·manifest·dashboard boot 전달 연동 |
| AP-only | full-system injection을 거부하며 별도 monitor 생성 경로 필요 | 읽기 전용 monitor 구성 추가, full-system mutation은 비활성 |
| 시간·CPU | `/sc_time`, `/sc_suspended`, `/qk_status` 제공 | 오류·신선도·동기화 차이 의미를 포함하는 정규화 |
| MCIPS | `/mcips_plugin_status` 제공 | 실제 활성화된 plugin과 필드만 노출 |
| 객체 조회 | `/object/`에서 debug socket 검사를 위해 MMIO read 수행 | MMIO 없는 metadata-only 경로 선행 구현 |
| Debug read | URL 주소 대신 `txn.set_address(0)` 사용, 직접 transport 호출 | 주소·SystemC 실행 문맥·응답 검증 후 별도 활성화 |
| Pause/Resume | SystemC suspend/unsuspend 경로 존재, dashboard에서는 QBox 비활성 | 반복 full-system qualification 후 capability 활성화 |
| Injection | typed API 및 플랫폼 allowlist 구현 | dashboard 작업·세션·판정·해제 정책 연결 |
| Capability 조회 | runtime mutation 비활성 시 injection capabilities도 403 | 기능 비활성으로 처리; monitor 전체 OFFLINE으로 취급하지 않음 |
| QMP | 재사용 컴포넌트는 존재하나 Apollo 도메인별 Lua 연결은 확인되지 않음 | 도메인별 연결 정의와 실제 biflow 발견 결과 검증 |

근거: [dashboard server](../../scripts/autosd_dashboard/server.py),
[guest collector](../../scripts/autosd_dashboard/guest_monitor.py),
[telemetry](../../scripts/autosd_dashboard/telemetry.py),
[AutoSD launcher](../../scripts/run/run_qbox_autosd.py),
[full-system runner](../../scripts/run/run_qbox_apollo_fvp_full.py),
[monitor 구현](../../hsoc-stack/tools/qbox/systemc-components/monitor/src/monitor.cc),
[monitor 문서](../../hsoc-stack/tools/qbox/docs/monitor.md),
[monitor 디버깅 제약](../../hsoc-stack/tools/qbox/docs/monitor-debugging-guide.md),
[full-system Lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua),
[AP-only Lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-linux.lua).

## 3. 연결 및 데이터 계약

브라우저는 기존 dashboard 포트 8765만 사용한다. Dashboard backend가 자신이
시작한 QBox의 loopback monitor에 접속한다. 외부 URL·임의 socket path를 사용자가
전달하는 범용 proxy는 만들지 않는다.

### 실행과 기능 발견

1. `run_qbox_autosd.py`에 monitor 활성화/포트 옵션을 추가하고 하위 runner로 전달한다.
2. 실행 manifest에 schema version, backend, run ID, monitor endpoint, PID와
   프로세스 시작 식별정보, profile, 도메인 object path 매핑을 기록한다.
3. 포트 충돌 검사 후 실제 endpoint 준비 상태와 소유 프로세스를 확인한다.
   빈 포트 사전 조회만으로 예약 성공을 간주하지 않는다. 충돌 시 실패를 보고하며
   다른 프로세스를 종료하거나 해당 포트에 임의로 연결하지 않는다.
4. Backend adapter가 실제 지원 기능을 발견한다. endpoint 존재, 모델 구성,
   런타임 검증 여부를 구분하고 `available`, `qualified`, `reason`을 반환한다.
5. QBox monitor 준비와 Guest SSH 준비는 독립 상태로 유지한다. Monitor만 ONLINE인
   것으로 Feature 1 부팅이나 Feature 2 health를 PASS 처리하지 않는다.

### 제안 dashboard API

아래 경로와 데이터 형식은 신규 설계이며 현재 구현된 API가 아니다.

| 경로 | 용도 |
|---|---|
| `GET /api/simulator/capabilities` | backend별 가용·검증된 기능 |
| `GET /api/simulator/snapshot` | 캐시된 시뮬레이터·도메인·CPU 상태 |
| `GET /api/simulator/events?after=<seq>` | 세션별 이벤트 증분, 페이지 크기 제한 |
| `GET /api/simulator/objects?parent=<id>` | 허용된 metadata-only 탐색 |
| 기존 시나리오 실행 API 확장 | 허용된 injection 시나리오 실행과 결과 조회 |
| 기존 system control API 확장 | qualification 완료 후 QBox Pause/Resume |

Snapshot은 `schema_version`, `run_id`, `sample_seq`, host 수집 시간,
`sim_time_ns`, `status`, `last_success_at`, `age_ms`, 오류 원인, 도메인/CPU 항목을
포함한다. 기존 monitor의 부동소수 seconds는 adapter에서 원본도 보존한다.
정수 nanoseconds로 변환했다고 원래 측정 정밀도가 높아졌다고 주장하지 않는다.

각 도메인은 `domain_id`, `qemu_instance_path`, `cpu_object_paths`,
`boot_epoch`, `last_event`를 갖는다. 실제 profile/객체 구성을 기준으로 목록을
만들고 전체 CPU 개수나 MPIDR을 추정하지 않는다. Epoch는 로그 추론인지 모델
이벤트인지 출처를 함께 기록한다.

### 시간과 상태 의미

- host monotonic, SystemC simulation time, Guest monotonic/boot ID를 별도 저장한다.
- 실행 속도는 `Δsimulation_time / Δhost_monotonic`으로 정의한다. 최초 표본,
  시간 역행, 새 run, 불충분한 구간에는 값을 만들지 않는다.
- QK 상태는 시뮬레이터의 실행·동기화 상태이다. RUNNING 표본 비율을 Linux CPU
  사용률이나 물리 CPU 사용률로 표시하지 않는다. WFI 원인도 상태 이름만으로 단정하지 않는다.
- local time의 단위와 absolute/offset 의미는 producer 구현으로 확인한 뒤 변환한다.
- MCIPS 수치는 활성화된 plugin이 실제 제공하는 필드에 한해 표시하고 물리 성능과 구분한다.
- simulation time 정지만으로 hang을 판정하지 않는다. PAUSED, 응답 정체,
  로그 진행 여부를 함께 보여주며 초기 판정은 `SUSPECTED_STALL`로 제한한다.

## 4. 수집·세션·보호 정책

### 수집 및 UI 전송

- QBox 수집은 Guest SSH collector와 별도 worker/lock으로 실행한다. Network I/O
  동안 dashboard 전역 lock을 보유하지 않는다.
- 초기 기본안은 simulator 2초, Guest는 기존 5초 수집이다. 실제 성능 검증으로
  조정하고 관측 주기를 결과에 남긴다. 브라우저 수와 무관하게 서버 collector는 한 개다.
- 첫 버전은 현재 HTTP polling을 확장한다. ThreadingHTTPServer에 WebSocket 지원이
  있다고 가정하지 않는다. 콘솔 스트림은 P2에서 별도 transport 설계를 검토한다.
- 요청 timeout, 최대 응답 크기, 연결 실패 backoff, queue 상한, 저장 quota 및 rotation을
  설정값으로 둔다. 초기 제안: 요청 2초, 응답 1 MiB, backoff 최대 30초,
  실행별 simulator evidence 64 MiB. 초과 시 drop/gap을 표시하고 서비스는 유지한다.
- Host timeout은 SystemC에 제출한 작업의 취소 완료를 뜻하지 않는다. 완료가 불명확한
  mutation은 UNKNOWN으로 표시하고 자동 재전송하지 않는다.
- RT 측정 구간에는 상세 polling·MMIO·객체 탐색을 중단한다. 최소 관측도 기존
  measurement barrier와 연동하며, 수집으로 인한 결과 변화를 비교한다.

### 재부팅 및 데이터 보존

- 프로세스 재시작은 새 `run_id`, AP reboot는 새 AP epoch/Guest boot ID로 구분한다.
- AP-only watchdog reset으로 SI가 유지되면 SI epoch·증거는 유지한다.
- Feature 상태 초기화는 기존 power lifecycle을 따른다. 지연 도착한 이전 세션
  snapshot이 새 Feature 상태나 그래프를 갱신하지 못하도록 요청 시점 ID를 검사한다.
- UI에는 현재 실행을 기본 표시하고 과거 실행은 dropdown에서만 선택한다.
- 기존 `telemetry.jsonl`과 별도로 `simulator.jsonl`, `simulator-events.jsonl`,
  `simulator-capabilities.json`을 실행 evidence 아래 저장한다. 이벤트는 출처,
  sequence, 관측/발생 시간, 시간 정밀도 및 누락 여부를 포함한다.

### 입력 및 실행 범위

- 로그인 요구를 추가하지 않고 기존 Host/Origin/CSRF 검사와 실행 허용 설정을 재사용한다.
- Monitor는 loopback에 바인딩한다. `runtime_mutation=false`가 `/pause`,
  `/continue`, biflow 입력까지 차단하지 않는다는 점을 adapter 정책에 반영한다.
- 클라이언트가 임의 monitor URL, HMP 명령, CCI 쓰기, 메모리 쓰기를 실행할 수 없게 한다.
- injection은 부팅 시 별도 opt-in한다. 기본 관측을 위해 mutation을 켜지 않는다.
- 요청 generation, reset domain, `clear_on_reset` 규약은 서버 capability와 현재
  snapshot에 맞춰 검증한다. Dashboard epoch와 injection generation을 동일시하지 않는다.
- cancel과 fault 해제는 별도 동작이다. 요청이 실행된 뒤 cancel했다고 GPIO/IRQ 상태가
  복구된 것으로 처리하지 않는다. 시나리오별 release 및 후조건 검사를 구현한다.

## 5. 단계별 작업과 종료 조건

### P0 — 부팅 전후 관측 통합

구현 순서:

1. Launcher 옵션·manifest·포트 준비 확인 및 simulator capability 계약.
2. 신규 `scripts/autosd_dashboard/qbox_monitor.py` adapter와 bounded collector.
3. 기존 `server.py`/`web/app.js`/`web/index.html`/`web/style.css`에 simulation 요약,
   도메인·CPU 카드, 진행 속도 그래프, stale/offline 표시 추가.
4. 실패 시 monitor snapshot·도메인 로그·Guest health를 함께 수집.
5. Full-system 검증 후 AP-only 읽기 전용 monitor 경로 추가. QEMU에는 해당 기능을
   UNSUPPORTED로 명시하고 기존 Guest 기능을 유지한다.

P0에서는 object tree 자동 탐색, MMIO, QMP, injection, QBox pause를 활성화하지 않는다.
Profile의 명시적 객체 매핑과 부작용 없는 status endpoint를 사용한다. QK/MCIPS
producer의 동시 접근 안전성 및 `run_on_sysc` 종료/timeout 동작도 검토한다.

종료 조건: SSH 준비 전 simulator 상태가 표시되고, Guest 연결 실패와 monitor 연결
실패가 서로 전파되지 않는다. 브라우저 3개에서도 sampler가 늘어나지 않고, Power
off/on 및 AP reboot 후 이전 표본이 새 run/epoch에 섞이지 않는다.

### P1 — 시나리오 증거와 하드웨어 장애 주입

1. Watchdog 시나리오에 WS0/WS1, SI 복구, RSE reload, AP boot, 서비스 health의
   타임라인을 연결한다. 초기 로그 기반 이벤트는 `source=log`로 표시한다.
2. 정확한 simulation timestamp가 필요한 모델 이벤트는 QBox platform에 bounded
   structured event stream을 추가한다. 기존 REST만으로 모든 전이를 복원한다고 가정하지 않는다.
3. QM 부하와 ADAS deadline miss, safety 상태, Guest cgroup, simulator 진행 속도를
   동일 실행 결과에서 비교한다. Clock 간 인과관계는 상관 정보 없이 단정하지 않는다.
4. 먼저 HIPC MHU drop-next-doorbell처럼 범위가 정해진 시나리오를 연결한다.
   GIC·GPIO·I2C fault는 capability와 실제 배선을 확인한 profile만 허용한다.
5. SSU critical fault와 counter 제어는 별도 파괴적 실험 profile로 분리한다.
   정상 복구 가능한 데모라고 사전 가정하지 않는다.

종료 조건: action 접수·실행·Guest 관측·복구 결과가 각각 구분되고, 요청 취소,
deadline 초과, reset 중 요청, stale generation, 재실행의 후조건이 검증된다.
Watchdog 성공은 새 AP boot ID와 Automotive health 회복으로 판정한다.

### P2 — Inspector, QMP 및 시스템 제어

1. Monitor에 MMIO 없는 metadata-only 객체 조회를 추가한 후 Inspector를 연동한다.
2. Debug read 주소 전달과 SystemC 실행 문맥을 수정하고, allowlisted RAM 및
   read-safe register만 제공한다. 읽기 길이·정렬·TLM response를 검증한다.
3. 도메인별 QMP 컴포넌트/Unix socket과 QemuInstance 소유 관계를 구성한다.
   실제 biflow 존재를 확인하고 도메인별 서버 연결을 단일화한다.
4. QMP 요청은 고유 ID로 대응시키고 과거 replay와 비동기 이벤트를 구분한다.
   처음에는 read-only 명령만 허용한다. 동작 중 CPU register snapshot은
   coherent snapshot이라고 표시하지 않는다.
5. SystemC suspend/unsuspend 중 monitor 접근과 재개 경로를 검증한 뒤 기존
   Pause/Resume 버튼의 QBox capability를 활성화한다. QMP로 AP만 stop하는 동작은
   full-system Pause 구현으로 사용하지 않는다.

종료 조건: 주소가 다른 두 RAM 값을 올바르게 읽고, 허용되지 않은 MMIO는 거부된다.
QMP 재접속 시 과거 응답이 현재 요청 결과가 되지 않는다. Pause/Resume 반복 후
4개 도메인·Guest SSH·HIPC·watchdog이 정상 동작하고 reset/timeout이 오발생하지 않는다.
이 gate 통과 전에는 기존 QBox Pause/Resume 비활성 상태를 유지한다.

## 6. 변경 소유권과 커밋 단위

| 소유 저장소 | 예상 변경 | 분리할 커밋 주제 |
|---|---|---|
| root | `scripts/run/run_qbox_autosd.py`, dashboard, tests, 본 문서 | launcher 계약 / collector / UI / 시나리오 / 검증 문서 |
| qbox | `systemc-components/monitor/`, monitor tests, docs | metadata-only 조회 / debug-read 수정 / control 검증 |
| qbox-platform | Apollo Lua, runtime injection, 모델 event 관측 | AP-only monitor / 도메인 QMP / typed events / 시나리오 배선 |

기존 QBox C++14, CCI, `gs::runonsysc` 경계를 재사용한다. 새 host→SystemC 실행
queue를 별도로 만들지 않는다. `patch-qbox/`의 보관 패치는 자동 적용하지 않는다.
공유 BitBake 빌드는 직렬 실행하며 source 변경 중 입력을 사용하는 build를 시작하지 않는다.

## 7. 검증 계획

| 계층 | 필수 검사 | PASS 기준 |
|---|---|---|
| Adapter 단위 | timeout, 잘못된 JSON, 403/404/503, oversized 응답, 단위 변환 | bounded 종료, 원인 유지, Guest 데이터 보존 |
| Lifecycle 단위 | 이전 run/epoch 응답, port 재사용, 작업 경합 | 잘못된 인스턴스 제어·상태 덮어쓰기 없음 |
| UI | full/AP-only/QEMU, offline/stale, history 선택 | 실제 capability와 일치, 미지원 숫자 생성 없음 |
| Monitor component | metadata 부작용, debug 주소, SystemC 경계, 정지 중 접근 | 자동 MMIO 없음, 올바른 주소·응답·종료 |
| Full-system | cold boot, 정상 reboot, watchdog AP reset, power cycle | epoch·로그·Feature 상태 정합성 및 Guest health |
| 부하/관측 영향 | collector off/on, 브라우저 1/3개, RT measurement barrier | 요청 수 증가 없음, 차이 보고, 허용 기준 합의 후 적용 |
| 장애 주입 | 실행/해제/취소/timeout/재부팅 중 주입 | accepted와 observed PASS 구분, 복구 후 상태 증거 |
| P2 control | 최소 10회 Pause/Resume 및 후속 HIPC/watchdog | 지속 동작, 예상치 않은 reset·멈춤 없음 |

UI 테스트는 기존 `tests/test_autosd_dashboard_ui.cjs`, backend는
`tests/test_autosd_dashboard.py` 및 신규 adapter 테스트로 확장한다. QBox 모델 변경은
해당 `do_check`와 실제 full-system traffic으로 검증한다. 빌드만 성공한 결과는
런타임 PASS로 보고하지 않는다.

증거는 실행별 JSON/JSONL, 로그, 입력 binary/image/config 식별정보와 함께 보존한다.
QVP 전용 qualification은 `build/qbox-apollo-qvp/`에 두고 dashboard 실행 evidence의
경로와 run ID로 연결한다. 미실행 항목은 NOT_RUN, 미지원 기능은 UNSUPPORTED로 보고한다.

## 8. 참고 및 미결정 사항

- QMP ID·event 계약: [QEMU 공식 QMP 사양](https://www.qemu.org/docs/master/interop/qmp-spec.html).
- 초기 수집 주기·quota는 설계 기본값이며 실제 부하 측정 후 조정한다.
- P0 검증 중 QK 상태 접근의 thread safety 문제가 발견되면 native snapshot API를
  선행 수정한다. 타이밍 측정에 임의 sleep이나 무제한 polling을 추가하지 않는다.
- QMP socket 노출/bridge 설계와 전역 pause의 안전한 정지 지점은 P2 착수 전
  실제 다중 QemuInstance 구성에서 확정한다.
- 동반 검토 문서: [검토 결과](qbox-monitor-integration-review-ko.md).
