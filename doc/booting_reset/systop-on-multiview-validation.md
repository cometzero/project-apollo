# SYSTOP ON 유지 suspend 및 GIC multiview 검증

이번 조건은 AP core/cluster OFF→ON이며 **SYSTOP domain-off 시험이 아니다**.
CL1 초기 OFF와 AP SRAM retention 계약은 유지한다. TF-A의 기존 GIC save/restore와
ISB/DSB는 그대로 두어 SYSTOP의 실제 전원 상태만 바꾼다.

## 구현

`APOLLO_FVP_SUSPEND_KEEP_SYSTOP_ON=1`에서 SCP의 logical SLEEP0를 SYS0 PPU의
physical ON으로 매핑한다. Framework의 sleep/wake 상태와 실제 전원 상태를 구분한다.
기존 native ON 요청/report 경로를 사용하되 SYS0 OFF write는 하지 않는다.
실제 AP core/cluster PWSR 전체 OFF와 SYS0 PWSR ON을 확인한 뒤 CL0 timer의
5초 wake를 시작한다. SRAM의 OFF 전후 fingerprint 검사는 이 mode에서 제외한다.

로컬 `build/conf/apollo-fvp-systop-on-test.conf`의 내용은 다음과 같다.
기본 `local.conf`에 include하지 않고 시험 빌드에만 `-R`로 전달한다.

```bitbake
SCP_APOLLO_FVP_ISOLATE_CL1 = "1"
APOLLO_FVP_TEST_SUSPEND_WAKE_US = "5000000"
APOLLO_FVP_AP_SRAM_RETAINED = "1"
APOLLO_FVP_SUSPEND_KEEP_SYSTOP_ON = "1"
```

```bash
source layers/poky/oe-init-build-env build
bitbake -R /build/arm/arm-auto-solutions/build/conf/apollo-fvp-systop-on-test.conf nexios-bsp-initramfs
```

## Multiview 소유권과 save/restore 범위

| 항목 | AP GIC | SI GIC |
| --- | --- | --- |
| 관리 View0 GICD | `0x20000000` | `0x30000000` |
| 사용 GICD view | TF-A/Linux View1 `0x20800000` | CL0 View1 `0x30100000`, CL1 View2 `0x30200000` |
| view 할당 주체 | SCP gicx00_multiview | SCP gicx00_multiview |

AP의 16개 redistributor와 지정 NS SPI도 실제 View1에 할당된다. TF-A의 일부
`VIEW0` 매크로 이름만 보고 실제 관리 View0라고 해석하면 안 된다.

근거: SCP `product/automotive-rd/apollo-fvp/si0_ramfw/config_gicx00_multiview.c`,
`product/automotive-rd/module/gicx00_multiview/src/mod_gicx00_multiview.c`,
TF-M Apollo `device/host_device_definition.c`, TF-A Apollo `platform_def.h`.

TF-A generic GICv3 save/restore는 driver가 사용하는 View1의 CTLR와 architectural
SPI 상태 및 현재 CPU redistributor context를 처리한다. 관리 View0의 전역 CTLR,
`GICD_IVIEWR`, `GICR_VIEWR`는 해당 context에 포함되지 않는다. SCP 초기화는
전역 CTLR을 7로 설정하며 effective interrupt group enable은 관리 View0와
해당 view의 enable을 함께 따른다. 따라서 View1 복원만으로 전역 enable과 view
할당의 reset 손실을 복구한다고 볼 수 없다.

Arm TRM도 power-up에서 multiview를 사용할 때 `GICR_VIEWR`를 다른 register보다
먼저 설정하도록 요구한다. [GIC-720AE power-management 순서](https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Other-power-management).

SYSTOP ON 조건의 before/compute-OFF/after 비교는 이 관리 상태의 **보존** 검사다.
실제 multiview reset-loss 후 **save/replay 검증과는 다르며**, generic TF-A에
누락된 multiview context가 자동으로 해결됐다고 판단하지 않는다. SPI pending/
active/enable은 실행 중 변하므로 static view 할당과 구분한다.

## 실행 결과

### r10: UART-only context 복귀

`build/fvp-boot/ap-systop-on-r10-uart-20260915/`에서 SCP가 5.685477초에
AP core/cluster 실제 OFF와 SYSTOP ON을 확인했고 10.685492초에 wake했다.
Linux suspend return=0, 동일 boot ID/shell PID·변수/tmpfs hash를 확인했다.
Arch timer IRQ count는 네 CPU 각각 `[536,537,535,535]`에서
`[869,876,865,857]`로 증가했다. TF-A의 기존 save/restore와 barrier는 바꾸지 않았다.

CL1 OFF 때문에 초기 remoteproc/RPMsg 검사 FAIL과 진단 shell을 사용했으며
결과는 `OS_RETURN_OBSERVED_WITH_BOOT_FAILURE`다. 전체 BSP boot PASS와 구분한다.
Post-login 명령 완료 후 해당 FVP만 SIGTERM으로 정리했다. 이 실행에는 Iris가 없다.

### r11: OS 복귀 재현, observer 실패

`build/fvp-boot/ap-systop-on-r11-iris-20260915/`에서도 OS context 일치와
timer IRQ 증가가 확인됐다. 그러나 observer는 첫 sample 이후 SDK run callback
timeout으로 종료하여 before/OFF/after 비교는 **NOT_TESTED**다. 실패 artifact는
보존하고 raw simulation run으로 observer를 보완했다. 이 실행을 multiview
보존 PASS로 사용하지 않는다.

### r12: compute OFF/ON과 multiview 관리 상태 보존

`build/fvp-boot/ap-systop-on-r12-multiview-20260915/`에서 raw Iris run을
사용한 observer가 812 samples를 저장했다. SCP UART는 5.325812초에
AP core/cluster OFF 및 SYSTOP ON, 10.325825초에 timer wake를 기록했다.
PPU observer는 먼저 core0 ON을 확인한 후 **물리 16개 core와 4개 cluster가
모두 OFF이고 SYS0는 ON인 sample**, 이어서 core0 ON을 확인했다.

`ppu-observations.json`의 독립 판정은 다음과 같다.

- `cl1_sampled_off=true`: qualified samples에서 CL1 cluster/4 cores OFF.
- `ap_compute_off_sampled=true`, `ap_compute_off_on_sampled=true`.
- `sys0_on_during_qualified_samples=true`: SYS0 자체 OFF 시험이 아니다.
- `multiview_ownership_comparison.ap/si=UNCHANGED_SAMPLED`.
- `multiview_save_restore_execution=NOT_TESTED`: 함수 실행은 이 observer로
  확인하지 않았다.

최신 before/compute-OFF/after snapshot 시점은 각각 simulation
6.652489829943 / 7.128160361843 / 12.888574216543초다. Before는 초기
부팅값만 사용하지 않고 OFF 전까지 5 host seconds마다 갱신했으며, after는
세 번째 warm register capture 시점에 다시 읽었다.

| 읽은 관리 상태 | Before | Compute OFF | After |
| --- | --- | --- | --- |
| AP view0/view1 CTLR | `0x37 / 0x37` | 동일 | 동일 |
| AP view2/view3 CTLR | `0x30 / 0x30` | 동일 | 동일 |
| AP 16개 GICR_VIEWR | 모두 `1` | 동일 | 동일 |
| SI view0/view1/view2 CTLR | `0x53 / 0x51 / 0x50` | 동일 | 동일 |
| SI CL0 / CL1 GICR_VIEWR | `1 / 2,2,2,2` | 동일 | 동일 |

Ownership fingerprint는 SCP 지원 SPI INTID 32..991의 `IVIEWR[2..61]`과
AP 16개/SI 5개 redistributor assignment를 포함한다. 모든 가능한 구현 IRQ를
포괄한다고 주장하지 않는다. AP digest는
`94bbc3b080a3d79cf13022642ce32656a6e17df1b14ecd3dd355f94d5e9f636e`, SI는
`6a294b1582726b7c6aebcdfa84e9b252105f242b957815291f59cea2f7588f8b`이며
세 단계가 일치했다. SI view3 CTLR의 접근 오류는 raw JSON에 보존했고 ownership
비교에서 제외했다. CTLR 값은 별도 raw 비교이며 assignment digest에 포함되지 않는다.

Linux는 `__AP_PM_RETURN_RC__=0`, `__AP_PM_OS_CONTEXT_MATCH__`,
`__AP_PM_END__`를 출력했다. CPU0..3의 실제 arch_timer IRQ count는
`[442,441,443,440]`에서 `[783,778,772,766]`으로 증가했다. 따라서 이 조건에서
OS witness 복귀와 네 CPU의 timer IRQ 재개를 관측했다.

Observer의 `status=INTERRUPTED`는 세 번의 warm capture와 OS 완료 후 Iris를
반환하기 위한 의도적 SIGINT이며, 자료 누락을 숨기는 PASS 변환이 아니다.
CL1 isolation으로 인한 초기 BSP boot 실패/진단 shell 사용은 유지되어
`suspend-result.json`은 `OS_RETURN_OBSERVED_WITH_BOOT_FAILURE`, runner exit=1이다.
그 파일의 `domain_power_off_verified=false`는 full SYS0 OFF를 입증하지 않았다는
뜻이며, 별도 PPU JSON의 compute OFF 관측과 구분한다. Root가 이후 해당 FVP를
정리했다. 실행 입력과 matching ELF는 같은 디렉터리의 `input-provenance.md`와
`initial-state.json`에 묶어 보존했다.

이 결과는 **SYSTOP ON 동안 multiview 관리 ownership/control의 보존** 증거다.
관리 view reset 손실 후 저장된 상태를 replay하는 복구 경로, 모든 CPU/device
architectural context, SYS0 전체 OFF 복귀, RTC가 실제 wake 원인이었는지는
검증하지 않았다. Global debugger pause의 timing 영향도 남으며, 별도 r10
UART-only 실행이 OS 복귀의 비-debugger 비교 근거다.

### r13: 실제 GIC context 함수 호출과 OS 복귀

`build/fvp-boot/ap-systop-on-r13-gic-calls-20260915/`에서 별도 Iris client로
다음 TF-A 함수 entry를 순서대로 관측했다. 네 entry 모두 live instruction과
matching `bl31.elf` opcode가 일치했다.

1. `gicv3_rdistif_save` (`PC=0xba64`)
2. `gicv3_distif_save` (`PC=0xaeec`)
3. `gicv3_distif_init_restore` (`PC=0xac90`)
4. `gicv3_rdistif_init_restore` (`PC=0xb72c`)

`gic-context-calls.json`은 `ORDERED_CALLS_OBSERVED`, cleanup error 없음,
owned breakpoints 제거를 기록한다. Probe가 초기 정지 상태로 복원했으므로
마지막 entry에서 root가 raw `simulationTime_run`으로 재개했다. 이후 Linux
return=0, OS context 일치, 네 CPU timer IRQ `[490,487,490,488]` →
`[828,818,819,810]`를 UART에서 확인했다. Entry 관측 자체와 함수 이후 OS
실행 재개 증거를 구분한다. 전체 BSP 결과는 CL1 OFF 때문에 여전히
`OS_RETURN_OBSERVED_WITH_BOOT_FAILURE`다. 완료 후 해당 FVP만 SIGTERM 처리했다.

입력 `initial-state.json`은 r12와 byte-identical이다. ELF SHA-256은
`ab73226d7f836063b775a86373c6324fea8423339061236948a45ab38d5c5b99`이며
r12 디렉터리에 보존된 ELF를 사용했다. 실행 명령:

```bash
python3 scripts/test/probe_apollo_fvp_suspend.py --state deep --seconds 30 --timeout 300 --cl1-isolated --iris-port 17243 --out-dir build/fvp-boot/ap-systop-on-r13-gic-calls-20260915
# 별도 terminal, guest suspend 전에 단독 Iris client로 접속
python3 scripts/debug/probe_fvp_gic_context_calls.py --iris-python build/tmp_baremetal/sysroots-components/x86_64/fvp-rd-aspen-native/usr/lib/fvp/fvp-rd-aspen/Iris/Python --port 17243 --tfa-elf build/fvp-boot/ap-systop-on-r12-multiview-20260915/bl31.elf --output build/fvp-boot/ap-systop-on-r13-gic-calls-20260915/gic-context-calls.json --timeout 150
```

## 회귀 검사 및 남은 범위

- 관련 pytest 98개 PASS, SCP power-domain/notification/state-check/SCMI/PPU
  native CTest 5개 PASS. Root/SCP/BSP diff whitespace 검사 PASS.
- `APOLLO_FVP_SUSPEND_KEEP_SYSTOP_ON`은 Apollo CMake와 BSP 기본값 1이다.
  시험 CL1 isolation 및 강제 timer wake는 정상 BSP에서 기본값 0으로 유지한다.
- Multiview reset-loss save/replay, ITS/LPI/MSI, AON counter 연속성 및 RTC wake
  routing은 미검증이다. 기존 logical SLEEP0의 RoS clock 오류도 별도 잔여 사항이다.
- 사용자 요청대로 이번 실행에서 SYS0 OFF 재시험은 하지 않았다.

### 정상 공유 BSP 복구 확인

`./yocto_build.sh --machine apollo-fvp --keep-conf --bsp`로 5091 tasks 빌드가
성공했다(5034 cached). 실제 SCP CMakeCache는 SRAM retention=1,
KEEP_SYSTOP_ON=1, CL1 isolation=0, test wake=0이다. 이후
`build/fvp-boot/ap-systop-on-default-restored-20260915/`에서 CL1 포함 전체
boot runner exit=0을 확인했다. Deep probe는 `UNSUPPORTED_SUSPEND_STATE`
(probe exit=1)로 기존 정상 제품 capability gate를 유지했다. 시험에서의
compute-only 복귀 성공을 근거로 정상 제품의 미완성 deep capability를
임의로 활성화하지 않았다.
