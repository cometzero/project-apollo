# AP SRAM retention 조건의 AP suspend/resume 재검증

2026-09-15. CL1은 임시 OFF로 유지하고 AP SYS0는 실제 OFF→ON을 요청한다.
AP SRAM retention은 CPU/GIC/CMN register retention을 뜻하지 않는다.

## 설정 및 검증 범위

- `APOLLO_FVP_AP_SRAM_RETAINED=1`: Apollo firmware/BSP의 SRAM 보존 계약.
  System suspend capability 자체를 활성화하지 않는다.
- `SCP_APOLLO_FVP_ISOLATE_CL1=1`, `APOLLO_FVP_TEST_SUSPEND_WAKE_US=5000000`:
  별도 시험 빌드에서만 CL1 초기 OFF와 CL0 timer wake를 활성화한다.
- SCMI fast-channel 접근은 SYS0 OFF 전 차단하고 실제 ON 이후 재개한다.
- 시험 callback은 AP 코어 OFF 후 SYS0 OFF 직전과 실제 SYS0 ON 후 코어 release
  전에 firmware가 매핑한 secure/nonsecure SRAM 각 1 MiB를 FNV-1a 64-bit로 비교한다.
  Hash는 CL0 private SRAM에 보관한다. 불일치는 CPU release를 차단한다.
  이는 진단용 fingerprint이며 암호학적 무결성 검사나 메모리 복원은 아니다.
- CL0의 ATW memory region은 `config_armv8r_mpu.c`의 `MPU_ATTR_2`,
  `MAIR_NORMAL_NC`로 설정된다. Hash loop는 volatile read를 사용한다.

설치 FVP의 `--list-params`에는 AP SRAM의 SYS0 OFF retention을 지정하는 별도
public parameter가 없다. `mem_ret`/`full_ret`는 PPU의 지원 상태 설정이며
OFF 상태에서 SRAM만 보존하는 설정과 동등하지 않다. 이를 바꾸거나 OFF를
MEM_RET로 대체하지 않는다. 모델 SRAM 기본 capacity는 128 MB지만 이번 fingerprint
범위는 firmware가 매핑한 2 MiB이며 나머지 capacity는 검사하지 않는다.
설정/문서 조사 증거: `build/fvp-boot/ap-sram-retention-params-20260915/`.

```bash
source layers/poky/oe-init-build-env build
bitbake -R /build/arm/arm-auto-solutions/build/conf/apollo-fvp-sram-retention-test.conf nexios-bsp-initramfs
```

## 판정 기준

SRAM fingerprint 일치와 SYS0 OFF→ON은 각각 확인한다. OS context 복귀는 Linux
suspend exit, 동일 boot ID/shell context/tmpfs witness를 별도로 요구한다.
SRAM 보존만으로 기존 GIC barrier 정지가 해결됐다고 판정하지 않는다.
Iris breakpoint 진단은 timing을 바꾸므로 debugger 없는 실행 결과와 구분한다.

## 실행 결과

### r8: UART-only

`build/fvp-boot/ap-sram-retention-r8-uart-20260915/`:

- SYS0 OFF 확인 5.974790초, CL0 timer wake 10.974799초.
- Secure SRAM FNV64 `7a5c5317b5825af3`, nonsecure SRAM
  `15555ba1e9f93d81`: 각각 OFF 직전과 ON 직후 동일.
- 10.984271초 2 MiB fingerprint match 후 10.984298초 fast-channel polling 재개.
- AP core ON notification 이후 OS 복귀 marker는 없으며 60.984369초 PFDI timeout.
- Root가 해당 진단 실행의 FVP만 SIGTERM으로 종료했다. 전체 timeout 만료로
  종료한 것이 아니며 `AP_SYS0_OFF_OBSERVED_NO_OS_RESUME`를 보존했다.

따라서 mapped SRAM 내용 보존과 polling 재개는 관측됐지만 OS context 복귀는
실패/미완료다. 디버거는 연결하지 않았다. `input-provenance.md`와 SCP/TF-A ELF
사본을 같은 실행 디렉터리에 보존했다.

### r9: Iris 재확인 및 barrier 진단

`build/fvp-boot/ap-sram-retention-r9-iris-20260915/`:

- 720개 Iris sample에서 CL1 cluster/4 core는 sampled OFF였다. SYS0 PWSR은
  ON → OFF(6.8860415059초 sample) → ON(12.2918801745초 sample)으로 바뀌었다.
- Secure SRAM `fa95be70e2be40df`, nonsecure SRAM `15555ba1e9f93d81`은 각 영역의
  OFF 직전/ON 직후 fingerprint가 일치했다. 실행 간 secure hash 차이는 정상적인
  mutable context 차이이며 서로 다른 실행의 hash를 비교하지 않는다.
- ON 후 AP PC는 12.2919, 20.3815, 28.3782초에 모두 `0xabd4`,
  `gicv3_cpuif_enable+204`의 ISB였다. ESR_EL3=0. Polling은 재개됐지만 OS는 복귀하지 않았다.
- Observer를 의도적으로 SIGINT하여 `INTERRUPTED` 결과와 sample을 보존한 뒤
  독점 barrier probe를 실행했다. 첫 `barriers.json`은 SDK callback 대기 timeout으로
  ERROR이며 명령 진행 여부를 판정하는 데 사용하지 않는다.
- SDK callback 대신 raw simulation run/stop으로 재실행한
  `barriers-raw-control.json`은 `DID_NOT_REACH_NEXT_INSTRUCTION`이다.
  Matching ELF/live instruction이 일치하고 실제 run 이후에도 PC=`0xabd4`이며
  다음 DSB `0xabd8` breakpoint에 도달하지 않았다. Cleanup error와 남긴 breakpoint는 없다.
  이 진단은 global stop/run이 timing을 바꾸므로 일반 runtime 성공 증거가 아니다.
- 기록된 ICC_HPPIR0/1=1023, ICC_RPR=255, ICC_IGRPEN0=1, ICC_IGRPEN1_EL3=2,
  ESR_EL3/FAR_EL3=0이다. 정지의 내부 GIC/ISS 원인은 미확정이다.
- Suspend 전 AP PFDI timeout도 관측됐으며, CL1 OFF 상태의 remoteproc/RPMsg 실패와
  함께 기존 log에 남긴다. 정상 전체 BSP boot PASS로 승격하지 않는다.
- 진단 종료 후 root 소유 FVP만 SIGTERM으로 정리했다.

## 결론

AP SRAM retention 계약을 적용했고 **검사한 2 MiB의 실제 OFF→ON 간 내용 보존과
fast-channel 재개는 확인**했다. 그러나 **Linux context 복귀는 실패/미완료**다.
SRAM 손실을 현재 ISB 정지의 원인으로 볼 근거는 없으며, barrier/IRQ enable을
생략하거나 debugger로 register/context를 복원하는 우회는 하지 않았다.
다른 SRAM capacity, RTC wake routing, 실제 DVFS 주파수 변경, AON counter 연속성,
반복 resume cycle은 별도 검증 대상이다.

## 기본 이미지 복구 및 회귀 검사

시험 후 `./yocto_build.sh --machine apollo-fvp --keep-conf --bsp`로 재빌드했다.
SRAM retention=1은 유지하고 SCP/RSE CL1 isolation=0, 시험 wake=0으로 복구했다.
시험 및 기본 BSP 모두 5091 task 성공이다. `local.conf`는 변경하지 않았다.

`build/fvp-boot/ap-sram-retention-default-restored-20260915/`에서 CL1 4 CPUs와
remoteproc/RPMsg를 포함한 전체 boot runner exit 0을 확인했다. Linux `[s2idle]`
노출과 `UNSUPPORTED_SUSPEND_STATE`는 미완성 deep capability 차단의 의도한
결과다. Probe exit 1은 boot 실패나 suspend 실행을 뜻하지 않는다.

Root 회귀 검사 81개, 재빌드한 focused SCP CTest 5개 suite, Python 문법 검사와
변경 repository whitespace 검사 PASS. 실행 모델과 Iris 포트는 모두 정리했다.
이 검사들은 OS context resume 실패를 대체하지 않는다.
