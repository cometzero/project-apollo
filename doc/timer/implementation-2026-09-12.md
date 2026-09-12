# Apollo QVP SysTick 및 firmware 단계별 timer 검증

2026-09-12 변경. [이전 조사](test-results-2026-09-11.md)의 QVP SysTick 누락과
SI CL1 주파수 불일치를 대상으로 한다. 이전 실패 기록은 그대로 보존한다.

## 기존 QEMU 모델 재사용

libqemu에 `hw/timer/armv7m_systick.c`의 `armv7m_systick`이 이미 있었다.
QBox Cortex-M55는 QEMU의 전체 ARMv7M container 대신 CPU와 NVIC를 직접
만들어 container 소유 SysTick 생성 과정이 빠져 있었다.

QEMU timer 구현을 추가하지 않고 QBox NVIC wrapper에서 native SysTick을 생성한다.
M55에는 secure/NS bank 두 개를, security extension을 사용하지 않는 wrapper에는
NS bank 하나를 제공한다. Countdown, reload, COUNTFLAG, IRQ 처리는 기존 QEMU
`ptimer`와 SysTick 모델이 수행한다.

| 항목 | 구현 |
| --- | --- |
| Native device | `armv7m_systick` |
| CPU clock | `cpu.nvic.systick_cpuclk_hz`, Apollo 설정 100MHz |
| SCS | `0xE000E000`, SysTick `0xE000E010`부터 |
| NS alias | `0xE002E000`, secure 접근의 SysTick NS bank view |
| Security 선택 | QEMU transaction의 secure/user attributes 전달 |
| Interrupt | native SysTick output → NVIC `systick-trigger[NS/S]` → exception 15 |
| Reset | NVIC cold reset과 두 SysTick cold reset을 같은 iothread lock 안에서 실행 |

Apollo SCS decode 범위는 alias를 포함하도록 `0x21000`으로 확장했다.
SysTick reference clock은 연결하지 않았으며 native 모델의 CPU-clock 선택을 사용한다.
현재 firmware의 `SystemCoreClock=100MHz`와 일치한다. SYSCTRL clock divider 변경을
SysTick clock에 동적으로 전달하는 기능까지 검증한 것은 아니다.

변경 소유권:

- `hsoc-stack/tools/qbox`: `libqemu-cxx` clock/MMIO/reset wrapper,
  `nvic_armv7m`, Cortex-M55 security bank 설정 및 standalone test.
- `hsoc-stack/tools/qbox-platform`: Apollo SCS map/clock,
  `qemu_device_cold_reset`의 compound reset 호출.
- QEMU C 소스는 변경하지 않았다.

## TF-M의 네 단계 검사

`APOLLO_TIMER_TEST` CMake 옵션은 기본 OFF이며 Apollo QVP 전용이다.
Yocto의 `APOLLO_TFM_TIMER_TEST="ON"`으로 활성화한다.
한 부팅에서 BL1_1, BL1_2, BL2, RUNTIME 각각에 다음 5개 검사를 실행한다.

| Timer | 실제 수행하는 검사 |
| --- | --- |
| SysTick | LOAD=999, CPU clock/enable 설정, VAL 변화 및 COUNTFLAG 관측 |
| TIMER0~3 | 125MHz 정보 설정, TVAL=1,250, enable, count 증가/ISTATUS/NVIC pending 관측 |

각 polling loop는 1,000,000회로 제한한다. 하나라도 실패하면 해당 stage에서
실패를 반환하여 다음 firmware로 넘어가지 않는다.
Timestamp timer의 NVIC delivery는 disable하고 pending까지만 검사한다.
SysTick stage 검사도 TICKINT를 켜지 않는다. 실제 SysTick ISR 검증은 별도 M55
standalone test가 담당하며, TF-M ISR을 테스트했다고 해석하지 않는다.

검사 후 SysTick disable/LOAD/VAL 정리, TIMER0~3 disable/CVAL 정리,
CNTFRQ 복원 및 NVIC pending clear를 수행한다. 테스트용 설정이 다음 단계에
켜진 채 넘어가지 않게 한다.

로그 형식:

```text
APOLLO_TIMER_TEST stage=BL1_1 timer=SysTick result=PASS start=... end=... load=999 core_hz=100000000 spins=...
APOLLO_TIMER_TEST stage=BL1_1 timer=TIMER0 result=PASS start=... end=... freq=125000000 pending=1 spins=...
```

`scripts/test/validate_tfm_timer_stages.py`는 네 stage × 다섯 timer의 20개 결과를
각각 정확히 한 번 요구한다. 누락, 중복, FAIL, counter 정지, 주파수 오류 및
pending 미관측은 실패로 판정한다.

## SI CL1 125MHz 정렬

QVP의 `si_cl1.lua` CPU `cntfrq_hz`와 Zephyr QVP board의
`CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC`를 125MHz로 맞췄다.
Timer snapshot의 SI1 주파수도 기존 hard-coded 100MHz 대신 CSS counter의 설정을
사용한다. 이 snapshot 필드를 CPU register 직접 측정으로 간주하지 않는다.

Zephyr QVP board init은 실제 `CNTFRQ_EL0`를 읽어 설정값과 비교하고 출력한다.

```text
APOLLO_SI1_TIMER cntfrq=125000000 configured=125000000 status=PASS
```

Zephyr tickless 설정과 100 ticks/s는 유지한다. Clock의 하드웨어 주파수와
논리 tick 설정은 다른 항목이다. FVP board의 주파수 설정은 변경하지 않았다.

## 빌드 및 실행

현재 `build/conf/local.conf`의 machine 기본값은 FVP라 모든 명령에 QVP를 명시한다.
공유 build directory에서 BitBake를 동시에 실행하지 않는다.

```bash
./yocto_build.sh --machine apollo-qvp qbox-apollo-qvp-native -c compile
./yocto_build.sh --machine apollo-qvp zephyr-demos-cl1 -c compile
```

테스트 override 파일 `build/timer-implementation/timer-test.conf`의 내용:

```bitbake
APOLLO_TFM_TIMER_TEST = "ON"
```

```bash
source layers/poky/oe-init-build-env build
MACHINE=apollo-qvp bitbake -R "$PWD/timer-implementation/timer-test.conf" nexios-bsp-initramfs
```

workspace root에서 실행:

```bash
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state --record-initial-state \
  --out-dir build/timer-implementation/runtime --timeout 600 --exit-after-pass -- \
  --timer-probe --timer-snapshot-time-ns 10000000000 \
  --timer-snapshot-interval-ns 1000000000
python3 scripts/test/validate_tfm_timer_stages.py \
  --rse-log build/timer-implementation/runtime/qbox-rse.log \
  --output build/timer-implementation/runtime/timer-stages.json
```

`timer-stages.json`뿐 아니라 runner의 `result.json`, SI1 주파수 marker와
`NEXIOS_BSP_INITRAMFS_READY`를 함께 확인한다.

## 실행 결과

최종 테스트용 BSP 빌드는 5,775개 task 중 5,761개를 재사용하고 성공했다.
`bsp-final-build.log`에 기록되어 있다. Provider의 `do_check`는 platform 60/60
(5.39초), 선택된 core 60/60 (18.57초)을 통과했다.
원시 로그는 `build/timer-implementation/provider-check.log`다.

별도 `cortex_m55` standalone test도 1/1 PASS, 총 0.64초다.
Secure/NS LOAD bank 분리, secure COUNTFLAG, 실제 SysTick 예외와 WFI 해제를
관측했다. NS bank의 ISR 실행까지 검사한 것은 아니다.
정확한 실행 명령과 binary SHA-256은 `systick-unit/ctest.log`, `sha256.txt`에 있다.

QVP의 실제 부팅에서 다음 20개 firmware 검사가 모두 통과했다.

| Timer | BL1_1 | BL1_2 | BL2 | RUNTIME |
| --- | --- | --- | --- | --- |
| SysTick | PASS | PASS | PASS | PASS |
| TIMER0 | PASS | PASS | PASS | PASS |
| TIMER1 | PASS | PASS | PASS | PASS |
| TIMER2 | PASS | PASS | PASS | PASS |
| TIMER3 | PASS | PASS | PASS | PASS |

`runtime/timer-stages.json`: `passed=true`, `expected=20`, `observed=20`,
`errors=[]`. 각 셀의 start/end, spins, clock, pending 값은 JSON과 `qbox-rse.log`에 있다.
일부 검사는 첫 polling에서 이미 만료되어 `spins=0`이다. MMIO·co-simulation 지연이
설정한 10µs보다 길 수 있으므로 이 결과를 cycle-accurate latency로 해석하지 않는다.

같은 실행에서 SI1 UART가 실제 register를 읽어 다음을 출력했다.

```text
APOLLO_SI1_TIMER cntfrq=125000000 configured=125000000 status=PASS
```

`runtime/result.json`은 전체 부팅 PASS 및 strict timer snapshot PASS다.
`timer-snapshot.json`의 10초/11초 SI1 주파수도 각각 125MHz이며,
Linux는 `NEXIOS_BSP_INITRAMFS_READY machine=apollo-qvp`와 BSP shell에 도달했다.

테스트용 TF-M 네 ELF와 원본 ROM/flash/OTP/provisioning/AP flash는
`build/timer-implementation/test-firmware/`에 보존했다.
`test-firmware-manifest.sha256`과 runtime의 `initial-state.json`으로 입력을 확인한다.
이 파일들에는 테스트 빌드의 firmware가 들어 있으므로 일반 배포 이미지와 구분한다.

단계별 로그 판정기의 누락/중복/FAIL/counter/frequency/pending 음성 검사는
`python3 -m pytest -q tests/test_tfm_timer_stage_validation.py`로 2/2 PASS했다.

QVP snapshot의 주파수/IRQ/counter identity 계약도 기존
`qbox_contract_checks`와 `css_identity_checks`로 33/33 PASS를 확인했다.
결과는 `runtime/timer-contracts.json`이다.

마지막으로 `./yocto_build.sh --machine apollo-qvp --keep-conf --bsp`로
일반 빌드를 복원했다. 5,775개 task 중 5,696개를 재사용하고 성공했다.
`APOLLO_TIMER_TEST:BOOL=OFF`, 네 ELF에 self-test 심볼 없음,
`runtime-normal/qbox-rse.log`에 테스트 marker 없음도 확인했다.
`runtime-normal/result.json`은 부팅 및 strict timer snapshot PASS이며,
SI1의 실제 CNTFRQ/configured 값은 일반 빌드에서도 125MHz로 일치했다.
현재 deploy 디렉터리는 이 일반 빌드이고 테스트용 입력은 별도 보존본이다.
