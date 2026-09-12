# Apollo FVP/QVP timer 검증 결과

실행일: 2026-09-11. [하드웨어 구성](hardware.md), [소프트웨어 구성](software.md).
결과는 **기본 TF-M의 timer 미사용**, **RSE TIMER0~3 동작 PASS**,
**QVP SysTick register 검사 FAIL**이다. 전체 timer 구성을 일괄 PASS로 판정하지 않는다.

이 파일은 변경 전 결과를 보존한다. SysTick 추가와 SI CL1 주파수 정렬 이후의
결과는 [후속 구현·검증 문서](implementation-2026-09-12.md)에 기록한다.

## 환경과 증거 범위

현재 `build/conf`는 `apollo-fvp`, cfg2, AP CPU 4개,
`build/tmp_baremetal`이다. 각 machine의 기존 Yocto BSP 배포 이미지와 대응 ELF를
명시적으로 선택했다. 이번 조사에서 firmware/model을 수정하거나 새 firmware를
빌드하지 않았고, 배포된 이미지와 provider test binary를 사용했다.

| 소스 | 조사 시 revision |
| --- | --- |
| TF-M | `c4d3bf96349c392c18570dfd39c87c7a56a42bc5` |
| QBox | `2bd8c4c03272065e85c6b08e9ab88e387a1901d6` |
| QBox platform | `718186507a70c78d3d980cb2acf3ad0110b2b789` |
| QEMU | `a6bb3a5f651d554375e2433a2523476a6c41f5fa` |

증거 루트는 `build/timer-audit/`이다. Firmware ELF의 SHA-256과 생성 시각은
`software/artifacts.tsv`, 실행에 사용한 flash/WIC 등은 각 runtime의
`initial-state.json`에 기록되어 있다. 오래된 문서의 PASS 수치를 재사용하지 않았다.

## 결과표

| 검사 | FVP | QVP | 관측 범위 |
| --- | --- | --- | --- |
| 정상 TF-M timer 설정 | TIMER0~3 CTL/CVAL/CNTFRQ=0, NVIC timer IRQ disabled | 동일 | 소스/ELF와 실행 상태 일치 |
| SysTick 정상 상태 | CTRL/LOAD/VAL=0 | 읽기는 모두 0이나 장치 구현 없음 | QVP에서는 read=0만으로 정상 장치라고 판단 불가 |
| SysTick LOAD write/read | 999 → 999 PASS | 999 → 0 **FAIL** | enable하지 않은 register 존재/동작 검사; tick/ISR 검증 아님 |
| RSE TIMER0 IRQ3 | PASS | PASS | comparator expiry, ISTATUS, NVIC pending, clear |
| RSE TIMER1 IRQ4 | PASS | PASS | 동일 |
| RSE TIMER2 IRQ5 | PASS | PASS | 동일 |
| RSE TIMER3 IRQ27 | PASS | PASS | 동일 |
| RSE count 증가 | 약 125MHz PASS | 125,000,000 ticks/1s PASS | timer enable과 독립 |
| AP Linux clocksource | `arch_sys_counter`, 125MHz | 동일 | 커널 보고값과 timer interrupt 실측 |
| AP CPU0~3 timer IRQ | 네 코어 모두 증가 | 네 코어 모두 증가 | 아래 delta 표 참조 |
| QBox component/WFI tests | 해당 없음 | 7/7 PASS, 4.15초 | isolated testbench 결과 |
| SI CL0/CL1 timer 코드 | 최종 ELF 연결 확인 | 최종 ELF 연결 및 model snapshot 확인 | 각 SI timer ISR 횟수/주기 검증은 미완료 |

정상 FVP 검사 런 `fvp-runtime/result.json`은 모든 부팅 도메인 PASS,
runner 시간 190.277초다. 최종 probe 코드 재검증 런
`fvp-complete/result.json`도 PASS, 113.893초다.
이 시간에는 설정된 최소 실행 시간과 debugger 정지 시간이 포함된다.
부팅 성능 측정값으로 사용하면 안 된다.
QVP `qvp-runtime/result.json`, `qvp-snapshot/result.json`도 부팅 PASS다.

## RSE 레지스터 검사 방법

Iris와 RSE QEMU GDB로 기본 상태를 먼저 읽었다. FVP PC `0x10001f10`은
대응 ELF에서 `tfm_idle_thread`로 해석된다. QVP도 TF-M runtime 및 BSP ready 후
접속했다. NVIC `ISER0=0x600`으로 IRQ9/10만 enable되어 있었다.

그 다음 disposable 실행에서 TIMER0~3을 하나씩 설정했다.
NVIC의 해당 IRQ enable은 계속 0으로 유지했다.

1. 원래 CVAL/CTL을 저장하고, timer가 이미 사용 중이면 검사하지 않는다.
2. FVP는 TVAL=125,000 tick과 CTL=1을 설정하고 실행 시간을 진행시킨다.
   QVP는 정지한 RSE에서 CVAL=0인 이미 만료된 deadline과 CTL=1을 설정한다.
3. CTL=5 (`ENABLE|ISTATUS`)와 해당 NVIC pending bit를 확인한다.
4. Timer disable 후 NVIC ICPR로 pending을 지우고, 원래 CVAL/CTL을 복구한다.

두 방식은 **만료→NVIC pending 경로**를 검사한다. QVP GDB 검사는 지연 시간이나
counter 기반 scheduling을 측정하지 않으며, 그 부분은 snapshot/component test와
구분한다. 어느 방식도 TF-M timer ISR을 실행하지 않는다.

FVP에서 관측한 pending 값은 IRQ3/4/5/27 순서로
`0x100008/0x100010/0x100020/0x8100000`이다. 기존 IRQ20 pending
`0x100000`은 유지했다. QVP는 `0x8/0x10/0x20/0x8000000`에서 각각 0으로 해제됐다.

최종 파일:

- `fvp-rse-complete.json`: SysTick LOAD PASS, 네 timer IRQ PASS, counter 증가 PASS.
- `qvp-rse-gdb-complete.json`: 네 timer IRQ PASS, SysTick LOAD FAIL, 전체 `passed=false`.
- `fvp-rse-complete.log`, `qvp-rse-gdb-complete.log`: 원시 출력.

초기 Iris probe의 5초 run-control timeout과 register 이름 `PC` 오류는 각각
30초 timeout과 API `get_pc()` 사용으로 보완해 재검증했다.
첫 실패 JSON과 로그도 보존했다. 이를 firmware timer 장애로 분류하지 않는다.

## Count와 AP IRQ 측정

FVP 최종 RSE count는 `2,913,337,317 → 2,936,731,231`,
Iris simulation delta는 `0.1871513156s`였다.
계산 rate는 약 `124,999,997.6Hz`로 정수 tick 관측 오차 내 125MHz다.
`CNTFRQ=0`은 미설정 정보 레지스터이며 정지된 clock을 뜻하지 않는다.

QVP snapshot은 10초/11초의 SystemC 시점에서 RSE TIMER0~3 모두
`1,250,000,000 → 1,375,000,000`을 기록했다.
CSS/AP/SI view도 같은 count를 기록했다.
이 snapshot은 mirror `synchronize()`를 사용하므로 모든 CPU가 직접 수행한
`MRS CNTPCT`의 독립 실측으로 해석하지 않는다.
`qvp-snapshot/timer-snapshot.json`에는 각 view의 `counter_basis`가 기록되어 있다.

AP에서는 게스트의 `/proc/interrupts`를 `sleep 2` 전후에 읽었다.
두 플랫폼 모두 `GICv3 26 Level arch_timer`였다.

| 플랫폼 | CPU0 delta | CPU1 delta | CPU2 delta | CPU3 delta |
| --- | ---: | ---: | ---: | ---: |
| FVP | 534 | 534 | 540 | 539 |
| QVP | 564 | 567 | 563 | 568 |

근거는 `fvp-runtime/terminal_ns_uart0_5004.log`의 `TIMER_AP_BEFORE/AFTER`와
`qvp-ap-timer.log`다. Tickless 동작과 실행 workload가 있으므로 delta를 고정 주파수
정확도나 FVP/QVP latency 동등성으로 판정하지 않는다.

## QBox component 테스트

기존 Yocto provider build에서 다음을 실행했다.

```bash
ctest --test-dir build/tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0/build \
  -R '^(arm_system_counter-tests|host_gtimer-tests|host_gtimer-irq-tests|aarch64-managed-timer-wfi-(baseline|timer-wake)|apollo-fourcpu-(local-ppi|mmio-broadcast)-wake)$' \
  --output-on-failure --output-junit /build/arm/arm-auto-solutions/build/timer-audit/qvp-unit/ctest-junit.xml -V
```

| Test | 시간 |
| --- | ---: |
| `arm_system_counter-tests` (8 cases) | 0.018초 |
| `host_gtimer-tests` (17 cases) | 0.012초 |
| `host_gtimer-irq-tests` | 0.007초 |
| `aarch64-managed-timer-wfi-baseline` | 2.536초 |
| `aarch64-managed-timer-wfi-timer-wake` | 0.514초 |
| `apollo-fourcpu-local-ppi-wake` | 0.525초 |
| `apollo-fourcpu-mmio-broadcast-wake` | 0.515초 |

7/7 PASS, 총 4.15초. 로그와 JUnit은 `qvp-unit/`에 있다.
네 CPU의 local PPI wake와 MMIO frame0/SPI49의 target CPU2 wake를 포함한다.
이 provider CTest에는 RSE SysTick 검사가 없어 별도 register 검사를 수행했다.

## 재현 절차

FVP debug root launcher는 현재 `--machine apollo-fvp --debug`를 거부한다.
따라서 동일 프로젝트의 log runner에 Iris 옵션을 전달하는 경로를 사용했다.
아래 두 실행 명령은 별도 terminal에서 실행한다. 출력 디렉터리는 새 이름을 사용한다.

```bash
python3 scripts/setup/setup_local_debug_env.py --artifact-root build \
  --out-dir build/timer-audit/fvp-symbols --component tfm-s \
  --elf tfm-s=build/tmp_baremetal/work/apollo_fvp-poky-linux/trusted-firmware-m/2.2.2+git/build/bin/tfm_s.elf

python3 scripts/run/runfvp_log_boot.py --machine apollo-fvp \
  --fvpconf build/tmp_baremetal/deploy/images/apollo-fvp/nexios-bsp-initramfs-apollo-fvp.fvpconf \
  --out-dir build/timer-audit/fvp-complete --timeout 300 --min-runtime 110 \
  --require all --no-login -- --iris-server --iris-port 7121

python3 scripts/test/probe_rse_timers_iris.py \
  --manifest build/timer-audit/fvp-symbols/symbols.json --port 7121 \
  --boot-seconds 75 --output build/timer-audit/fvp-rse-complete.json
```

Iris endpoint 준비 후 probe를 실행한다. IRQ test를 끝낸 후 probe가 연결을 해제하고,
runner는 부팅 조건 및 최소 실행 시간을 확인한 뒤 종료한다.

QVP는 정상 BSP ready까지 실행한 후 RSE에 접속한다.

```bash
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state --record-initial-state --timeout 600 \
  --out-dir build/timer-audit/qvp-snapshot --keep-running-after-pass -- \
  --timer-probe --timer-snapshot-time-ns 10000000000 \
  --timer-snapshot-interval-ns 1000000000 \
  --platform-param platform.rse_cpu_pass.cpu_0.gdb_port=12340

RSE_TIMER_RESULT="$PWD/build/timer-audit/qvp-rse-gdb-complete.json" \
timeout 45 gdb-multiarch -q -nx -batch \
  build/tmp_baremetal/work/apollo_qvp-poky-linux/trusted-firmware-m/2.2.2+git/build/bin/tfm_s.elf \
  -ex 'set pagination off' -ex 'set remotetimeout 10' \
  -ex 'target remote 127.0.0.1:12340' \
  -ex 'source scripts/test/probe_rse_timers_gdb.py' -ex detach

python3 -c 'import json; assert json.load(open("build/timer-audit/qvp-rse-gdb-complete.json"))["passed"]'
```

마지막 assertion은 현재 SysTick 미구현으로 **실패하는 것이 관측 결과**다.
GDB가 script 오류 뒤 detach에 성공하면 exit code가 0일 수 있으므로 JSON 판정을
생략하지 않는다. keep-running 실행은 관측 후 해당 실행의 process만 종료한다.

## 미해결 항목

1. **QVP M55 SysTick 미구현**: LOAD write/read 실패와 소스가 일치한다.
   secure/NS SysTick device, CPU/reference clock, NVIC trigger 연결이 필요하다.
   이번 작업은 조사·문서·검증이며 모델 수정은 포함하지 않았다.
2. **SI CL1 주파수 계약 불일치 가능성**: Lua `cntfrq_hz=100MHz`, Zephyr
   `CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC=100MHz`인데 CSS mirror는 125MHz다.
   QEMU `arm_gt_counter_mirror_set()`는 mirror rate만 바꾸며 architectural
   CNTFRQ를 변경하지 않는다. Snapshot의 SI1 100MHz 필드는 hard-coded이므로
   실제 CNTFRQ read 증거가 아니다. 별도 GDB 검증 런 `qvp-si1/`은 RSE BL2의
   `SCP is not ready. Abort`에서 부팅 실패했고 GDB 접속도 timeout이었다.
   따라서 실제 SI1 register 값/timeout 오차는 이번에 확정하지 못했다.
   이 실패를 timer 결함으로 단정하지 않았으며 정상 QVP 2회 PASS와 구분한다.
3. **RSE test frequency**: TF-M 테스트의 32MHz 상수와 실제 125MHz 차이를 해결하기
   전에는 SLIH/FLIH의 1ms 주기를 신뢰할 수 없다.
4. **독립 RSE LSC, SOC_TIMER0/1, SLOWCLK, watchdog, reset/low-power,
   secure/NS 접근 정책 및 실제 TF-M ISR**은 이번 전체 시스템 동작 검증 범위 밖이다.
   FVP/QVP의 모든 timer 기능 동등성을 입증한 결과가 아니다.

추가한 두 Python probe는 `py_compile`을 통과했고 파일 whitespace도 확인했다.
