# Apollo QVP PSCI CPU/cluster idle

**상태: 2026-10-07 AP4 BSP의 PPU/GIC wake 및 PSCI resume 기능 검증 PASS.
GDB 관측을 포함한 전체 실행의 SCMI timeout-free 보장은 미확정.**

**현재 기본 정책:** 사용자 요청으로 QVP DTS의 deep idle 노드와 CPU 참조를
제거해 architectural WFI로 복귀했다. 아래 powerdown 검증은 idle-states를
복원한 구성에서 수행한 기록이며, 모델/펌웨어 구현은 유지한다. 변경한 DT는
다음 이미지 빌드부터 적용된다.

대상은 Saturn-V `apollo-qvp`, AP 4 CPU, BSP initramfs다.
실행 증거는 `build/qbox-apollo-qvp/psci-powerdown/`에 보관한다.

## 구현 경로

1. Linux PSCI cpuidle이 TF-A에 CPU/cluster powerdown을 요청한다.
2. TF-A가 GIC CPU interface를 비활성화하고 Redistributor를 sleep으로 전환한다.
   A720AE `CPUPWRCTLR_EL1.CORE_PWRDN_EN` 설정 후 EL3 WFI에 진입한다.
3. QEMU의 `powerdown-wfi` 출력이 core PPU의 dynamic OFF 요청으로 전달된다.
   PPU는 OFF 상태와 dynamic-min interrupt를 기록하고 CPU reset을 assert한다.
   일반 WFI는 이 신호를 발생시키지 않는다.
4. 모든 core의 PACTIVE가 내려가면 cluster PPU가 SI CL0에 interrupt를 보낸다.
   기존 SCP 절차가 core OFF-lock을 확인한 뒤 cluster를 static OFF로 전환한다.
5. enabled pending PPI/SPI가 있으면 GIC Redistributor가 CPU interface mask와
   독립적인 wake-request를 발생시킨다. 잠든 CPU에는 일반 IRQ/FIQ 대신 이
   요청이 전달된다.
6. core PPU의 wake demand는 reset 중에도 PACTIVE에 반영된다. cluster가 꺼져
   있으면 SCP가 먼저 cluster ON을 요청하고 core lock을 해제한다.
7. core PPU가 CPU reset을 해제한다. CPU는 RVBAR의 BL2 진입점에서 trusted
   mailbox를 거쳐 TF-A PSCI warmboot 및 suspend 완료 경로로 돌아온다.
   이때 CPU0의 cold-boot loader/보드 전체 reset 신호는 발생시키지 않는다.

이 구성은 기존 SCP의 static cluster 정책을 유지한다. QVP TF-A의
`CLUSTERPWRDN.PWRDN=0`은 cluster powerdown **허용**이므로 변경하지 않는다.
계약의 근거는 [DSU power transition 순서](dsu-120ae/0090-Programming-sequence-for-an-interrupt-controller-to-control-transitions-between-On-and-Off-mode.md)다.

## 소스 소유권

| 저장소 | 변경 |
|---|---|
| `hsoc-stack/tools/qemu` | GIC wake output/WAKER 재평가, A720AE powerdown WFI GPIO, native QTest |
| `hsoc-stack/tools/qbox` | GIC wake output wrapper, bare-metal 테스트의 GICR_WAKER 초기화, GPIO callback 비동기 전달 및 BQL 유지 |
| `hsoc-stack/tools/qbox-platform` | CPU GPIO wrapper, PPU dynamic OFF/lock/IRQ/warm reset, Lua wiring, PPU 검사 |
| `hsoc-stack/components/system_mgmt/scp-firmware` | AP PPU interrupt, cluster 전환 중 wake 보존, 상태 보고 합치기, SMCF SYSTOP 구독 수정 |
| `hsoc-stack/components/primary_compute/linux` | QVP CPU/cluster DT idle-states 복원, NO_HZ_IDLE/HZ100 유지 |

PPU IRQ는 SI architectural INTID 기준 cluster `260 + 5*c`, core
`261 + 5*c + k`다. QEMU SPI socket index는 각각 32를 뺀 값이다.
PPU는 DISR.PACTIVE8, ISR dynamic-min/PACTIVE edge, IMR, IESR 및 OFF-lock/UNLK
계약을 구현한다. OFF-lock을 disable하는 것과 latched lock을 UNLK로 해제하는
것은 별개다. 이미 예약된 wake도 lock 또는 static OFF가 들어오면 CPU를 풀지 않는다.

SCP `cluster_on()`은 기존에 IRQ 호출 경로에서만 falling-edge 감지가 복구됐다.
이를 공통 성공 경로로 옮겨 cold boot의 명시적 ON 요청 후에도 cluster idle을
검출하도록 했다.

## 통합 과정에서 확인한 오류

- AP MMIO broadcast timer의 Lua `irq.0/irq.1` 설정은 실제 SystemC
  `irq_0/irq_1` 포트와 연결되지 않았다. 이전 WFI 경로에서는 쓰이지 않던
  broadcast IRQ를 deep idle에서 사용하면서 드러났다. 실제 포트 이름으로
  수정했다. 수정 전에는 timer IRQ level=1인데 GIC INTID81 level=0이었다.
- GIC wake 출력의 비동기 전달 중 BQL을 해제하면 다른 AP CPU가 아직 끝나지
  않은 GIC MMIO에 재진입한다. `Blocked re-entrant IO on MemoryRegion:
  gicv3_dist`와 Linux external abort가 같은 실행에서 관찰됐다.
- 반복 idle의 매 OFF/ON 보고가 SCP ISR 이벤트 풀에 누적됐다. 명시적인
  전원 제어 응답과 비동기 상태 관측을 구분해 후자를 도메인별 최신 상태로
  합치도록 수정했다. 마지막 성공 상태와 같은 deferred 보고는 생략하며 명시적 완료 보고는 유지한다.
  관련 SCP unit test 및 cluster wake/중복/실패 재시도 회귀 검사 23개가 통과했다.

`boot2`/`debug1`~`debug4`는 IRQ 미연결 조사, `boot4`/`boot5`는 반복 resume
중 재진입/이벤트 풀 실패 증거다. `boot3`는 AP 부팅 전 PMIC rail read 실패다.

- cluster OFF 절차에서 PACTIVE edge 감지가 잠시 꺼진 동안 wake가 도착하면,
  rising edge를 다시 켠 뒤에도 interrupt가 없어서 모든 core가 잠긴 채 남았다.
  SCP가 edge 재활성화 직후 PACTIVE level을 확인해 이미 도착한 wake도 처리한다.
  수정 전 증거: `cpuidle1/cluster-missed-wake.json`.
- SMCF client가 static domain offset인 0을 절대 PD index로 사용해 SYSTOP 대신
  core0를 구독했다. 매 core0 idle마다 5개 MGI가 정지/재시작됐다. core/cluster
  도메인 수를 더한 실제 SYSTOP index로 수정했다. 단위 검사 42개 PASS.
- BusyBox `nproc --all`은 가능한 CPU 16개를 반환한다. AP4 profile은 온라인
  `0-3`을 검증하도록 수정했다. MENU-only kernel과 sysfs trailing whitespace도
  처리하며 알 수 없는/중복 governor 목록은 거부한다.

## 검증

2026-10-07 통합 빌드와 후속 SCP/BSP 빌드가 통과했다.
최종 `cpuidle5/qualification.json`은 아래 범위에서 PASS다.

- Standalone QEMU: PPI/SPI wake, enabled/disabled pending, 일반 WFI와 powerdown
  WFI의 구분 및 reset clear 4개 PASS.
- PPU: core OFF, cluster PACTIVE, OFF-lock/UNLK, queued wake 중 lock/static OFF,
  warm/cold reset 구분 검사 PASS.
- SCP PPU: cluster wake, 중복 보고와 실패 재시도 등 23개 PASS.
- SCP SMCF: SYSTOP 구독을 포함한 42개 PASS.
- QBox native: platform 67/67 및 core 63/63 PASS (`log.do_check`).
- Linux cpuidle profile Python 검사 46개 PASS, static full-map 검사 PASS.
- `cpuidle4/result.json`: BSP full-system boot 및 cpuidle profile **8/8 PASS**.
  CPU0~3 × state0/1/2의 disable, 자연 timer wake, 사용 횟수/시간 증가, governor
  전환 및 원상복구를 확인했다.
- `cpuidle4/gdb-resume3/resume.json`: TF-A
  `psci_cpu_suspend_to_powerdown_finish`의 CPU0~3 `abandon=false` 확인.
  CPU/cluster OFF level 0/1을 관찰했다. TF-A ELF와 배포 FIP hash를 검증했다.
  일부 CPU1 stack memory read는 실패했지만 각 CPU의 함수 진입/인수는 수집됐고,
  breakpoint 제거/detach 후 Linux UART, SCMI 설정 및 PFDI 조회가 계속 동작했다.
- 같은 실행에서 SCMI 1.8/2.0/2.5/1.8 GHz 설정·조회 및 AP 4개 CPU PFDI
  count/result 조회 PASS. 이후 idle SCMI timeout은 재발했으므로 이 실행만으로
  최종 안정성을 주장하지 않는다. 중복 PPU 보고 제거본은 `cpuidle5`에서 별도 검증한다.
- `cpuidle4/qbox-platform.log:16051` 이후 cluster OFF PWSR `0x70000`,
  ON PWSR `0x70008`, core0~3 UNLK `0x1c=1`, warm resume/reset 해제를 확인했다.
- 후속 최종 이미지: `build-ppu-dedup.log` Yocto 5915 tasks PASS.
  `cpuidle5/image-provenance.json`에 배포 artifact hash를 보관한다.

### 최종 이미지 (`cpuidle5`)

- BSP 부팅 및 canonical cpuidle **8/8 PASS**. 모든 4개 CPU의 3개 idle state에서
  사용 횟수/시간 증가와 자연 timer wake, disable/restore를 확인했다.
- SCMI 1.8→2.0→2.5→1.8 GHz 설정 및 읽기 일치, 원래 governor/min/max 복원 PASS.
- 디버거 없이 guest uptime **133.82→193.91초** idle 관측: SCMI timeout **0건**.
  이 수치는 부하 절감율 또는 물리 소비전력 측정이 아니다.
- AP CPU0~3 PFDI count/result와 Online test 0~40 모두 PASS. 기존 sample app을
  다시 시작했다. SI CL1은 부팅/PFDI service ready를 확인했으며 SI 전체 fault
  injection profile을 이번 실행에서 반복한 것은 아니다.
- 이후 GDB에서 최종 이미지의 CPU0~3 `psci_cpu_suspend_to_powerdown_finish`,
  `abandon=false` 확인. CPU/cluster OFF level 0/1을 관측했고 detach 후 UART
  명령 응답과 uptime 259.89초를 확인했다. 일부 stack read 실패는 JSON에 보존했다.
- **제한:** PFDI 온라인 검사 이후 GDB 관측 구간에 SCMI timeout 1건이 있었다.
  GDB는 AP를 멈추는 동안 다른 QEMU domain/타이머의 진행을 막지 않는다.
  그러나 원인을 독립적으로 분리한 것은 아니므로 전체 실행을 timeout-free라고
  주장하지 않는다. 장시간 무계측 안정성 및 GDB 영향 분리 검증은 후속 과제다.
- kernel panic, GIC re-entrant MMIO, SCP event-pool 소진은 관찰하지 않았다.
  테스트가 끝난 후 이 작업에서 실행한 QBox process group을 종료했다.

재현 도구는 evidence 디렉터리의 `run-cpuidle.py`, `capture-psci-resume.py`와
각 run의 `scmi-command.sh`, `idle-command.sh`, `pfdi-online-command.sh`다.
실행한 이미지 hash, TF-A ELF/FIP hash, 원시 UART/PPU 로그 및 모든 실패 실행을
함께 보존했다. 루트 launcher 자체는 boot/login 용도이며 cpuidle qualification은
canonical runner의 `--post-login-probe --validation-profile cpuidle`로 수행한다.

첫 통합 빌드의 platform 검사는 67개 PASS였고 core 검사 중 UART wake 2개가
실패했다. 해당 bare-metal test guest가 GICR_WAKER 초기화를 생략한 것이
확인돼 ProcessorSleep 해제/ChildrenAsleep 확인 절차를 추가했다. 실패 로그는
`build-integrated.log`에 보존하고 재검사는 `build-integrated-retry.log`에 기록한다.

## 검증 경계

DT의 latency/residency 값은 기존 reference 값이다. functional model의
CPU 상태 전환 및 firmware resume 검증이 물리 소비전력, cache 전력 차단,
전기적 isolation 또는 FVP/RTL 시간 동등성을 의미하지는 않는다.
시스템 전체 SYS0 suspend와 Safety Island cluster powerdown은 별도 범위다.

## 2026-10-06 중단 기록과 재개 절차 (과거 상태)

아래는 중단 당시 기록이며, 현재 결과는 위 검증 절을 기준으로 한다.

### 완료 및 미완료 구분

- QEMU GIC wake/PPI/SPI, A720AE powerdown WFI GPIO 구현 및 native QTest 4개 PASS.
- QBox wrapper, PPU OFF-lock/UNLK/PACTIVE/IRQ/warm reset, SCP PPU IRQ 연결,
  Linux CPU/cluster idle-state 복원 구현.
- 최초 Yocto 통합 빌드 PASS: `build-integrated-retry.log`. 당시 platform 67개,
  core 63개 검사 PASS. **이 결과는 아래 후속 수정본의 검증 결과가 아니다.**
- AP broadcast timer의 `irq_0/irq_1` Lua 연결 수정. static full-map PASS.
- 후속 QBox 수정: 외부 GPIO 전달을 항상 비동기로 예약하고 source BQL을 유지한다.
  `runonsysc.h`, `qemu-initiator-signal-socket.h`, PL061 재진입 회귀 검사 변경.
  코드 검토 완료. **후속 수정본의 native/full-system 검증은 아직 미완료.**
- 후속 SCP 수정: PPU별 dynamic 관측 이벤트를 최대 1개로 합치며 최신 상태를 유지한다.
  명시적 전원 제어 보고는 즉시 전달한다. unit test 20개 PASS
  (`scp-coalesce-test.log`). cross compile에서 발견한 `fwk_core.h` include 누락을
  보완했으며, 재빌드에서 SCP compile/package/deploy가 통과했다.
- 마지막 통합 빌드는 QBox 컴파일 중 사용자 요청으로 중단했다.
  로그: `build-reentrancy-retry.log`. 최종 image/provider는 아직 검증되지 않았다.
- 수정 전 `boot4`/`boot5`에서 반복 powerdown/resume은 관찰했지만 Linux panic과
  SCP event pool 소진이 발생했다. **성공한 부팅 또는 지원 완료 증거로 쓰면 안 된다.**
- 실제 TF-A `abandon=false` warm-resume breakpoint, BSP READY 이후 idle 반복,
  CPU/cluster별 cpuidle profile 및 안정성 검증은 남아 있다.

### 재개 명령

공유 BitBake가 종료된 상태에서 기존 설정을 유지해 다시 빌드한다.

```sh
APOLLO_BUILD_THREADS=3 APOLLO_PARALLEL_MAKE=-j4 \
  ./yocto_build.sh --keep-conf scp-firmware qbox-apollo-qvp-native nexios-bsp-initramfs
```

1. QBox native `do_check`에서 PL061 재진입 검사와 기존 UART/timer WFI 검사까지
   통과하는지 확인한다. 중단된 빌드의 provider 경로가 비어 있을 수 있으므로
   재빌드/설치가 끝나기 전에 launcher를 실행하지 않는다.
2. `run_qbox_yocto.sh --bsp --headless --no-vmcu --multi-session
   --no-persistent-rse-state --copy-disks`로 새 디렉터리에 bounded boot 증거를 남긴다.
   이전 실행에 사용한 monitor port는 18110, QMP 디렉터리는
   `/tmp/apollo-psci-qmp`다. 디렉터리는 launch 전에 생성해야 한다.
3. canonical Python runner의 `--post-login-probe --validation-profile cpuidle`로
   state0/1/2, CPU0~3의 자연 timer wake/residency 증가와 설정 복원을 검사한다.
   root launcher는 `--no-post-login-probe`를 추가하므로 resolved command에서
   이를 교체한다. `--dashboard --dry-run` launch specification 생성 시 timeout은 0이다.
4. 생성된 `build/qbox-apollo-qvp/psci-powerdown/capture-psci-resume.py`를 사용해
   BSP READY 후 TF-A 실제 warm-resume을 확인한다. 이 도구는 monitor WebSocket
   QMP bridge로 GDB server를 열며 직접 QMP Unix socket에 연결하지 않는다.
   TF-A ELF/FIP hash 및 실행 PID를 검증하고 CPU0~3의 `abandon=false`를 수집한다.
   breakpoint 관측 후에도 Linux가 계속 동작하는지 별도로 확인한다.
5. cluster PPU의 실제 OFF→ON과 core UNLK 순서, PFDI/SCMI 기존 기능을 확인하고
   본 문서 및 platform README, `doc/qbox-fvp-emulation-project.md`의 지원 상태를 갱신한다.

이번 작업은 커밋하거나 push하지 않았다. 기존 `doc/qbox-runtime-idle.md`,
`doc/scp-idle-ablation.md`, `scripts/test/measure_scp_idle.py`,
`tests/test_measure_scp_idle.py`의 이전 측정 작업은 보존했다.
