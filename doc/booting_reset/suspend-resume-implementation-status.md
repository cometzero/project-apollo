# Apollo FVP suspend/resume 구현 상태

2026-09-14~15. 대상: apollo-fvp, cfg2, AP 4 CPUs, SI CL1 4 CPUs.
**AP/SI CL1 domain suspend/resume 구현 완료 또는 검증 PASS가 아니다.**

2026-09-15 최신 조건: 사용자 요청대로 **SYSTOP ON 유지**로 변경했다.
AP SRAM retention과 CL1 초기 OFF 조건에서 AP core/cluster OFF→ON 및 Linux
context 복귀를 재현했다. r12 Iris에서는 physical 16 cores/4 clusters의 OFF와
SYS0 ON 유지, AP/SI GIC multiview ownership/control의 전후 보존을 확인했다.
이는 SYSTOP/GIC 전원 상실 후 복원이 아니라 compute-only suspend 검증이다.
일반 TF-A context에는 관리 View0 CTLR/IVIEWR/VIEWR가 포함되지 않으므로
multiview reset-loss 복원 완료로 해석하지 않는다. 상세 결과는
[SYSTOP ON 및 multiview 검증](systop-on-multiview-validation.md)을 참조한다.

2026-09-15 갱신: 사용자 조건에 따라 AP SRAM retention 계약을 추가했다.
r8 UART-only 및 r9 Iris에서 mapped SRAM 2 MiB의 OFF 직전/ON 직후 fingerprint가
일치하고 SCMI fast-channel polling도 재개됐다. 그러나 AP는 여전히 GIC CPU
interface의 ISB에 머물며 OS 복귀는 실패했다. 상세 설정과 새 증거는
[AP SRAM retention 재검증](ap-sram-retention-validation.md)을 참조한다.
시험 종료 후에는 SRAM retention=1을 유지하고 CL1 isolation/wake=0으로 공유
deploy를 복구했다. `ap-sram-retention-default-restored-20260915`의 전체 boot는
runner exit 0이며 deep suspend capability 차단을 유지한다.

## 이전 AP-only SYS0 OFF 검증 이력

후속 요청에 따라 CL1은 임시 초기 OFF로 유지하고 AP만 시험한다. RSE와 SCP의
CL1 초기 boot를 함께 생략해야 cluster까지 OFF가 된다. Owned BSP metadata에
기본값 0의 시험 옵션을 연결했으며 `build/conf/apollo-fvp-suspend-test.conf`는
명시적인 BitBake `-R` 실행에만 사용한다. `arm-zena-css/`는 변경하지 않았다.

- r5 Iris: CL1 cluster/4 cores OFF, AP SYS0 실제 OFF 확인. 이후 CL0 fast-channel
  load가 OFF된 AP SRAM에서 Data Abort를 발생시켜 wake하지 못했다.
- FC pre-transition quiesce와 queued event/output write 보호를 추가했다.
- r6 UART-only: SYS0 OFF 후 5초 timer wake 및 AP ON notification까지 진행.
  Data Abort는 없으나 OS context 복귀가 없고 AP PFDI timeout이 발생했다.
- r7 Iris: SYS0 PWSR `8 → 0 → 8`, CL1 전체 sampled OFF. AP는 TF-A warm-resume
  경로를 실행한 후 `gicv3_cpuif_enable+204`의 ISB(`PC=0xabd4`)에 정지했다.
  Linux context 복귀는 실패했다. GIC 정지 원인은 미확정이며 SRAM/CMN 손실로
  단정하지 않는다. 실제 stack과 register 증거를 실행 디렉터리에 보존했다.
- 기본 제품은 미완성 deep-suspend capability를 계속 차단한다. 시험용 wake는
  CL0 timer이며 Linux RTC의 실제 wake routing을 검증한 것이 아니다.
- 시험 종료 후 isolation/wake=0으로 공유 BSP deploy를 복구했다.
  `ap-suspend-default-restored-20260914`에서 CL1 포함 전체 boot runner exit 0,
  deep probe는 의도한 `UNSUPPORTED_SUSPEND_STATE`를 확인했다.

빌드 옵션, 변경 사항, 실행별 FAIL과 증거 경로는
[AP-only 시험 기록](ap-only-suspend-experiment.md)을 기준으로 한다.
이하 내용은 이전 단계의 이력이며 당시 이미지/검사 수를 나타낸다.

## 최초에 구현·검증한 범위

- `scripts/test/probe_apollo_fvp_suspend.py`: 전용 FVP에서 Linux RTC alarm을
  설정하고 deep/s2idle suspend를 요청하는 bounded probe.
- `tests/test_apollo_fvp_suspend_probe.py`: terminal command echo 오인 방지,
  unsupported RTC/state, setup 실패, 실제 kernel marker 및 firmware 실패 판정. 6/6 PASS.
- Owned TF-A: system(level 2) topology 및 실제 core 수에 맞는 domain count,
  suspend-finish에서 CSS restore 후 CPU RAS 재초기화.
- Owned SCP: Apollo에서 AP system subtree만 system suspend 대상으로 선택.
  독립 SI CL1 root가 AP suspend를 거절하거나 진행 상태를 취소하지 않도록 수정.
  기존 제품에는 기본 비활성화인 opt-in 설정이다.
- `tests/test_apollo_fvp_psci_topology.py`: 10가지 core 수의 실제 전처리 결과 PASS.
- SCP power-domain CTest 3개 suite, 총 81개 case PASS. 다른 module 전체 검증은 아니다.
- TF-A/SCP 각각 compile 및 apollo-fvp BSP 이미지 재빌드 PASS.
- `arm-zena-css/`, BSP metadata 및 build 설정은 변경하지 않았다.
- Runner는 writable image 복사본을 사용하고 실행 종료 후 자신이 시작한 FVP를 정리했다.

## AP 실제 결과

기본 boot/preflight는 exit 0. Linux는 다음을 노출했다.

```text
/sys/power/state: freeze mem
/sys/power/mem_sleep: s2idle [deep]
RTC: rtc0
clocksource: arch_sys_counter
```

별도 인스턴스에서 실행:

```sh
python3 scripts/test/probe_apollo_fvp_suspend.py \
  --state deep --seconds 10 --timeout 900 \
  --out-dir build/fvp-boot/suspend-deep-20260914
```

RTC `rtc-pl031 300d0000.rtc` alarm 설정 성공 후 `PM: suspend entry (deep)`에
진입했으나 TF-A가 다음 assertion으로 중단했다. Resume marker는 없다.

```text
ASSERT: plat/arm/css/common/css_pm.c:260
```

수정 전 소스의 근거:

- `trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_fvp/include/platform_def.h`:
  `PLAT_MAX_PWR_LVL=ARM_PWR_LVL1`, `CSS_SYSTEM_PWR_DMN_LVL=ARM_PWR_LVL2`.
- 같은 platform의 `apollo_fvp_topology.c`: cluster/core topology만 정의.
- `plat/arm/css/common/css_pm.c:260`: system suspend 진입 시 위 두 level의 일치를 assert.
- `scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_system_power.c`:
  ON/OFF 상태 table 및 `soc_wakeup_irq=FWK_INTERRUPT_NONE`.

위 assertion은 이번 TF-A topology 수정으로 제거했다. 새 TF-A/기존 SCP의
실행(`build/fvp-boot/suspend-deep-topology-20260914/`)은 다음 단계에서 실패했다.

```text
[PD] Invalid system suspend request.
[SCMI] SERVICE0: Cmd [0 (0x12:0x3)] returned error (-3)
ERROR: SCMI system power domain suspend return 0xfffffffd unexpected
```

SCP가 독립 SI CL1의 실행 core까지 AP system suspend 조건으로 검사하는 문제가
있어 위의 opt-in subtree 분리를 적용했다. 새 SCP 포함 실행
(`build/fvp-boot/suspend-deep-scoped-20260914/`)에서는 위 assertion/SCMI 거절 없이
다음 단계까지 진행했다.

```text
[SI0 PLATFORM][SCMI] Performing power state notification request
[INF][SCMI] Power state notification received
[INF][SCMI] Graceful system power state transition requested
[ERR][SCMI] Unsupported command
```

마지막 세 줄은 RSE 로그다. 당시 Owned TF-M Apollo `scmi/scmi_hal.c`의 notification
handler에는 suspend 처리 경로가 없었다. Runner가 error pattern을 검출해 종료했으며
`suspend-result.json`은 `FAIL_OR_INCOMPLETE`, resume marker는 없다. 이는
RTC wake timeout의 증거도, 실제 SYSTOP OFF의 증거도 아니다.

따라서 level 상수만 바꿔 assertion을 제거하는 것으로는 충분하지 않았다.
System topology, SCP suspend state, wake routing, restore 순서를 함께 정의해야 한다.

증거는 `build/fvp-boot/suspend-resume-preflight-20260914/`와
`build/fvp-boot/suspend-deep-20260914/`에 보존했다. 후자의
`suspend-result.json`은 `FAIL_OR_INCOMPLETE`, runner exit 1이며
`domain_power_off_verified=false`, `si_cl1_suspend_verified=false`이다.
`initial-state.json`에 firmware 입력 hash, `result.json`에 실행 command가 있다.

## SI CL1 현재 제약 — 정적 분석

- Owned `zephyr_hsoc_src/boards/hsoc/apollo_fvp_safety_island_c1/`에서
  `CONFIG_SOC_FVP_AEMV8R_SIMULATE_CPU_PM=y`, `CONFIG_PM_CPU_OPS=y`, PSCI 비활성화.
- Zephyr `soc/arm/fvp_aemv8r/aarch64/soc.c`의 simulated `pm_cpu_on()`은
  성공만 반환한다. `drivers/pm_cpu_ops/pm_cpu_ops_weak_impl.c`의
  `pm_cpu_off()`는 `-ENOTSUP`이다.
- 배포 build `.config`는 SMP, tickless, ARM_ARCH_TIMER를 사용하지만 system PM은
  활성화되어 있지 않다. 일반 WFI/WFE idle은 domain-off suspend가 아니다.
- 현재 앱은 read-only reference sample이다. 기능 추가 시 owned
  `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src`를 사용해야 한다.

## SI CL1 실제 PPU OFF 시도

`scripts/debug/probe_fvp_cl1_power_retention.py`는 disposable FVP 전용
`--disposable-power-cycle` 모드에서 SRAM 원본을 보관하고 marker를 검사하며,
core OFF가 실제 확인될 때만 cluster OFF를 요청한다. PWSR/PC/reset을 강제
변경하거나 snapshot을 복원하여 resume 성공을 만들지 않는다.

- CL0 Secure Physical bus의 SRAM write/readback 성공. 같은 경로의 PPU PWPR
  debug write는 실패했다.
- Iris PPU writable resource의 PWPR OFF 요청은 수락했지만 29회 poll,
  simulation 98.67 ms 동안 네 core의 PWSR는 모두 `0x8`(ON)이었다.
- 따라서 cluster OFF는 요청하지 않았고 OFF 후 SRAM retention도 판정하지 않았다.
- 일반 ON 정책과 SRAM 원본, execution gate를 복원하고 자체 FVP를 종료했다.
- 증거: `build/agent-debug/cl1-off-cycle-20260914/power-cycle-resource-polled.json`.
- 판정: 해당 debugger-gated 조건의 OFF 전환 실패. Hardware OFF 미지원이라는
  증거는 아니다. 실제 firmware의 cache/GIC quiesce와 powerdown handshake가 필요하다.
- Probe 최종 cleanup 보강은 정적 검사만 완료했으며 수정 후 전체 재실행은 하지 않았다.

### 실제 firmware PWRDN/WFI 후 재검증

Owned `zephyr_hsoc_src/samples/cl1_powerdown_handshake/`에 opt-in standalone
검증 앱을 추가했다. 별도 CMake build 및 ELF 적재를 사용하며 배포 Zephyr 이미지는
교체하지 않았다. 초기 reset에서의 debugger ELF bootstrap은 context resume가 아니다.

- 첫 앱 시험에서 physical timer 접근의 EL2 trap과 Zephyr 전역 IRQ lock에 의한
  barrier 문제를 확인했다. Local IRQ mask 및 사용 중인 virtual timer만 끄도록 수정했다.
- 최종 실행 `build/agent-debug/cl1-firmware-powerdown-r4-20260914/firmware-powerdown.json`:
  `ready_mask=15`, 네 core 모두 `IMP_CPUPWRCTLR_EL1=1`, `CNTV_CTL_EL0=0`,
  PC=`0x140001050`. 실행한 ELF의 해당 명령은 실제 `WFI`다.
- ELF SHA-256:
  `c6a2be0c37aeb5d7cc6d5050b87f1c838399083726aef5d825d4b50e64a7750f`.
- Iris writable PPU resource로 OFF 정책을 쓴 뒤에도 네 core의 PWSR는
  115 samples / 2.35153749 simulation seconds 동안 `0x8`(ON)에 머물러 timeout했다.
  따라서 cluster OFF는 요청하지 않았고 context resume도 시험하지 않았다.
- 판정: **firmware PWRDN/WFI 도달 확인, 실제 core/domain OFF 실패**.
  FVP의 OFF 미지원 확정이 아니라 추가 PPU handshake/configuration 조사 대상이다.
- 추가 live readback은 core 모두 `PWPR=0`, `PWSR=8`, `DISR=0x100`이다.
  Resource write가 실제 CPU MMIO write와 같은 side effect를 발생시키는지는
  별도 검증해야 한다. SCP 정상 경로는 AE `CLUSTERWRITEKEY=0xba`를 쓴 뒤
  PPU MMIO에 store한다. Resource 값 변경만으로 이 transaction을 입증하지 못한다.
- 이 sacrificial 시험에서는 PFDI 간섭을 막기 위해 CL0 실행을 debug-gate했다.
  그러므로 AON firmware 연속 실행이나 production suspend sequence의 증거가 아니다.

자동화는 `scripts/debug/probe_fvp_cl1_firmware_powerdown.py`이며 failure 시
PC/power/exception register를 보존한다. 초기 API/endpoint 실패와 timer-trap
실패 기록은 삭제하지 않고 별도 run directory에 유지했다.

실제 CL0 CPU MMIO 경로를 분리 검증하기 위해 SCP debug CLI 방식도 시도했다.
`build/agent-debug/cl1-firmware-powerdown-cl0mmio-20260914/firmware-powerdown.json`
기록은 CLI 진입 timeout이며 `ppu_writes=[]`이다. 이 실행에서는 OFF write도
PWRDN도 수행하지 않았으므로 실제 MMIO 경로의 성공/실패 근거로 사용하지 않는다.

그 뒤 기존 SCP `ppu_v1_request_power_mode()`를 CL0에서 실제 실행했다.
`build/agent-debug/cl1-firmware-powerdown-scpcall-20260914/firmware-powerdown.json`
에는 네 번의 AE-key/PPU STR 직후 breakpoint와 정상 return, `PWPR=0` readback이
있다. 실행 함수의 live bytes와 배포 ELF 일치도 확인했다. SCP ELF SHA-256은
`c71851d90a0e52609eef90dad53623866e8217d7e095bb4ad2389e249f657551`이다.
115 poll / 2.3455537168 simulation seconds 동안 PWSR는 모두 ON이었다.
따라서 Iris resource write의 side effect 차이만으로 이 실패를 설명할 수 없다.

이때 CL0 register/stack scratch 복원은 debugger 함수 호출을 끝내기 위한 처리일
뿐이며 domain-off context resume가 아니다. CL1 core register는 OFF 요청 전에
읽지 않았고, 실제 MMIO 경로에서도 PPU acknowledgement를 강제하지 않았다.

GIC quiesce도 단계별로 보강했다.

- `cl1-firmware-powerdown-gic-20260914/`: 네 core 모두 WAKER=6
  (ProcessorSleep/ChildrenAsleep), PWRDN=1, 실제 WFI를 확인했지만 OFF 실패.
- `cl1-firmware-powerdown-localirq-20260914/`: 각 core의 SGI/PPI enable을
  `0x08000005`에서 0으로 변경했고 pending은 전후 모두 0, RWP=0이다.
  WAKER=6 및 실제 WFI 도달 후 실제 SCP MMIO OFF를 요청했으나
  115 samples / 2.3465331704 simulation seconds 동안 PWSR=ON이었다.
- 해당 run의 `postdiag-live-readback.md`에서 CL1 view-0 redistributor
  `0x30060000/0x30080000/0x300a0000/0x300c0000`의 TYPER affinity를 확인했다.
  이 단계까지 PWRR.RDPD는 0이며 쓰지 않았다. CL0의 `0x30040000`은 별도다.
- `cl1-firmware-powerdown-rdpd-20260914/`: matching SCP ELF의
  `set_redistributor_power`를 실제 CL0에서 호출했다. 네 CL1 redistributor의
  PWRR는 `0x100/0x200/0x300/0x400`에서 `0x101/0x201/0x301/0x401`로
  바뀌었으며 STR 직후 breakpoint, 정상 반환 및 RDPD acknowledgment를 확인했다.
  CL0 PWRR=0은 유지하고 RDAG 및 global Sleep은 변경하지 않았다.
  이어 네 core의 실제 PPU OFF store를 실행했지만 115 samples /
  2.3455330804 simulation seconds 동안 PWSR=8, DISR=`0x100`이었다.
  WFI 및 PWRDN=1도 유지되어 **OFF FAIL**이다. 결과 JSON과 추가 readback은
  `build/agent-debug/cl1-firmware-powerdown-rdpd-20260914/`에 보관했다.
  이 결과는 남은 ON handshake 원인이 미해결임을 뜻하며, FVP가 power-off를
  지원하지 않는다는 증거는 아니다. 전용 FVP는 종료하고 포트를 해제했다.

## 확정한 요구사항과 남은 구현

사용자 요구사항은 **AP 및 SI CL1 domain power-off 후 기존 context 복귀**이다.
WFI/s2idle, CPU-only OFF, cold reboot, debugger register 복원은 대체 검증이 아니다.

추가로 사용자가 **Always-on power domain의 메모리와 DRAM은 전원 차단 중
보존된다**고 확정했다. 이는 설계 입력이며 이번 FVP 시험으로 입증한 사실과
구분한다. AP local SRAM 및 CL1 LLRAM에는 이 보존 조건을 확대 적용하지 않는다.
현재 AP BL31은 `0x4000`부터 AP SRAM에 있으며 trusted mailbox도 `0x1ff8`이다.
따라서 DRAM이 보존되더라도 현재 배치 그대로의 BL31/context 복귀는 보장되지 않는다.

### 후속 control-flow 수정

- TF-A의 `CSS_SCP_SUSPEND_GRACEFUL` 요청에 대해 Apollo SCP 정책이 handler를
  건너뛰고 성공 응답만 반환하는 별도 결함을 발견했다. Generic graceful timeout
  callback도 suspend를 실행하지 않는다. Apollo 정책은 이제 suspend를 실제
  handler에 전달한다. 이전 UART 단계 통과만으로 handler 실행을 추론하면 안 된다.
- Scoped power-domain 경로는 요청한 root 상태가 허용되는지 enqueue 전에 검증한다.
  현재 ON-only 정책의 OFF 요청은 명확히 거절하며 비동기 수락을 OFF 성공으로
  오인하지 않는다.
- RSE는 AP suspend notification을 advisory로 처리하고 계속 실행한다. 이미지
  재적재, reset, retained transport 재초기화는 하지 않는다. 이 처리는 OFF 완료
  acknowledgement나 wake 구현이 아니다.
- 실제 RSE handler를 host stub과 함께 컴파일한 회귀 검사 PASS. TF-M compile PASS.
  SCP 정책 host 검사 7개 및 power-domain CTest 83개 PASS.

새 BSP 재빌드 후 `build/fvp-boot/suspend-deep-policy-20260914/`에서 확인:

```text
[SI0 PLATFORM][SCMI] System state 4: execute handler
[SCMI] SERVICE0: Cmd [0 (0x12:0x3)] returned error (-3)
ERROR: SCMI system power domain suspend return 0xfffffffd unexpected
```

실제 handler 경유와 현재 OFF 정책의 거절을 확인했다. TF-A는 이 거절을 panic으로
처리하므로 OS 복귀는 없고 결과는 `SCMI_SUSPEND_FAILED`이다. 성공을 거짓으로
반환하지 않는 것과 OS에 미구현 기능을 광고하지 않는 것은 별개 문제다.
RSE advisory handler는 이 거절 경로에서 호출되지 않으므로 해당 handler의
검증은 현재 host test와 firmware build까지다.

현재 메모리 배치와 필요한 복구 순서는
[retained context 계약](retained-context-contract.md)에 정리했다.

### 미구현 기능의 안전한 노출

SCMI `disable_system_suspend` 설정을 추가했다. 기본 false로 다른 제품의 기존
동작은 유지하고 Apollo FVP에서만 true로 둔다. Suspend capability bit를 제거하되
warm-reset bit는 유지하며, 직접 요청도 policy/notification 이전에 거절한다.
TF-A의 기존 SCMI discovery는 이 bit가 없으면 system-suspend callback을 등록하지
않는다. 전체 복귀 backend 구현 후에만 이 설정을 해제한다.

관련 host Python 검사 24개와 SCP CTest 4개 suite(107 case)가 PASS이며,
이 설정까지 포함한 BSP 재빌드도 PASS이다. 이는 power-off 복귀 PASS가 아니다.

최신 실제 실행: `build/fvp-boot/suspend-capability-gated-20260914/`.
전체 boot 판정 PASS, runner exit 0, 실행 시간 69.628초이며 Linux는
`/sys/power/mem_sleep`에 `[s2idle]`만 노출했다. Probe는 RTC 설정/suspend 요청
전에 `UNSUPPORTED_SUSPEND_STATE`로 종료했다. Probe exit 1은 의도한 미지원
판정이며 boot 실패 또는 suspend 성공이 아니다. 현재 배포 이미지는 이 gate가
활성화된 이미지다.

- AP: SYSTOP OFF 정책, AON wake source→CL0 route, CMN/메모리 유지·복구 계약을
  연결해야 한다. 현재 `soc_wakeup_irq=FWK_INTERRUPT_NONE`이고 SYSTOP 허용 상태는
  ON뿐이다. RTC alarm 설정 성공만으로 domain-off wake route를 증명하지 못한다.
  RSE의 SCMI suspend notification은 후속 advisory handler로 처리한다. CL0 timer IRQ34는 기존
  timer driver가 소유하므로 system-power wake ISR로 덮어쓰면 안 된다.
- CL1: 전체 CPU/device quiesce, retained context 저장, CL1↔CL0 handshake,
  AON wake, reset entry의 warm-resume 분기 및 ARM64 context restore가 필요하다.
  현재 일반 reset 경로는 BSS 초기화로 이어지므로 기존 context resume가 아니다.
- 공통: 실제 PPU OFF→ON, memory/CPU context 일치, timer deadline 처리,
  AON counter 연속성 및 반복 cycle 증거가 있어야 최종 PASS이다.

현재 구현은 위 선행 결함 수정과 재현 가능한 검증 도구까지이며,
**요청한 end-to-end power-off/context resume는 미완료**이다.
