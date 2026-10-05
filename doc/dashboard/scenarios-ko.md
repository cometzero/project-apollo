# 시나리오와 보드 제어 설계

상태: **dashboard 연결은 계획 단계**. 아래의 '기반 있음'은 현재 모델/CLI/검증 코드의
존재를 뜻한다. 이미지와 실행 조건 없이 모든 버튼을 활성화하지 않는다.

## 1. 공통 실행 계약

Scenario descriptor는 `id`, title, adapter, required capabilities/image/artifacts,
`mode`(live 또는 fresh-run), reset scope, destructive 여부, timeout, locks,
expected evidence, cleanup, qualification reference를 포함한다.

모델 API 존재(`implemented`), 이미지 지원(`image-capable`), 현재 준비(`ready`),
해당 조합 검증(`qualified`)을 별도로 표시한다. 전체 상태는 AVAILABLE/BLOCKED/
UNSUPPORTED로 제공하며 이유를 tooltip과 상세에 남긴다. Source registry와 descriptor의
교집합만 실행할 수 있고 browser가 script path나 argv를 지정하지 못한다.

Live job은 해당 run에서 precheck → request receipt → firmware/guest 관측 → 후조건 →
cleanup 순서로 진행한다. Fresh-run job은 변경되는 image/profile을 제시한 뒤 현재
소유 run을 종료하고 private artifact로 별도 run을 만든다. 포트 충돌이 가능한 검증기를
현재 보드와 무작정 병렬 실행하지 않는다. 초기 board mutation은 run당 한 개다.

## 2. vMCU 및 SIL Kit

기반: [main.c](../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src/src/main.c),
[서비스 검증기](../../scripts/test/verify_qbox_vmcu_services.py),
[Safety 검증기](../../scripts/test/verify_qbox_zephyr_vmcu.py),
[SIL Kit 검증기](../../scripts/test/verify_tc397_silkit.py),
[서비스 계약](../vmcu/can-and-services.md).

다음 ID는 신규 dashboard의 stable action ID 제안이다.

| ID/화면 | 기반 / transport | 조건·동작 | 완료 근거와 영향 |
|---|---|---|---|
| `vmcu.status` | `vmcu-cli status` | MCU shell 준비; 읽기 | SI PFDI mask/epoch/sequence/age. AP 관리 ping과 health 구분 |
| `vmcu.ap.ping`, `vmcu.safety.ping` | CLI AP/SI RPC | 해당 UART session 준비 | peer·operation·sequence가 일치하는 응답 |
| `vmcu.pmic.snapshot` | `pmic rail 0..8`, `pmic fault 0..10` | SI READY/freshness; 직렬 조회 | 설정 uV/enable와 live STAT. SI 소유 유지 |
| `vmcu.recover` | `recover start/status` | SI 복구 가능한 상태 | firmware COMPLETE 뒤 새 Linux boot/PFDI online/AP ping까지 확인; AP만 복구 |
| `vmcu.power.off` | `power off/status` | AP RUN, SI arm 성공 | AP core OFF 확인, IST_DONE_N low, SI/MCU/CAN 생존 |
| `vmcu.power.on` | `power on/status` | AP_OFF | GPIO wake→RSE reload→AP release→새 Linux/PFDI 확인 |
| `vmcu.reset` | 소유 TC397 QMP `system_reset` | MCU endpoint 소유 확인 | 새 MCU boot marker, SI epoch 유지, UART 재협상, AP 생존. CAN 활성 시 새 cookie 추가 확인 |
| `vmcu.can.status` | `can status` + event JSONL | M_CAN/bridge 활성 | RX/TX/error/drop과 연결 상태; tx enqueue를 성공으로 판정하지 않음 |
| `vmcu.can.roundtrip` | 기존 classic/FD64 test fixture | `--sil-kit --sil-kit-echo-fixture` | driver TX 완료와 실제 RX payload/IRQ callback; bus frame 발생 |
| `vmcu.can.restart` | `can restart` | transport 복구 후 bus-off 상태 | controller 정상 + 실제 왕복 복구 |
| `vehicle.command` | `vehicle-can.in` typed `command OP ARG` | 현재 epoch/cookie; op5..7은 `--sil-kit-allow-actuation` | 0x600→0x601 transaction 일치 + 동작별 후조건 |
| `vmcu.pfdi.fault-recover` | 실제 AP PFDI agent SIGSTOP | 전용 BSP fault job; reset 허용 | SI fault mask→CAN report→명시적 recover→RUN. 일반 runner FAIL 별도 보존 |
| `vmcu.safety.loss-recover` | 기존 Safety 보고 on/off 시험 | 전용 fault job; watchdog 영향 고지 | UART freshness timeout과 재개, GPIO 경로 독립 관찰 |
| `vmcu.can.disconnect-recover` | 기존 SIL Kit 단절 시험 | 전용 isolated network/fresh-run | bridge 단절→transport bus-off→재연결/restart→왕복 |

현재 vMCU 검증 스크립트는 자체 tmux 세션을 만들고 정리한다. 그대로 live 버튼에서
호출하면 현재 run과 다른 보드를 시험할 수 있다. 검사/evaluator를 작은 공용 함수로
분리해 `existing session` adapter와 `fresh-run CLI`가 함께 사용하도록 만든다.
초기에는 live 조회·AP 제어부터 연결하고 fault 시험은 fresh-run으로 노출한다.

기존 UART 통신의 합성 AP workload/heartbeat 테스트는 현재 health 흐름의 기준으로
되살리지 않는다. UI의 AP health는 SI CL0 PFDI 판정이다. 기존 `heartbeat off` CLI는
**Safety UART 보고 중지 fault 시험**이라는 실제 의미로 표시한다.

## 3. 현재 Apollo QVP validation profile

기준은 [registry](../../scripts/run/qbox_validation/registry.py),
[등록 구현](../../scripts/run/qbox_validation/builtins.py),
[공식 matrix](../../qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml)다.
구현된 11개 profile을 아래와 같이 dashboard job으로 연결한다. 기존 `identical`/
`semantic` coverage 의미와 assertion 결과를 보존한다. 단순 exit code로 PASS를 만들지 않는다.

| Profile | 내용 | 초기 실행 방식/조건 |
|---|---|---|
| `bsp-core` | BSP 핵심 driver/환경 검사 | fresh-run; BSP marker/primary FIFO |
| `platform-devices` | CPU/network/RTC/hotplug/RNG/watchdog 구성 | fresh-run; 네트워크 fixture·도구 필요. hotplug 원복 확인 |
| `trusted-services` | trusted service 경로 | fresh-run; 해당 guest client/firmware 필요 |
| `cpuidle` | idle 동작 | fresh-run; CPU/idle driver 및 timing 관측 |
| `cpufreq` | 주파수/정책 동작 | fresh-run; 정책 변경/원복. host 처리량과 구분 |
| `pfdi` | AP PFDI 검사·오류 주입 | fresh-run; SI 감시와 AP fault 영향 |
| `pfdi-si-cl1` | SI CL1 PFDI 검사 | fresh-run; SI CL1 shell/image 조건 |
| `ras_cpu` | CPU RAS 주입·guest 관측 | fresh-run; correctable/uncorrectable 포함, 정상 보드와 분리 |
| `safety-diagnostics-tests` | SI FMU/SSU integration test | fresh-run; SI0 console/test firmware 조건 |
| `si-cl1` | SI CL1 기능 검사 | fresh-run; Zephyr console·장치 조건 |
| `smcf` | SI SMCF test | fresh-run; SI0 console, 반복 assertion |

Matrix에는 `crypto-extension`, `mbpp`, `hipc`도 있지만 현재 이 registry에 독립 factory가
없다. 이름만 읽어 실행 가능 버튼을 생성하지 않는다. HIPC는 아래 AutoSD/MHU 시나리오의
guest helper로 사용되는 경로와 별도다. 초기 UI는 미등록 이유를 보여주거나 숨긴다.

Canonical runner의 `--validation-profile ID`와 기존 live engine/console writer 계약을
재사용한다. 초기 fresh-run은 alias ID를 등록 profile로 매핑하고 일반 launcher의
post-login probe 비활성 정책을 조용히 변경하지 않는다.

## 4. 기존 AutoSD 시나리오의 조건부 재사용

기반: [server catalog](../../scripts/autosd_dashboard/server.py),
[monitor scenario](../../scripts/autosd_dashboard/monitor_scenarios.py),
[watchdog scenario](../../scripts/autosd_dashboard/watchdog_scenarios.py).

| 기존 시나리오 | 기능 | Saturn-V dashboard 적용 조건 |
|---|---|---|
| S01–S06 | Automotive health, BlueChi, QM/ADAS fault/latch/recovery | 해당 customization/service가 설치된 guest만. BSP 기본 비활성 |
| MC01–MC03 | partition·QM 부하·장애 격리 | cgroup/ADAS/Safety app과 SSH capability 필요 |
| R01–R06, timerlat/osnoise | PREEMPT_RT 측정/지연 검출 | guest 도구·RT image 필요; 측정 중 collector barrier. TCG 관찰 결과 |
| WD01–WD03 | 구성, keepalive, 서비스 watchdog | 장치·systemd helper 조건; WD02는 장치 소유권 배타적 |
| WD04 | SBSA WS1→AP reset→서비스/HIPC 복구 | qbox-full, reset trace, baseline health·boot ID·소유 process 확인 |
| MHU01 (`monitor-mhu`) | lost doorbell→timeout→전체 reset 복구 | startup runtime injection, 실제 target capability, private run. RSE/SI/AP reset |
| `monitor-qualify` | pause/resume 반복·health·WD04 | TC397 미연결 profile에서 우선 유지; board 전체 pause 검증은 아님 |

실행 capability가 없는 image에서 AutoSD health FAIL을 보드 health FAIL로 바꾸지 않는다.
`UNSUPPORTED_IMAGE`와 필요한 package를 표시한다. 기존 AutoSD backend는 그대로 유지한다.

## 5. 보드 제어 범위

| UI 동작 | 범위 | 기본 정책 |
|---|---|---|
| 보드 실행 시작/정지/재실행 | host의 소유 QBox/TC397/participants | 기본 제공. 새 실행은 새 run_id, 기존 증거 보존 |
| AP 종료/wake/복구 | SI/RSE 유지하며 AP 코어 제어 | vMCU 검증 조건 만족 시 제공. Linux 재부팅 관측까지 분리 표시 |
| MCU 재시작 | 독립 TC397만 reset | 명시적 동작, SI epoch/MCU boot 확인. CAN 활성 시 cookie 재협상 |
| QBox 전체 reset | RSE/SI/AP, vMCU는 독립 | 검증된 named scenario에서만. 세션 재협상·stale command 거부 확인 |
| Apollo QBox 일시정지/재개 | QBox 내부 instance | 초기 vMCU 연결 시 비활성. 독립 clock의 가짜 timeout 방지 |
| PMIC 조회 | SI proxy가 rail/STAT 읽기 | 기본 read-only. rail write·PFSM·전체 cold-off는 UNSUPPORTED |
| GPIO raw reset/wake drive | 모델 핀 레벨 | 정상 제어 버튼에 노출하지 않음; named fault 실험 후속 |
| CPU/backend/loopback/SD·disk 설정 | startup Lua/env/artifact | 다음 run 설정. runtime toggle로 오표기하지 않음 |

현재 runtime injection 모델에는 GIC `pulse-spi`, SSU fault, system counter control,
system reset, MHU drop, I2C5 IRQ filter, 일부 PL061 pin action이 있다.
근거: [apollo_runtime_injection.cc](../../hsoc-stack/tools/qbox-platform/systemc-components/apollo_runtime_injection/src/apollo_runtime_injection.cc).
하지만 capability 존재는 해당 guest scenario qualification이 아니다. 초기 UI는 검증된
MHU 등 named action만 허용한다. vMCU/PMIC GPIO는 일반 PL061 injection allowlist에
자동 포함되지 않는다. GIC raw pulse, counter stop, SSU critical fault는 후속 실험으로 둔다.

## 6. 결과 모델

Job 상태 `QUEUED/RUNNING/PASS/FAIL/BLOCKED/UNSUPPORTED/CANCELLED/UNKNOWN`과
`request_receipt`, `observations`, `verdict`, `cleanup_receipt`, `recovery_required`를 분리한다.
Raw runner FAIL, 예상 fault 검증 PASS, 최종 board health는 각각 보존한다.
AP off 시 QBox process가 살아 있는 것, recover RPC가 OK인 것, CAN TX callback 성공은
각각 완료 판정의 일부이며 Linux/PFDI 복귀를 대체하지 않는다.
