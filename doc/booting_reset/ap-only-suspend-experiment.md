# CL1 초기 OFF 상태에서 AP suspend 시험

이 시험은 CL1 context 복귀를 제외하고 AP domain OFF→ON 및 기존 OS context
복귀를 우선 확인한다. 기본 제품의 deep-suspend capability gate는 유지한다.
시험 옵션을 켰다는 사실이나 OS `mem_sleep`의 `deep` 노출은 성공 증거가 아니다.

## 시험 구성

- `SCP_APOLLO_FVP_ISOLATE_CL1=1`: CL1 하드웨어와 PD topology를 유지하면서
  최초 CL1 ON 요청을 생략한다. 초기 OFF는 Iris PWSR로 별도 확인한다.
- CL1 PFDI는 최초 alarm만 생략하고 PD notification 구독을 유지한다.
  AP 감시는 기존 동작을 유지한다.
- `APOLLO_FVP_TEST_SUSPEND_WAKE_US=5000000`: SLEEP0를 AP SYS0 OFF로 매핑하고
  CL0 timer의 독립 alarm으로 5초 후 wake를 요청하는 시험 전용 backend다.
  기존 timer IRQ34 ISR을 교체하지 않는다.
- AP 마지막 코어 OFF 완료는 별도 bounded polling으로 실제 PWSR을 읽는다.
  SYS0 OFF 확인 전에 wake alarm을 시작하거나 OFF 완료를 만들어내지 않는다.
- CMake는 CL1 isolation 없이 시험 wake를 활성화하는 구성을 거절한다.
  두 옵션의 제품 기본값은 각각 0이다.

`build/conf/apollo-fvp-suspend-test.conf`를 명시적인 BitBake `-R` 입력으로만
사용한다. `local.conf`에는 include하지 않는다. 해당 입력을 사용한 BSP 빌드가
공유 deploy 이미지를 시험 이미지로 교체하므로 시험 종료 후 기본 BSP를 다시
빌드해야 한다. 공유 빌드는 직렬로 실행한다.

```bash
source layers/poky/oe-init-build-env build
bitbake -R /build/arm/arm-auto-solutions/build/conf/apollo-fvp-suspend-test.conf nexios-bsp-initramfs
```

## 판정

1. CL1 cluster 및 4개 core PWSR=OFF, CL0/RSE 실행 및 AP Linux 부팅.
2. Linux deep-suspend 진입과 마지막 AP core/cluster 및 SYS0의 실제 OFF.
3. CL0 timer wake 및 SYS0→cluster→core ON.
4. 원래 OS 실행 복귀. Probe는 boot ID, shell PID와 변수, 4 KiB tmpfs 데이터의
   SHA-256을 비교한다. 이는 OS 수준 witness이며 전체 CPU/device context 검사는 아니다.
5. AP SRAM hash와 mailbox는 OFF 전후 관찰을 비교한다. OFF를 거치지 않은
   동일 hash나 FVP에서의 우연한 SRAM 유지로 하드웨어 retention을 주장하지 않는다.

`scripts/debug/probe_fvp_cl1_initial_off.py`는 별도 Iris observer이며 전원 상태를
쓰거나 CPU별 execution gating을 하지 않는다. 전역 debug pause가 timing에 영향을
줄 수 있고 이산 sampling은 연속 상태의 증명이 아니라는 한계가 있다.

CL1 OFF 상태에서는 기존 BSP initramfs의 remoteproc/RPMsg 검사가 실패할 수 있다.
`probe_apollo_fvp_suspend.py --cl1-isolated`는 명시적인
`--allow-bsp-failure-shell`을 runner에 전달해 `nexios-bsp-failed#`에서도 진단
명령을 실행한다. Boot 판정 기준이나 실패 로그는 완화하지 않는다. Context
witness용 tmpfs는 `/tmp` 아래 새 임시 디렉터리에 mount하고 시험 후 해제한다.
시험에서는 `--min-runtime`을 전체 timeout과 같게 설정해 console error만으로
조기 종료하지 않는다. Process 종료와 post-login timeout은 여전히 적용된다.

## 첫 실행: 2026-09-14

`build/fvp-boot/ap-only-suspend-cl1-off-20260914/`:

- 시험 BSP 빌드 5091 task 완료. 관련 root host 검사 44개 PASS 시점의 이미지.
- RSE는 CL1 이미지를 먼저 적재한 뒤 CL0를 reset에서 해제했다.
- 네 CL1 core는 PWSR=0이지만 cluster는 `0x1070008`, PWPR=`0x1000008`로 ON.
  최초 core ON 요청 생략만으로 전체 CL1 OFF를 보장하지 못했다.
- AP Linux는 진단 shell까지 도달했으나 remoteproc/RPMsg 검사 FAIL.
- 기존 runner는 실패 shell을 인식하지 못했고, 별도 console 명령도 `/dev/shm`
  부재로 setup 실패했다. **AP suspend 요청과 SYS0 OFF는 아직 수행되지 않았다.**
- 이 결과로 runner의 명시적 진단 shell 지원과 전용 tmpfs witness를 추가했다.
  CL1 cluster OFF는 RSE의 이미지 적재 완료 이후 별도 요청과 실제 PWSR 확인이 필요하다.

`ap-only-suspend-cl1-off-r2-20260914/`에서는 새 OFF guard가 SCP 초기화 시
assertion을 일으켜 AP 부팅 전에 종료되었다. PD `get_state`는 상위 domain까지
포함하는 composite state이므로 전체 값을 OFF와 비교하면 안 된다. Leaf mask로
수정하고 core OFF/parent ON 조합의 회귀 검사를 추가했다. CL1 cluster PPU의
동기식 전원 요청에도 시험용 1초 timeout을 설정했다. r2는 suspend 실패가 아닌
**시험 firmware 초기화 실패**로 보존한다.

`ap-only-suspend-cl1-off-r3-20260914/`에서는 canonical runner로 진단 shell에서
메모리 witness를 준비하고 실제 deep suspend를 요청했다. SCP가 마지막 AP core의
실제 OFF를 보고했으나 RSE `Unsupported command`로 runner가 약 103초에 조기
종료했다. 153개 PPU sample에서 SYS0 OFF는 관측되지 않았고 CL1 cluster 역시
ON이었다. Resume는 미검증이다. 이후 PPU driver의 cluster OFF/ON 반환값 무시를
수정해 timeout을 성공 report로 승격하지 않도록 했으며, bounded observation을
끝까지 유지하는 runner 옵션을 추가했다.

### RSE 실행 이미지 갱신 결함

r3의 `Unsupported command`는 최신 handler의 동작 증거가 아니었다. Raw
`tfm_s.bin`에는 새 handler가 있었지만 `tfm_s_signed.bin`은 이전 파일이었다.
서명 custom command가 `tfm_s_bin` target에만 의존해 Ninja의 order-only 관계로
생성되었고, raw 파일 변경이 signed output 재생성을 유발하지 않았다.

Owned TF-M `bl2/ext/mcuboot/CMakeLists.txt`에 raw BIN의 파일 의존성을 추가했다.
생성된 Ninja rule의 `CUSTOM_COMMAND bin/tfm_s.bin ... || ...`를 확인했고,
작은 native incremental-build 회귀 검사에서도 raw 변경 후 signed output이
갱신된다. 최신 서명 이미지의 install/sysroot hash 일치와 RSE 실제 UART에서
새 handler 실행을 함께 확인해야 runtime 갱신 검증이 완료된다.

전체 CL1 OFF 시험은 RSE의 기존 `boot_platform_should_load_image()` hook에서
공용 SI 초기화를 유지한 뒤 CL1만 생략하도록 보완했다. Hardware presence나
이미지 ID를 바꾸지 않으며 `APOLLO_FVP_ISOLATE_CL1`은 BL2에만 적용한다.
Yocto에서는 SCP와 같은 `SCP_APOLLO_FVP_ISOLATE_CL1` 값으로 두 옵션을 연결한다.

### r4: CL1 전체 OFF와 AP compute OFF 확인

`ap-only-suspend-cl1-off-r4-20260914/`의 433개 유효 PPU 관측에서 CL1 cluster와
4개 core는 모두 OFF였다. RSE의 새 suspend advisory handler도 실제 UART에서
확인했다. AP는 Linux deep suspend 후 core/cluster PPU가 OFF가 되었지만 SYS0는
PWSR=8로 남았고 OS 복귀는 없었다. 약 244초에 post-login timeout으로 종료했다.
RSE 서명 이미지 갱신 문제와 CL1 초기 isolation은 이 실행에서 해결을 확인했다.

후속 소스 분석에서 `complete_system_suspend()`가 아직 dispatch하지 않은
상위 domain의 current/sent 상태를 requested 값으로 덮어쓰는 것을 발견했다.
그 결과 cluster OFF report 후에도 SYSTOP을 이미 요청했다고 판단해 driver 호출을
생략했다. Scoped Apollo 경로에서 이 선반영을 제거하고, 실제 cluster report 이후
SYSTOP driver를 호출하며 실제 root report 이후에만 current를 갱신하는 native
비동기 순서 회귀 검사를 추가했다. 다른 제품의 legacy bookkeeping은 유지했다.

### r5: 실제 SYS0 OFF와 CL0 fast-channel fault

`ap-only-suspend-cl1-off-r5-20260914/`에서는 SCP가 5.802899초에 실제 SYS0 PPU
OFF를 확인하고 5초 wake alarm을 설정했다. Iris에서도 SYS0 PWSR의 ON(8) → OFF(0)
변화를 확인했으며, 1641개 관측에서 CL1 cluster와 4개 core는 OFF를 유지했다.
그러나 5.840091초에 CL0가 Data Abort에 진입했다. ELR `0x120028e30`은 matching
SCP ELF의 `scmi_perf_fastchannels.c:418`, `perf_fch_process()`의 load 명령이며,
FAR `0xe01b0204`는 전원이 차단된 AP SRAM fast-channel 영역이다. Wake callback,
SYS0 ON, OS context 복귀는 관측되지 않았다. 판정은
`AP_SYS0_OFF_OBSERVED_NO_OS_RESUME`이며 전체 suspend/resume PASS가 아니다.

OFF 시점 debugger SRAM read도 실패했으므로, 이 관측은 SRAM의 접근 불가를
보일 뿐 전원 재인가 후 내용 소실/보존을 증명하지 않는다. 이후 observer는
SYS0 OFF 동안 SRAM을 읽지 않는다. 다음 실행은 debugger 없이 UART만으로 먼저
검사하여 debugger traffic의 영향을 분리한다. SCMI performance의 pre-transition
ACK 전에 접근 gate를 닫고, 이미 큐에 있는 polling과 출력 write도 차단하도록
보완한다. 시험 설정에서는 SRAM 복원 계약이 없으므로 ON 후 polling 재개는
보류한다. 이것은 정상 DVFS 복구까지 검증했다는 의미가 아니다.

### r6: debugger 없는 OFF/wake 실행

`ap-only-suspend-cl1-off-r6-uart-20260914/`는 Iris를 사용하지 않았다. UART에서
5.263110초 FC quiesce → 5.263121초 SYS0 PPU OFF 확인 → 10.263130초 timer wake
요청 → 10.263156초 root ON notification → 10.263217초 AP core ON notification을
확인했다. CL0 Data Abort는 재발하지 않았지만 Linux suspend exit/context witness는
없고 60.263230초 AP PFDI timeout이 발생했다. UART notification만으로 최종
하드웨어 ON 상태를 확정하지 않으며 다음 Iris 실행에서 PWSR와 AP PC를 확인한다.

OFF 직후의 `FWK Error -1` 11개는 별도 잔여 오류다. 소스상 SYSTOP에 연결된
RoS clock element 11개가 SLEEP0 notification을 받으나 driver는 ON만 허용한다.
오류 개수 일치는 원인 추론이며 event별 runtime trace는 없다. 단순 성공 처리하면
AON의 RSE/SI clock까지 STOPPED로 통지하므로 이를 숨기지 않는다. CMN과 cluster
control의 초기화도 one-shot이며 현재 wake 경로에 재초기화 hook이 없다.

### r7: 실제 OFF→ON, warm-resume 진입 후 GIC CPU interface 정지

`ap-only-suspend-cl1-off-r7-iris-20260914/`에서 read-only Iris 관측을 추가했다.
647개 sample을 저장한 뒤 observer만 중단해 live 진단을 수행했다. 따라서 sampler
전체 status는 `INTERRUPTED`이며 이를 PASS로 바꾸지 않는다. 별도 관측 결과는
CL1 cluster/4 cores sampled OFF, SYS0 PWSR `8 → 0 → 8`이다. OFF sample은
7.907588495818초, 다시 ON sample은 12.748328251799초의 simulation time이다.
OFF 구간에는 AP SRAM과 AP core register를 읽지 않았다.

AP core 0의 PC는 12.7483, 21.1413, 29.5285초에 모두 `0xabd4`였다. Matching
BL31 ELF에서 `gicv3_cpuif_enable+204`, SCR_EL3 복원 이후 마지막 `ISB` 명령이다.
추가 live stack에서 `psci_cpu_suspend_to_powerdown_finish+112`와
`psci_warmboot_entrypoint+324`의 return address를 확인했다. Mailbox는 `0x4160`
(BL31 warm entry)이며 ESR_EL3/FAR_EL3는 0이다. 따라서 AP가 실제 TF-A warm
resume 경로를 실행했으며, reset entry 이전에 멈췄다고 설명하면 틀리다.

정지 시 관측값은 GICD_CTLR=`0x37`, GICR_CTLR=`1`, GICR_WAKER=`0`,
GICR_PWRR=`0`이다. PC가 ISB에 고정되는 원인은 아직 미확정이다. PWRR/WAKER
polling 정지, SRAM 내용 소실, CMN 손실로 단정할 근거가 없다. ISB 제거 또는
interrupt group enable 생략으로 우회하지 않았다. BL31 영역은 ON 후 읽히지만
mutable data를 포함한 hash 차이를 retention 증명으로 사용하지 않는다.

최종 판정: **AP SYS0 실제 OFF→ON 및 TF-A warm-resume 진입은 확인했지만,
Linux suspend exit와 원래 OS context witness는 실패/미완료**다. r6의 UART-only
실행에서도 OS가 복귀하지 않았으므로 관측 도구 없이도 end-to-end 실패는 재현된다.
정지 증거 확보 후 root 소유 FVP만 SIGTERM으로 종료하고 실패 artifact를 보존했다.
RTC wake routing, AON counter 연속성, DVFS 재개, 반복 resume는 검증하지 않았다.

### 하드웨어 retention 계약과의 차이

현재 backend에는 CMN reset 후 복구 및 non-retained AP SRAM 복원 절차가 없다.
BL2 entry `0x82000`, BL31 및 mailbox `0x1ff8`이 SRAM에 있으므로, SYS0 ON만으로
원래 context로 돌아온다고 가정할 수 없다. 사용자 retention 계약은 AON 영역과
DRAM만을 보장한다. 관측 결과와 잔여 실패는
[전체 구현 상태](suspend-resume-implementation-status.md)에 기록한다.

## 시험 종료와 기본 이미지 복구

`./yocto_build.sh --machine apollo-fvp --keep-conf --bsp`로 기본 BSP를 다시 빌드했다.
5091 task가 성공했으며 SCP cache의 isolation/wake는 모두 0, TF-M isolation도 0이다.
`local.conf`에 시험 옵션을 영구 include하지 않았다. 시험 소스와 재현 입력은 남기되
공유 deploy는 기본 이미지로 복구했다.

`build/fvp-boot/ap-suspend-default-restored-20260914/`에서 전체 boot runner exit 0,
CL1 4 CPUs/PFDI service, AP remoteproc/RPMsg 및 BSP 검사 PASS를 확인했다.
Linux는 `[s2idle]`만 노출하고 probe는 `UNSUPPORTED_SUSPEND_STATE`로 종료했다.
이는 의도한 deep capability 차단이며 suspend 요청/성공을 뜻하지 않는다.
해당 probe exit 1과 boot runner exit 0을 구분한다.

최종 root 회귀 검사 66개, focused SCP CTest 5개 suite PASS. FC native 검사 11개
PASS는 별도 module 범위다. 변경 repository의 `git diff --check`도 통과했다.
빌드/host 검사는 r7의 OS 복귀 FAIL을 대체하지 않는다. 실행 모델은 모두 정리했다.
