# Apollo GIC-720AE 작업 재개 인계서

작성일: 2026-08-05 KST

## 1. 목적과 현재 판정

이 문서는 사용자의 명시적 요청으로 실행 중인 Task를 중단한 시점의 소스,
검증 결과, 미해결 이슈와 재개 순서를 다른 PC와 Agent가 그대로 이어갈 수
있도록 고정한다. 2026-08-03 인계서 이후의 Task 13 완료와 Task 15 추가
디버깅 결과를 반영한 최신 기준이다.

현재 결과는 **중간 checkpoint**이며 GIC-720AE FVP parity 완료가 아니다.
Prometheus plan의 top-level 항목 46개 중 21개가 완료됐고 25개가 미완료다.
Task 15와 final qualification이 닫히지 않았으므로 plan의 Task 45/46도
완료로 체크하지 않는다. 이 인계 시점의 signed commit과 push는 사용자가
승인한 checkpoint publication이며 final release closure가 아니다.

중단 시점에 현재 UID 소유의 QBox, QEMU, SystemC, GDB, runner와 관련 tmux
session이 남아 있지 않음을 확인했다. 다른 사용자의 process나 session은
변경하지 않았다.

## 2. 재개 기준

### 2.1 활성 구성

| 항목 | 값 |
| --- | --- |
| top branch | `feature/qbox-rebase` |
| QBox platform branch | `qbox-timer` |
| machine | `apollo-qvp` |
| RD-Aspen variant | `cfg2` |
| Primary Compute CPU | 4 |
| QBox SI topology | `--si-single-gic` opt-in, split rollback 유지 |
| local build | `build/local-apollo-qvp` |
| plan | `.omo/plans/apollo-gic720ae-implementation.md` |
| plan SHA-256 | `e2cec0537121b17f2e8be1cd0314f0ae4def2fe8c6e13d24b0049ff6c0d40e8a` |
| ledger | `.omo/start-work/ledger.jsonl` |
| ledger SHA-256 | `875a8e42ae2483fd93f3ea52f245d2ac64a97972befa937e230e1a9b4a2d51ba` |
| latest ledger event | seq 101, Task 16 dispatched |

checkpoint의 최종 commit SHA는 아래처럼 top branch와 submodule pointer에서
직접 확인한다. 별도 nested branch를 임의로 조합하지 않는다.

```bash
git clone --recurse-submodules \
  git@github.com:cometzero/project-apollo.git arm-auto-solutions
cd arm-auto-solutions
git checkout feature/qbox-rebase
git submodule sync --recursive
git submodule update --init --recursive
git rev-parse HEAD
git submodule status --recursive
```

### 2.2 완료 상태

현재 plan에서 완료된 항목은 다음과 같다.

```text
1-14, 20-23, 29-31
```

Task 13은 single-SI의 active SGI/PPI/SPI ownership route와 BQL teardown
문제를 해결하고 독립 검증까지 완료했다. 이후 Task 15 디버깅은 그 경로를
사용해 SI0의 INTID 105가 실제 `mhu3_isr`까지 전달되는 것을 확인했다.

완료 표시는 각 Task 당시의 acceptance evidence에 대한 표시다. 현재 전체
tree의 fresh Linux/SCP/Zephyr/FVP final qualification을 뜻하지 않는다.

## 3. 이번 checkpoint의 소스 변경

### 3.1 QBox platform

소유 저장소: `hsoc-stack/tools/qbox-platform`

- `gic720ae_power_bridge`가 interrupt rising edge에서 backend
  `GICR_WAKER`를 다음 SystemC delta cycle에 읽고 redistributor power state를
  동기화한다.
- QEMU MMIO callback 안에서 즉시 다시 MMIO를 수행해 발생했던
  `Blocked re-entrant IO`를 피하기 위해 `sc_event` 기반 비동기 동기화를
  사용한다.
- `gicx00_multiview`가 view별 `GICD_CTLR` enable 상태를 보관하고 SCP
  production driver의 정의대로 최종 group enable을
  `view0 & (view1 | view2)`로 backend에 반영한다.
- component test가 backend WAKER asleep/wake에 따른 interrupt 차단/전달과
  view별 `GICD_CTLR` logical-AND 동작을 검증한다.

이 구현은 backend architectural state의 owner를 QEMU GIC로 유지한다.
SystemC에는 power/view integration에 필요한 최소 shadow만 둔다. backend
WAKER 변경은 다음 rising interrupt에서 동기화되므로, 이것을 독립적인
power-state notification model로 과장하면 안 된다.

### 3.2 top launcher

- `run_qbox_local.sh`가 `--debug si_cl0|si_cl1`의 noninteractive
  `probe/server` 경로에도 `--si-single-gic`를 전달한다.
- 회귀 test는 dry-run command에서 canonical 5-PE topology option이 실제
  child runner까지 전달되는지 검증한다.

이 수정은 Task 16 전체 완료가 아니다. 같은 endpoint에서 CL0/CL1 selector,
5개 thread, MPIDR, breakpoint/continue를 실제 GDB로 다시 검증해야 한다.

## 4. Task 15 디버깅 결과

### 4.1 해결된 문제

#### A. backend WAKER와 bridge state 불일치

초기 bridge state는 awake였지만 QEMU backend redistributor는 asleep일 수
있었다. 반대로 backend를 wake한 뒤에도 bridge가 stale asleep 상태이면
interrupt를 계속 차단했다. backend WAKER ownership을 포함한 failing-first
component test를 추가하고 다음 delta cycle의 `transport_dbg` read로 상태를
동기화했다.

동일 callback 안의 즉시 read는 아래 경고를 발생시켰다.

```text
libqbox: warning: Blocked re-entrant IO on MemoryRegion:
gicv3_redist_region[0] at addr: 0x14
```

비동기 수정 후 같은 경고는 재현되지 않았고 asleep일 때는 전달 0회,
backend wake 뒤에는 전달 1회 이상을 component test에서 확인했다.

#### B. multiview GICD_CTLR enable 결합

View0와 active view의 `GICD_CTLR` group-enable write를 그대로 backend에
forward하면 마지막 writer가 다른 view의 enable을 덮어썼다. SCP production
driver의 다음 계약을 소스에서 확인했다.

```text
The final GICD_CTLR result of each view is the LOGICAL AND of
the GICD_CTLR from view-0 and the GICD_CTLR from each view.
```

이에 따라 view 상태를 분리하고 backend에는
`view0 & (view1 | view2)`를 반영했다. 단순 OR 구현은 채택하지 않았다.

#### C. INTID 105가 SI0 ISR까지 도달하지 않던 문제

수정 전에는 INTID 105가 pending/enable 상태여도 SI0 handler가 실행되지
않았다. 수정 후 guest GDB에서 아래 순서를 확인했다.

```text
TASK15_ENABLE_CALL irq=105
TASK15_ENABLE_RET status=0
TASK15_IAR intid=105 raw=0x69
TASK15_MHU3_ISR pc=0x12001d3c8
```

backtrace는 `mhu3_isr -> irq_global -> fiq_handler`였다. 따라서 현재 최초
blocker를 GIC pending/CPU interface/ISR route로 계속 분류하면 안 된다.

### 4.2 통과한 검증

| 검증 | 결과 | 로컬 evidence |
| --- | --- | --- |
| QBox-only build | PASS | `build/task15-debug/final3-local-build-qbox.log` |
| power bridge + multiview CTest | 2/2 PASS | `build/task15-debug/green-async-power-ctest.log` |
| noninteractive topology regression | PASS | `build/task15-debug/green-noninteractive-single-gic-test.log` |
| launcher child command | `--si-single-gic` 포함 | `build/task15-debug/green-launcher-command.log` |
| SI0 guest GDB | INTID 105 IAR/ISR 확인 | `build/task15-debug/final3-si0-intid105-gdb.log` |

`build/` 아래 evidence는 Git에 publish하지 않는 생성물이다. 다른 PC에서는
아래 재현 명령으로 fresh evidence를 생성한다.

### 4.3 현재 blocker: RSE SCMI 재시도 창과 SI0 준비 시간

headless full-system run은 아직 실패한다.

```text
result blocker: qbox_platform_failed:-15
RSE BL2: Getting SCMI power domain protocol version... (3회)
RSE BL2: SCP is not ready. Abort
SI0: [17.059148] [FWK] Module initialization complete!
```

RSE BL2는
`trusted-firmware-m/.../apollo-qvp/bl2/boot_hal_bl2.c`에서 세 번만 protocol
version을 요청하고 각 실패 사이에 `SCMI_BUSY_WAIT_CYCLES=10000000`만큼
기다린다. QBox에서 SI0 framework가 약 17초 뒤 준비되기 전에 RSE가 abort
한다. INTID 105의 실제 ISR delivery는 별도 GDB로 확인됐으므로 현재 문제는
SCMI interrupt route가 아니라 **QBox의 RSE/SI0 상대 실행 시간과 firmware
startup ordering**이다.

다음 timing 실험은 모두 같은 SCMI abort로 끝났으며 소스에는 반영하지 않았다.

- RSE `multithread-quantum`
- 전체 QEMU instance `multithread-quantum`
- RSE TCG `SINGLE` + `singlethread-quantum`

RSE retry count나 busy wait를 바로 늘리는 변경은 QBox 전용 firmware
workaround가 될 수 있으므로 현재 checkpoint에 넣지 않았다. 먼저 SI0가
17초를 소비하는 구간을 FVP와 비교하고 QBox의 time synchronization/DMI/
device latency 중 어느 경계가 잘못됐는지 확인해야 한다.

### 4.4 Task 15 재개 순서

1. top branch와 submodule pointer를 맞춘 뒤 QBox만 빌드한다.

   ```bash
   ./local_build.sh qbox
   ```

2. power/multiview component test를 먼저 실행한다.

   ```bash
   ctest --test-dir build/gic720ae-qbox-platform-tests \
     -R '^(gic720ae_power_reset-tests|gicx00_multiview-tests)$' \
     --output-on-failure
   ```

3. headless full-system으로 최초 실패 로그를 다시 고정한다.

   ```bash
   python3 scripts/run/run_qbox_apollo_fvp_full.py \
     --timeout 600 \
     --skip-build \
     --si-single-gic \
     --no-post-login-probe \
     --out-dir build/task15-resume/headless
   ```

4. `qbox-rse.log`의 첫 SCMI request/abort와
   `qbox-safety-island-cl0.log`의 framework/module별 timestamp를 비교한다.
   SI0의 긴 초기화 구간을 먼저 좁힌 뒤 그 구간의 QBox/SystemC source만
   GDB 또는 trace로 확인한다.

5. GDB server를 사용할 때 endpoint에 TCP health check를 하지 않는다.
   첫 연결이 debugger session을 소비할 수 있다. `qbox-platform.log`의
   breakpoint-ready marker를 기다린 뒤 한 번만 attach한다.

   ```bash
   ./run_qbox_local.sh \
     --debug si_cl0 \
     --debug-mode server \
     --out-dir build/task15-resume/gdb \
     --no-persistent-rse-state
   ```

6. RSE와 SI0의 상대 실행 시간을 바로잡은 뒤에만 Task 15의 production SCP
   Test Driver와 3-cycle PWRR/WAKER/reset qualification을 다시 실행한다.

   ```bash
   python3 scripts/test/run_gic720ae_p0_power_reset.py \
     --out-dir build/task15-resume/power-reset
   ```

Task 15 PASS는 component test나 INTID 105 ISR만으로 선언하지 않는다. 실제
SCP production power API를 사용한 3회 연속 down/asleep/up/wake/reset cycle과
negative ordering 결과가 모두 있어야 한다.

## 5. 남은 Task 계획과 이슈

아래 표는 현재 미완료 top-level Task 25개를 정확히 한 번씩 포함한다.
`우선순위`는 재개 순서이며 plan의 acceptance 조건을 줄이지 않는다.

| 우선순위 | Task | 현재 상태/이슈 | 다음 완료 조건 |
| --- | --- | --- | --- |
| P0 | 15 | component/GDB 부분 PASS, RSE가 SI0 SCMI ready 전에 abort | QBox timing 원인 수정 후 production SCP 3-cycle power/reset PASS |
| P0 | 16 | launcher topology 전달만 수정, 실제 selector/thread 검증 미완료 | endpoint 12341에서 CL0/CL1 selector, 5 thread, MPIDR, continue 확인 |
| P0 | 17 | 13/15/16 선행 조건 중 15/16 미완료 | SCP CL0 controlled IRQ/FMU command와 negative runtime PASS |
| P0 | 18 | 13/15/16 선행 조건 중 15/16 미완료 | Zephyr CL1 directed/broadcast IPI, timer PPI, cross-view negative PASS |
| P0 | 19 | 15-18 미완료로 single-SI default 전환 금지 | 동일 source SHA에서 single default와 split rollback 모두 PASS |
| P0 | 27 | 구현 lane은 있으나 Yocto tuple 생성이 host userns 정책에 막힘 | user namespace 허용 host에서 kernel/DTB/WIC/qboxconf/module tuple 생성 후 Linux runtime PASS |
| P1 | 24 | 미구현 | QEMU-owned GIC-720AE IIDR property와 AP/SI readback PASS |
| P1 | 25 | Task 24 선행 | `spi/espi/ppi/eppi` socket ABI/property CTest PASS |
| P1 | 26 | Task 19/25 선행 | SI capacity와 extended-range SCP/Zephyr runtime PASS |
| P1 | 28 | Task 27 선행 | AP PCI MSI-X→ITS→physical LPI와 INTx 비교 PASS |
| P2 | 32 | opt-in KVM software-vLPI 범위, hardware forwarding gap 유지 | software-vLPI probe와 미지원 hardware gap을 분리 기록 |
| P1 | 33 | Task 17 선행, SPI collator availability 불확정 | controlled preflight 뒤 active일 때만 message path 검증 |
| P1 | 34 | Task 33 선행 | GIC FMU SystemC model과 `zena_fmu` 연결 CTest PASS |
| P1 | 35 | Task 17/34 선행 | SCP production FMU driver/test로 end-to-end fault PASS |
| P1 | 36 | Task 17/18/26/35 선행 | 공개 RAS/GSPV error/correction/flush 경로 PASS |
| P1 | 37 | Task 15/19 선행 | low-power, CPU hotplug, system reset fresh qualification PASS |
| P1 | 38 | SI feature chain 선행 | 동일 stimulus의 SI FVP/QBox differential PASS |
| Gate | 39 | Task 1-38 closure 전 freeze 금지 | scope audit, repository SHA/pointer, input manifest 고정 |
| Gate | 40 | Task 19/26/27/32/38/39 선행 | fresh Primary Compute Linux final qualification PASS |
| Gate | 41 | Task 19/26/32/38-40 선행 | fresh SI CL0/CL1 final qualification PASS |
| Gate | 42 | Task 33/40/41 선행 | fresh FVP differential과 full coverage audit PASS |
| Gate | 43 | Task 39-42 선행 | 한글 계획/분석/test-completion 문서와 evidence 동기화 |
| Gate | 44 | Task 1-43 선행 | read-only repository/pointer/rollback release exit gate PASS |
| Gate | 45 | Task 44와 final review 선행 | final source SHA에 대해 signed atomic commit closure |
| Gate | 46 | Task 45 선행 | changed nested-first/top-last push 및 remote SHA 일치 |

### 5.1 Task 27 별도 환경 blocker

Task 27의 host-tools, kernel, Yocto profile 구현 lane은 완료됐지만 통합은
`key-store:do_unpack`의 `/proc/self/uid_map` 쓰기 `EPERM`으로 중단됐다.
현재 host의 AppArmor/userns 정책을 약화하거나 BitBake isolation을 우회하는
소스 변경은 하지 않는다. user namespace가 허용된 다른 PC에서 기존 builder
command로 유효 tuple을 생성한 뒤에만 QBox Linux probe를 실행한다. 자세한
기존 evidence와 명령은 `deferred-tasks-todo.md`의 Task 27 절을 참고한다.

## 6. 다른 PC/Agent의 최소 실행 전략

1. Task 15 timing blocker를 먼저 해결한다. QBox-only 변경이면 반드시
   `./local_build.sh qbox`만 사용하고 headless runner로 검증한다.
2. Task 16은 Task 15 debug와 같은 boot를 재사용하되, GDB endpoint를 TCP로
   선접속하지 않는다.
3. Task 15/16 이후 Task 17과 18을 SCP CL0/Zephyr CL1로 병렬화할 수 있다.
4. Task 17/18이 통과한 동일 source SHA에서만 Task 19 default 전환과 split
   rollback을 수행한다.
5. Yocto image가 실제 acceptance에 필요한 Task 27/40에서만 Yocto를
   수행한다. QBox/SystemC/QEMU 변경의 중간 검증에 Yocto를 사용하지 않는다.
6. P1/P2 feature를 build-only, marker-only, TCP-connect-only evidence로
   완료 처리하지 않는다.
7. Task 39 이후에는 source를 변경하지 말고 동일 SHA에 final Linux/SI/FVP,
   review, commit, push receipt를 묶는다.

## 7. 재개 시 필수 확인 목록

- [ ] top branch와 recursive submodule pointer가 publish된 checkpoint와 일치
- [ ] `git status --short`에서 예상하지 않은 user change가 없음
- [ ] `./local_build.sh qbox` PASS
- [ ] power bridge/multiview focused CTest 2/2 PASS
- [ ] headless log에서 최초 실패 domain과 timestamp 재측정
- [ ] GDB attach 전 endpoint TCP probe를 하지 않음
- [ ] RSE, SI0, AP 등 active QEMU/SystemC pause domain을 함께 제어
- [ ] Task 15의 3-cycle production Test Driver PASS 전 완료 표시 금지
- [ ] Task 27은 userns 가능 host의 fresh tuple 전 runtime 금지
- [ ] generated `build/` evidence와 Git-tracked source evidence를 구분
- [ ] 각 nested repository commit/push 후 top submodule pointer commit/push

## 8. 명시적 비완료 경계

- GIC-720AE FVP parity는 완료되지 않았다.
- Task 15의 production 3-cycle power/reset runtime은 PASS하지 않았다.
- RSE SCMI retry 확대는 구현하지 않았다.
- Task 16의 실제 5-thread GDB selector qualification은 완료되지 않았다.
- Task 27의 fresh Yocto Linux runtime은 host userns 정책 때문에 완료되지
  않았다.
- Task 40-44의 final qualification/review는 수행하지 않았다.
- 이번 Task 45/46 성격의 commit/push는 사용자 승인 checkpoint이며 plan의
  final Task 45/46 completion이 아니다.
