# 현재 구성과 재사용 대상

조사 기준: 2026-10-05 작업 checkout. 이 문서는 구현된 기반을 설명하며
[신규 실행 설계](architecture-ko.md)의 기능 완료를 의미하지 않는다.

## 1. 실행·이미지 소유권

현재 local configuration은 `MACHINE ??= "apollo-qvp"`,
`TMPDIR = "${TOPDIR}/tmp_baremetal"`이며 template은 owned
`meta-hsoc-auto-solutions/conf/templates/apollo-qvp`다. `bblayers.conf`에는
owned BSP/product layer와 외부 Zena/Yocto layer가 함께 있다. 이 값은 조사 당시
파일 내용이고 BitBake effective environment를 새로 평가한 결과는 아니다.
구현 시마다 선택한 `.qboxconf`와 실제 artifact를 다시 해석해야 한다.

| 소스 | 현재 책임 | dashboard에서 필요한 변경 |
|---|---|---|
| [run_qbox_yocto.sh](../../run_qbox_yocto.sh) | `.qboxconf`, 이미지, provider 선택; tmux/headless 분기; post-login probe 비활성 | `--dashboard` 분기, typed launch specification, 웹/보드 수명 연결 |
| [full runner](../../scripts/run/run_qbox_apollo_fvp_full.py) | RSE/SI/AP boot gate, artifact·결과, 지속 실행·검증 profile | foreground 소유 실행, boot deadline와 서버 수명 분리 |
| [runtime](../../scripts/run/qbox_apollo_runtime.py) | 실제 QBox 명령·환경, 콘솔 FIFO/로그, private 이미지, monitor manifest | dashboard에 경로·PID·시작시각·상태 전달 |
| [tmux runner](../../scripts/run/run_qbox_apollo_fvp_full_tmux.sh) | 콘솔 창과 TC397 supervisor 실행 | supervisor 준비 코드를 공통 headless 실행으로 추출; tmux는 보기만 담당 |
| [TC397 supervisor](../../scripts/run/qbox_tc397.py) | 외부 QEMU, console bridge, GPIO/UART endpoint, process 정리 | dashboard도 같은 소유·준비 절차 사용 |
| [SIL Kit supervisor](../../scripts/run/qbox_silkit.py) | registry/bridge/restbus 준비·감시·정리 | manifest와 job adapter 연결 |
| [vMCU boot adaptation](../../scripts/run/qbox_vmcu_boot.py) | unsigned BSP UKI의 private 복사본에 `apollo.vmcu=1` 추가 | 기존 원본 보존·서명 이미지 거부 계약 유지 |

현재 BSP의 vMCU 자동 실행은 **비-headless 경로**에 묶여 있다. `--sil-kit`도
그 조건을 요구한다. 따라서 새 dashboard가 단순히 `--headless`를 덧붙이면
요청한 vMCU 기능이 빠진다. 공통 supervisor 경로를 먼저 구현해야 한다.

현재 `--keep-running-after-pass`는 부모 runner가 반환하고 child를 남기는 경로도
있다. Dashboard 소유 실행은 `--foreground-runtime`을 함께 사용하고, 하위 지속
실행 timeout과 boot deadline를 별도로 관리해야 한다.

## 2. 이미 존재하는 웹 기반

| 소스 | 재사용할 기능 | 현재 격차 |
|---|---|---|
| [server.py](../../scripts/autosd_dashboard/server.py) | HTTP, 인증/Host/Origin/CSRF, job·결과·artifact, backend 선택 | boot가 AutoSD manifest/rootfs/SSH에 결합; BSP serial-only 지원 필요 |
| [topology.py](../../scripts/autosd_dashboard/topology.py) | 제한된 Lua 평가, include SHA, component/binding/주소, draw.io export | 현재 고정 checkout/profile; 실제 provider·override 일치 보장 없음 |
| [topology.js](../../scripts/autosd_dashboard/web/topology.js) | subsystem 전개, 검색, Inspector, zoom, export | 보드 외형·외부 TC397·상태 overlay 추가 |
| [simulator.py](../../scripts/autosd_dashboard/simulator.py), [qbox_monitor.py](../../scripts/autosd_dashboard/qbox_monitor.py) | SystemC 시간/QK/MCIPS, 독립 수집, listener 소유권, 상태 신선도 | Yocto manifest adapter 필요 |
| [qbox_diagnostics.py](../../scripts/autosd_dashboard/qbox_diagnostics.py) | metadata-only Inspector, 제한된 QMP 조회 | 별도 TC397 QMP와 board capability 통합 필요 |
| [qbox_control.py](../../scripts/autosd_dashboard/qbox_control.py) | qualified QBox pause/resume 및 제어 | 독립 MCU/SIL Kit 동시 정지 보장 없음 |
| [qbox_load_stats.py](../../scripts/run/qbox_load_stats.py), [qbox_stats_monitor.py](../../scripts/run/qbox_stats_monitor.py) | `--stats`의 `/proc` CPU/RSS/thread 측정, QMP domain TID 매핑; 기본 5초, monitor/QMP 자동 활성화 | 현재 `LoadStats.poll()`은 text line을 반환해 `qbox-platform.log`에 기록. Dashboard용 structured sample/API/graph는 추가 필요 |
| [telemetry.py](../../scripts/autosd_dashboard/telemetry.py), [guest_monitor.py](../../scripts/autosd_dashboard/guest_monitor.py), [service_logs.py](../../scripts/autosd_dashboard/service_logs.py) | SSH guest metric·서비스 로그 | BSP에는 systemd/SSH가 없을 수 있음; capability 판정 필요 |
| [monitor_scenarios.py](../../scripts/autosd_dashboard/monitor_scenarios.py), [watchdog_scenarios.py](../../scripts/autosd_dashboard/watchdog_scenarios.py) | MHU fault, WD04, 증거와 복구 판정 | AutoSD guest 조건과 전체 reset 영향을 분리 |

기존 API `/api/topology`, `/api/simulator/*`를 보존한다. 현재 AutoSD 화면을 모두
복제하지 않고 backend 계약을 분리한다. 기존 dashboard는 종료 시 guest를 강제
종료하지 않으며 재시작 뒤 진행 작업을 `ORPHANED_NOT_MANAGED`로 취급한다.
새 `--dashboard` 소유 모드는 이 수명 정책을 명시적으로 구분해야 한다.

## 3. Lua 보드와 실제 실행 구성의 차이

주요 소스:

- [Saturn-V entrypoint](../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua)
- [Apollo entrypoint](../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua)
- [board population](../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/saturn-v.lua)
- [기존 연결도 가이드](qbox-topology-guide-ko.md)

현재 topology extractor는 Saturn-V entrypoint를 사용한다. 기존 가이드의
`apollo-qvp.lua`·333 components·1,184 bindings 수치는 이전 snapshot이다.
이번 source 기본 profile 정적 평가에서는 337 nodes / 1,185 edges / 104 sources /
9 groups / warnings 0을 관찰했다. 실행마다 이 숫자를 고정 assertion으로 사용하지 않는다.

보드 population에는 EEPROM, PCA9539, TPS6594가 있고 SoC에는 AP/SI/RSE,
router·memory·UART·I2C·SPI·GPIO·Ethernet·PCIe·audio 등의 모델이 포함된다.
어떤 장치가 켜졌는지, 어떤 sink와 연결되는지는 선택된 Lua 평가 결과를 따른다.
`board/saturn-v.lua`의 실물 schematic parity는 `UNVERIFIED`다.

일반 Yocto 실행은 `.qboxconf`의 native provider data directory에서 설치된 Lua를
선택할 수 있다. 개발 checkout Lua와 설치 복사본은 달라질 수 있다. TCP endpoint,
CPU 수, optional 장치, runtime injection, CCI override도 topology에 영향을 준다.
정적 그래프를 실행 중 객체의 실측 결과로 표시해서는 안 된다.

## 4. vMCU 연결과 현재 기능

TC397은 QBox 내부 QemuInstance가 아닌 **독립 QEMU process**다.
[Zephyr overlay/app](../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src)
및 [현재 동작 시각화](../vmcu/visualization.html)를 재사용 근거로 삼는다.

| 연결 | 현재 경로 | dashboard에서의 의미 |
|---|---|---|
| AP 관리 | TC397 ASCLIN0 ↔ Apollo DW UART2 | ping/status 및 graceful shutdown; health 원천 아님 |
| Safety | ASCLIN2 ↔ SI CL0 PL011 | 기존 PFDI 종합 상태 5초/변화 시 보고, RPC |
| GPIO | TC397 PORT0 ↔ SI PL061 + reset arbiter | SOC_ERROR/PWR_REQ/IST_DONE_N/RESET_N/WAKE |
| MCU console | ASCLIN1 ↔ host console bridge | Zephyr shell, typed `vmcu-cli` adapter |
| CAN | TC397 M_CAN ↔ native SIL Kit bridge ↔ VehicleRestbus | 실제 CAN driver/IRQ와 시험용 FD 메시지 |
| PMIC | vMCU → Safety UART → SI CL0 → I2C TPS6594 | 단일 SI 소유, rail 설정 readback/live STAT 조회 |

AP PFDI → SI CL0 → vMCU → CAN 경로가 상태의 기준이다. Safety UART freshness
15초와 SOC_ERROR edge watchdog 1.5초는 이미 firmware 정책이다. UI의 host 수집 age와
구별한다. GPIO heartbeat, UART report, CAN report는 서로 다른 관측이며 로그가
조용하다는 이유만으로 healthy vMCU를 OFFLINE으로 판정하지 않는다.

최근 [CAN·서비스 구현 기록](../vmcu/can-and-services.md)의 원본 JSON을 확인했다:

| 기존 증거 | 파일의 status | 이 계획에 재사용하는 범위 |
|---|---|---|
| [full-system-sixth](../../build/qbox-apollo-qvp/vmcu-services/full-system-sixth/vmcu-services-result.json) | PASS | PMIC 조회, CAN, MCU reset, AP 복구 및 off/wake |
| [PFDI 고장 실행](../../build/qbox-apollo-qvp/vmcu-services/full-system-pfdi-fault/vmcu-services-result.json) | PASS | AP agent 정지 → SI fault → CAN 보고 → 명시적 복구 |
| [SIL Kit 없는 실행](../../build/qbox-apollo-qvp/vmcu-services/safety-default-regression/vmcu-result.json) | PASS | quiet shell, Safety/GPIO, AP 관리 경로와 감시 독립 |
| [CAN shell 시험](../../build/qbox-apollo-qvp/vmcu-services/can-shell-serialized/result.json) | PASS | 실제 SDK·M_CAN 교환과 transport fault/restart |

이는 **기존 실행 증거 확인**이며 dashboard/headless 통합의 새 검증이 아니다.
의도된 PFDI 고장의 일반 runner FAIL은 전용 검증기의 예상 fault PASS와 함께 유지한다.
PMIC rail power gating, SoC cold-off, 물리 CAN timing, 공통 virtual clock은 미지원이다.

## 5. 조사 방법과 변경 범위

Codebase index의 root generation은 2026-09-30이며 새 `qbox_tc397.py`와
`verify_qbox_vmcu_services.py`는 coverage가 없었다. 해당 파일은 직접 읽었고,
등록된 profile은 실제 registry와 matrix의 교집합으로 확인했다. index refresh나
빌드는 실행하지 않았다. 이번 신규 문서의 소유 repository는 root의 `doc/dashboard/`다.
기존 dirty launcher·firmware·QEMU·Yocto 파일은 이 문서 작업에서 수정하지 않는다.
