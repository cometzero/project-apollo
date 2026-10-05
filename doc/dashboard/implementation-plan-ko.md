# 구현 및 검증 계획

상태: **P0–P4 구현, P5 기능·회귀 검증 수행**. 실제 결과와 장시간 부하 시험 등 잔여 범위는 [구현 보고서](implementation-report-ko.md)를 참조한다.
아래 표와 행렬은 최초 설계의 목표를 보존한다. 실제 수행한 시험과 미수행 항목은 보고서에서 구분한다.
시나리오 adapter는 별도 `board_scenarios.py` 대신 `yocto_board.py`의 typed job dispatch에 통합했다.

## 1. 단계별 작업

| 단계 | 산출물·주요 파일 | 완료 조건 |
|---|---|---|
| P0: 실행 계약 | `run_qbox_yocto.sh`, 신규 launch spec/`qbox_board_session.py`; tmux runner 공통화 | artifact 선택 보존, headless+BSP+TC397+SIL Kit 가능, process 소유권 격리 |
| P1: 웹 관측 | `server.py`, 신규 `yocto_board.py`, log adapter, 기존 simulator/diagnostics와 stats collector | LAN 접속·자동 boot·기본 5개 UART, BSP/vMCU 활성 시 6개; `--stats` 현재 부하·추이; browser 재접속 가능 |
| P2: 실제 구성의 보드도 | `topology.py`, descriptor evaluator, `web/board.js/css`, launch snapshot | provider/env/override 기반 Board/Block 보기, source 추적, 외부 MCU/SIL Kit |
| P3: 기본 제어 | 신규 `vmcu.py`, typed jobs/capabilities, 기존 CLI/CAN adapter | 조회·PMIC·AP off/wake/recover·MCU reset의 후조건까지 증거 |
| P4: 시나리오 | 신규 `board_scenarios.py`, 기존 validation engine·vMCU evaluator 재사용 | vMCU fault·CAN·11개 QVP profile을 지원 조건에 따라 실행·판정 |
| P5: 회귀·운영성 | UI/launcher/backend 회귀, quota·reconnect·auth·shutdown | 기존 tmux/headless/AutoSD 동작 보존, 2개 격리 session 및 장시간 로그 검증 |
| P6: 선택 확장 | 아래 기능 우선순위에 따라 추가 | 각 기능의 telemetry 근거와 active runtime 시험이 있을 때만 enable |

P0에서 먼저 CLI만으로 companion의 headless 동작을 검증하고 웹을 붙인다.
P1 완료 시 외부 사용자가 실제 UART를 볼 수 있고, P2 완료 시 구성도와 실제 실행의
출처가 일치한다. P3/P4는 이 read-only 관측 기반을 이용해 요청과 효과를 검증한다.
기존 UI 전체 교체, microservice 분할, WebSocket/DB 도입을 선행 조건으로 만들지 않는다.

## 2. 파일과 repository 소유권

| 소유 repository | 변경 예상 | 규칙 |
|---|---|---|
| root | `run_qbox_yocto.sh`, `scripts/run/`, `scripts/autosd_dashboard/`, `tests/`, `doc/dashboard/` | 초기 구현의 주 소유자. 기존 public CLI/API 회귀 보장 |
| `zephyr_vmcu_src` submodule | `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src/` | 초기는 existing CLI 재사용. 새 structured telemetry가 필요할 때만 변경 |
| qbox-platform nested repo | selected manifest에 필요한 최소 metadata 또는 실제 모델 확장 | topology 외형을 위해 live CCI path/배선을 바꾸지 않음 |
| qbox nested repo | monitor producer 개선이 필요한 경우만 | 기존 metadata-only/QMP query 계약 우선 재사용 |
| qemu/SCP/owned Yocto repo | 추가 runtime feature 또는 product vMCU packaging이 필요한 후속 단계 | 해당 저장소에서 수정·검증. web 기능만을 위해 불필요한 rebuild 금지 |

Source tree와 installed provider가 다르면 웹은 실제 실행 provider를 표시한다.
자동으로 provider를 rebuild/설치하거나 실행 중 파일을 교체하지 않는다. Artifact가
없으면 웹의 PRECHECK 실패와 재현 가능한 기존 build 안내를 제공한다.
공유 BitBake build는 직렬 실행하며 진행 중 configuration을 변경하지 않는다.

## 3. 필수 검증 행렬

다음 항목은 구현 후 수행할 시험이다. `build/qbox-apollo-qvp/dashboard-validation/`
아래 run별 명령·source/artifact SHA·원본 결과를 보관한다.

| 영역 | 입력/자극 | 필수 관측 |
|---|---|---|
| 옵션 | 일반 `--dashboard`, BSP, `--no-vmcu`, SIL Kit, dry-run, 충돌 옵션 | 예상 argv/spec, 기존 이미지 유지, tmux 실행 없음, 오류 전에 child 없음 |
| 이미지 | BSP 및 `nexios-image` 각각 | BSP serial marker와 product readiness 구분; 미지원 service는 명시적 상태 |
| 소유권 | 2개 `--multi-session`, HTTP/monitor 충돌, 외부 registry | 다른 session/PID/registry 종료 없음; 고유 artifact·FIFO |
| 부팅 수명 | login PASS 뒤 기존 boot timeout 이상 유지 | 서버·QBox·MCU 생존, hidden detached child 없음 |
| 종료/장애 | browser 종료, SIGTERM, boot 실패, MCU/participant crash | browser는 run 유지; owned server stop은 정리; fault는 FAILED/DEGRADED로 명시 |
| 인증·접속 | 다른 host에서 LAN URL, 잘못된 password/Host/Origin/CSRF | 정상 UI·로그·job; 비인가 mutation 거부; monitor/QMP 외부 미노출 |
| UART | 6개 domain, 부분 UTF-8/ANSI, rotation/truncate, slow client | 누락/중복·generation·gap 처리; 실제 TC397 수신 byte; XSS 미실행 |
| 입력 | BSP headless FIFO, 동시 status poll/job | 단일 writer, 명령 응답 상관관계; AP/SI console 입력 충돌 없음 |
| topology | Lua 장치 추가/삭제, CPU 옵션 변경, provider/source 불일치 | 두 view가 같은 변경 반영; 존재/edge 하드코딩 없음 |
| topology edge case | address 0/64bit/missing size, override, parse 실패 | 정밀도 보존, unresolved·error 표시, old graph 오표시 없음 |
| attachment | MCU on/off, UART loopback, SIL Kit on/off | active endpoint에 맞는 edge, phantom MCU/CAN 없음 |
| health | AP 관리 peer 중단, quiet console, SI 보고 관측 | 기존 PFDI 판정 유지, UI silence와 offline 구분, 5초 policy 유지 |
| MCU/CAN | PMIC snapshot, AP off/wake, MCU reset, CAN loopback | 아래 기능별 후조건 + board component 생존 |
| 오류/경합 | stale run/epoch/cookie, 중복 요청, job 중 reset, response timeout | 409/차단/idempotency, UNKNOWN 보존, mutation 자동 retry 없음 |
| 검증 job | success, 실제 fault, prerequisite 누락, cleanup 실패 | PASS/FAIL/BLOCKED/UNSUPPORTED와 cleanup 상태가 정확 |
| UI | 1440px/1024px/390px, keyboard, 필터, 다운로드, reconnect | 겹침·scroll trap 없음, 현재 run 복구, 오류 console 없음 |
| 비용 | UI 1개/3개, UART burst, 30분 관측 | collector 수 동일, memory/log 상한 준수, byte drop 명시 |
| 부하 옵션 | `--dashboard --stats`, `--stats-interval 2`, 미사용/잘못된 주기 | 5초/2초 전달, monitor/QMP 자동 활성화, DISABLED/입력 오류 |
| 부하 수치 | 같은 run의 text/structured sample, host CPU 활동 변화 | 동일 CPU/RSS/thread 값, 실제 QBox PID, domain vCPU 중복 합산 없음 |
| 부하 경계 | QMP 지연/실패, TID 종료·재사용, 새 run, RT barrier | 가능한 process 통계 유지, domain N/A, baseline reset, gap 표시 |

vMCU 기능의 완료 조건:

1. PMIC: rail 9개와 live STAT 11개 조회. SI ownership과 preserve 정책 유지. rail 변경 없음.
2. AP off/wake: SI가 실제 AP core OFF를 확인한 뒤 완료; 같은 QBox/MCU process에서
   SI ping/CAN 유지, wake 뒤 새 Linux boot/PFDI RUN/AP ping 확인. 최소 2회 반복.
3. MCU reset: QMP receipt와 새 MCU boot marker, SI epoch/AP 생존, UART cursor 재협상.
   CAN 활성 profile에서는 추가로 MCU cookie 변경과 이전 CAN command 거부를 확인한다.
4. CAN: classic/FD64 왕복의 실제 driver completion/RX 확인. 단절 시 bus-off, controller
   restart 뒤 복구. Transport bus-off를 물리 TEC/error confinement 검증으로 보고하지 않음.
5. PFDI fault: 실제 AP agent 정지 → SI mask → vMCU/CAN fault → 명시적 복구. 일반 runner의
   예상 fault FAIL과 scenario verdict를 각각 보존.
6. PAUSE: 초기 MCU 연결 상태에서 요청 차단을 검증. 후속 coherent pause는 별도 common
   clock/lease 정책과 시험이 있을 때만 제공한다.

RT/timerlat/osnoise job 동안 현재 수집 barrier를 유지하고 상세 polling/Inspector를
정지한다. 측정 결과는 QVP/TCG 조건으로 보고한다. 물리 power/timing/FVP 동일성을
dashboard 통과 기준으로 대체하지 않는다.

## 4. 검증 명령과 자동화 재사용

기존 테스트 중 변경 영역부터 실행한다. 아래는 **향후 구현 시 사용할 명령**이며
이번 문서 작업에서 실행한 결과가 아니다.

```bash
pytest -q tests/test_run_qbox_yocto_sh.py tests/test_run_qbox_yocto_tc397.py \
  tests/test_qbox_tc397.py tests/test_qbox_vmcu_boot.py
pytest -q tests/test_autosd_dashboard.py tests/test_autosd_topology.py \
  tests/test_autosd_dashboard_telemetry.py tests/test_autosd_monitor_scenarios.py \
  tests/test_autosd_watchdog_scenarios.py
node --test tests/test_autosd_topology_ui.cjs tests/test_autosd_dashboard_ui.cjs
pytest -q tests/test_qbox_load_stats.py tests/test_qbox_stats_monitor.py \
  tests/test_qbox_stats_options.py
```

추가 테스트는 launcher dispatch/lifecycle, run-scoped API, log cursor/rotation,
effective topology/attachments, typed vMCU transaction을 대상으로 한다. Firmware를
변경하지 않으면 기존 artifact로 boot·traffic 검증하고 전체 image 재빌드를 요구하지 않는다.
실제 firmware/model 변경이 생기면 해당 narrow build와 IRQ/guest traffic 시험을 추가한다.

새 통합 검증기 `scripts/test/validate_qbox_board_dashboard.py`를 제안한다. Port/output을
매번 격리하고 HTTP bootstrap→boot→UART→topology→control→cleanup을 검사한다.
외부 host 접속과 browser 화면 검사는 별도 수행한다. 초기 실패 실행도 지우지 않는다.
headless companion qualification 완료 후 기존 vMCU tmux 검증도 회귀 실행한다.

## 5. 추가 발굴 기능

| 우선순위 | 기능 | 현재 근거 / 필요한 확장 |
|---|---|---|
| P1 | 부팅 단계 timeline | RSE/SI/AP UART marker, existing simulator event. Source clock과 추론 표시 |
| P1 | Run 비교/재현 bundle | `.qboxconf`, image/provider SHA, launch manifest; 비밀 제외 export |
| P2 | GPIO·PFDI 상태 map | vMCU snapshot, masks, SI 보고. age·intentional off를 분리 |
| P1 필수 | `--stats` 현재 부하·추이 | [qbox_load_stats.py](../../scripts/run/qbox_load_stats.py), QMP domain TID mapping, RSS, `threads=N`; text/structured 표본 공유 |
| P2 | Simulation 진행률 비교 | QK/sc_time과 host 경과 시간. Host CPU/guest CPU/virtual progress를 구분 |
| 후속 | TC397/SIL Kit process별 부하 | supervisor 소유 PID의 CPU/RSS, QBox와 별도 표시; 외부 registry 미관측 |
| P2 | PMIC inventory panel | SI proxy 설정값/STAT, `policy=preserve`. 실제 voltage/current/온도 게이지는 만들지 않음 |
| P3 | CAN message inspector | `vehicle-can.jsonl`/`tc397-can.jsonl`, 0x510/600/601 decode, transaction correlation, dropped frame 표시 |
| P3 | EEPROM/PCA9539 inventory | Lua I2C routes와 guest at24/GPIO evidence. 변경 검사는 백업/restore receipt 필요 |
| P3 | Watchdog/reset 원인 timeline | WS0/WS1, SI recovery, RSE reload, AP boot ID; reset scope 구분 |
| P3 | 사전 조건 설명·검증 결과 지도 | registry assertions와 node capability 연결; 미지원 image/tool을 설명 |
| P4 | IRQ/통신 fault 실험 | 실제 runtime injection allowlist. Named scenario/evaluator/cleanup을 추가한 항목만 |
| P4 | Audio/DMA 시험 패널 | [full audio 검증기](../../scripts/test/verify_qbox_full_audio.py), DMA/I2S evidence. AP-only/full-system, DMA/PIO별 결과를 분리; 성공을 가정하지 않음 |
| P4 | PCIe/ITS·SMMU 실험 | 기존 [PCIe runtime 검증기](../../scripts/test/validate_qbox_apollo_pcie_irq_runtime.py) 등 private profile. 별도 boot artifact와 IRQ 관측 |
| 후속 | DBC/ARXML decode, 외부 차량 simulator 연결 | 현재 시험 CAN protocol을 넘어서는 입력 사양 필요 |
| 후속 | 공통 virtual-time·coherent pause/replay | 현재 QBox/TC397/SIL Kit 독립 clock. 단순 웹 adapter로 해결 불가 |
| 후속 | PMIC rail sequencer·cold power cycle | 실제 domain/PGOOD/retention 모델과 always-on 경계가 먼저 필요 |

## 6. 단계별 납품물

각 단계는 변경 파일, 실행 명령, source/artifact fingerprint, testcase별 결과와 한계를
남긴다. 구현 후 [README](README.md)에 지원 옵션과 실제 quick start를 추가하고 이 계획의
미구현 표기를 해당 증거로 갱신한다. 기존 AutoSD 보고서와 vMCU 검증 기록은 보존한다.
모델 동작이 바뀌면 해당 platform README와 `doc/qbox-fvp-emulation-project.md`도 갱신한다.

문서 자체 검토는 상대 링크·소스 경로·XML 구조·draw.io 렌더링과 요구사항 대응을
확인한다. 이것은 dashboard 구현/부팅 통과를 뜻하지 않는다.
