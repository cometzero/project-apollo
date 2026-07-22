# Apollo QVP timer 지연 원인과 subsystem 영향 분석

- 작성일: 2026-07-23
- 기준 top-level commit: `98d46764e570`
- 기준 QBox commit: `2dbbdff91f36`
- 기준 QBox Platform commit: `14b73e8e9558`
- 기준 QEMU commit: `99f3ef09d751`
- 대상: Apollo QVP의 AP, SMD, Safety Island CL0/CL1, RSE timer/counter

## 1. 결론

AP Linux의 `sleep 3` 지연은 125 MHz라는 주파수 값이 잘못되어 생긴
고정 비율 오차가 아니다. AP CPU 내부 Arm Generic Timer의 counter와
clockevent deadline을 SystemC의 공유 CSS counter provider에 연결하면서,
CPU의 빈번한 deadline 처리 경로가 QEMU와 SystemC 사이의 시간 변환 및
동기화 경계를 통과하게 된 것이 원인이다.

원래 timer feature에서는 반복 3초 sleep의 guest monotonic 경과 시간이
평균 3.938초, 최대 5.450초였다. AP CPU만 QEMU native Generic Timer로
되돌린 진단 빌드는 평균 3.113초였고, 최종 Yocto 빌드는 평균 3.106초였다.
두 구성 모두 Linux가 `arch_sys_counter`를 선택했고 125 MHz를 보고했으므로,
큰 편차가 있는 지연은 counter 주파수 배수 오차가 아니라 clockevent의
늦은 전달 또는 늦은 servicing으로 판단한다.

현재 해결 방법은 다음과 같다.

1. AP 각 Cortex-A720AE CPU의 내부 Generic Timer는 QEMU native counter와
   QEMU `QEMU_CLOCK_VIRTUAL` 기반 deadline을 사용한다.
2. AP CPU의 PPI timer는 기존처럼 각 CPU의 GIC PPI에 직접 연결한다.
3. CSS 공유 `arm_system_counter`와 bridge는 제거하지 않았다. AP의 platform
   REFCLK MMIO timer frame만 이 provider를 계속 사용한다.

이 방법은 Linux의 주 clocksource/clockevent 경로를 안정화하면서 AP MMIO
REFCLK 구현을 유지한다. 다만 AP CPU counter와 CSS MMIO counter가 하나의
mutable provider state를 비트 단위로 공유한다는 성질은 사라졌다. 두 경로는
현재 모두 125 MHz이고 co-simulation의 각 virtual time에 따라 진행하지만,
CSS counter를 정지하거나 다시 쓰거나 increment를 변경하면 서로 달라질 수
있다.

나머지 subsystem을 동일하게 볼 수는 없다.

| 영역 | 현재 주 시간 경로 | AP와 같은 지연 위험 | 별도 확인 사항 | 판정 |
| --- | --- | --- | --- | --- |
| AP CPU | QEMU native Generic Timer/PPI | 해결됨 | CSS counter mutation 시 MMIO와 불일치 | 낮음 |
| AP REFCLK MMIO | CSS provider -> bridge -> QEMU MMIO timer/SPI | 조건부 존재 | CVAL-to-SPI 48/49 latency 미측정 | 중간 |
| SI0 CPU 내부 timer | CSS provider -> bridge -> R82 PPI | 존재 가능 | visible 125 MHz, reported 1 GHz; 주 time driver는 MMIO | 중간 |
| SI0 MMIO gtimer | `host_gtimer` counter frame | AP형 지연 이전에 기능 누락 | comparator, expiry event, IRQ 34가 없음 | 높음 |
| SI1 Zephyr timer | CSS 125 MHz provider -> bridge -> R82 virtual timer/PPI | 존재 | Zephyr 및 CNTFRQ는 100 MHz이므로 25% 빠른 tick 가능 | 높음 |
| SMD counter frame | CSS provider를 직접 읽고 제어 | clockevent가 없어 직접 해당 안 됨 | multi-chip sync는 register 수준 모델 | 낮음/중간 |
| RSE TIMER0..3 | 한 RSE-local SSE counter/timer, QEMU 내부 | 직접 해당 안 됨 | TF-M 32 MHz와 QBox input 125 MHz 계약 불일치 | 중간 |

따라서 AP fix를 모든 CPU에 기계적으로 적용해서는 안 된다. CPU 내부 Generic
Timer는 QEMU `ARMCPU`가 소유해야 한다는 구조를 유지하되, SI0는 먼저 MMIO
timer frame과 IRQ를 완성하고, SI1은 100/125 MHz 계약을 정리한 뒤 동일한
latency A/B를 수행해야 한다.

## 2. 분석 범위와 신뢰도

이 문서에서는 다음 용어를 구분한다.

- **reference clock**: counter를 진행시키는 입력 clock이다.
- **counter**: 시간에 따라 증가하는 값이다. 그 자체로 interrupt를 만들지
  않는다.
- **timer**: counter와 compare value를 비교해 deadline 상태와 interrupt를
  만든다.
- **clocksource**: OS가 현재 시간을 읽는 경로이다.
- **clockevent**: OS가 미래 시점에 interrupt를 요청하는 경로이다.
- **guest monotonic time**: guest가 읽는 단조 증가 시간이다. host wall-clock과
  simulation time은 서로 다른 값이다.

판정 신뢰도는 다음처럼 사용한다.

- **확인**: 현재 소스, 저장된 실행 로그 또는 A/B 결과로 직접 확인했다.
- **강한 추론**: counter rate와 firmware 변환식처럼 소스의 수치 관계로
  결과를 계산할 수 있지만 전용 runtime 측정은 아직 없다.
- **가능성**: 구조가 AP 실패 경로와 같으나 해당 subsystem에서 deadline
  latency를 직접 측정하지 않았다.

이번 분석은 저장된 AP A/B runtime 결과를 재검토하고 현재 소스를 정적으로
추적했다. SI0, SI1, RSE 각각의 반복 delay/IRQ latency runtime 실험은 아직
없으므로 해당 부분을 AP 측정 결과처럼 확정해서 표현하지 않는다.

## 3. Arm Zena CSS가 요구하는 큰 구조

Arm Zena CSS programmer's model은 CPU 내부 Generic Timer와 platform MMIO
timer를 구분한다.

- AP에는 REFCLK Generic Timer control frame과 secure/non-secure base frame이
  있다.
- SMD에는 CSS REFCLK counter의 control, read, multi-chip synchronization
  frame이 있다.
- SI0에는 SYSCLK counter control과 CL0 timer base frame이 있다.
- RSE에는 CSS counter와 별개인 Local System Counter가 있고, 이 counter가
  TIMER0..3의 `CNTVALUEB` 입력을 공급한다.

관련 hardware 근거는 다음 위치에 있다.

- AP REFCLK frame: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
  의 AP memory map, `0x1A810000`-`0x1A830000`
- CSS REFCLK control/read/sync: 같은 문서의 CSS control map,
  `0x02_0000_D010_0000`-`0x02_0000_D012_FFFF`
- SI0 SYSCLK frame: 같은 문서의 Safety Island map,
  `0x2A6F0000` 및 `0x2A720000`
- RSE timer/LSC: 같은 문서의 9.4.3 및 9.4.9 절

중요한 원칙은 다음과 같다.

```text
CPU 내부 Generic Timer                  Platform MMIO Generic Timer
----------------------                 ---------------------------
CNTVCT/CNTPCT system register          CNTBase/CNTControl MMIO register
CNTV_CVAL/CNTP_CVAL                    MMIO CVAL/TVAL/CTL
per-core PPI interrupt                 platform SPI 또는 subsystem IRQ
QEMU ARMCPU가 소유                     QEMU device 또는 SystemC model이 소유
```

Platform MMIO timer를 추가했다고 CPU 내부 PPI timer를 대체하는 것은 아니다.
반대로 CPU 내부 timer를 native QEMU로 운용한다고 AP REFCLK MMIO frame을
삭제해서도 안 된다.

## 4. 현재 QBox timer/counter 전체 구조

### 4.1 최상위 시간축과 instance 경계

현재 Apollo full-system은 AP, SI0, SI1, RSE를 각각 다른 `QemuInstance`로
실행한다. CSS 공유 counter는 SystemC 쪽에 하나만 존재한다. 각 external
consumer bridge는 자기 QEMU instance의 virtual time과 SystemC absolute
time 사이 epoch offset을 보관한다.

```text
                           SystemC simulation time
                                    |
                                    v
                 +--------------------------------------+
                 | css_system_counter                   |
                 | type: arm_system_counter             |
                 | input clock       : 125 MHz          |
                 | integer increment : 1                |
                 | reported frequency: 125 MHz          |
                 | mutable: enable/count/scale/frequency|
                 +------------------+-------------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
          v                         v                         v
  +---------------+        +----------------+        +----------------+
  | SMD MMIO view |        | SI0 consumers  |        | SI1 consumers  |
  | control/read  |        | bridge + MMIO  |        | CPU bridge     |
  | sync registers|        | counter frames |        |                |
  +---------------+        +----------------+        +----------------+
          |
          +-------------------------> AP MMIO bridge

  Separate QEMU virtual-time domains
  ==================================

  AP QemuInstance       SI0 QemuInstance      SI1 QemuInstance
  ----------------      ----------------      ----------------
  native AP CPU timer   external R82 timer    external R82 timer
  external MMIO timer   via CSS bridge        via CSS bridge

  RSE QemuInstance
  ----------------
  QEMU clock source -> one SSE Local System Counter -> SSE TIMER0..3
  (CSS arm_system_counter bridge를 사용하지 않음)
```

`arm_system_counter`는 매 tick마다 event를 발생시키는 clock object가 아니다.
주어진 SystemC absolute time에 대해 fixed-point 연산으로 count를 계산한다.
control, count, increment 등이 변경될 때만 observer generation을 갱신한다.

### 4.2 AP의 현재 구조

```text
                        AP QemuInstance
                QEMU_CLOCK_VIRTUAL, 125 MHz contract
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
  +----------------------+           +--------------------------+
  | Cortex-A720AE CPU x4 |           | AP REFCLK MMIO device    |
  | QEMU native counter  |           | arm_arch_timer_mmio      |
  | QEMU native deadline |           | external counter mode    |
  +----------+-----------+           +-------------+------------+
             |                                       ^
   per-core Generic Timer PPI                         |
             |                              ap_timer_counter_bridge
             v                                       ^
      +-------------+                                |
      | GIC-720 PPI |                  +-------------+-------------+
      +-------------+                  | css_system_counter 125 MHz|
                                       +-------------+-------------+
                                                     |
                              +----------------------+------------------+
                              |                                         |
                              v                                         v
                      frame 0, non-secure                       frame 1, secure
                      AP_SYS_CNT_BASE_NS                        AP_SYS_CNT_BASE_S
                      SPI 49                                    SPI 48
```

AP CPU는 `cpu_arm_cortexA720AE`이며 external provider argument가 없다.
`cntfrq_hz = 125000000`이고, Linux가 사용하는 CPU Generic Timer interrupt는
각 CPU의 PPI로 연결된다. 반면 `ap_timer_counter_bridge`는 여전히 존재하며
`qemu_arm_arch_timer_mmio_external_counter`에만 전달된다.

### 4.3 SI0와 SMD의 현재 구조

```text
                 css_system_counter, 125 MHz
                            |
          +-----------------+-------------------+
          |                 |                   |
          v                 v                   v
  SMD CNTControl       SMD CNTRead         SMD Sync frame
  host_gtimer          host_gtimer         host_gtimer
  active counter       read-only view      register-level model
  state control

                            |
          +-----------------+-------------------+
          |                                     |
          v                                     v
  si_cl0_timer_counter_bridge          SI0 host_gtimer frames
          |                            - CNTCTL at 0x2A6F0000
          v                            - CNTBase at 0x2A720000
  Cortex-R82 CPU internal timer        - PCTL/PCTH/FRQ are dynamic
  external counter/PPI                 - CVAL/CTL are passive registers
                                       - expiry scheduler 없음
                                       - IRQ output/IRQ 34 wiring 없음

  SCP-firmware intended alarm path
  ===============================

  fwk_time / mod_timer
          |
          v
  mod_gtimer::set_timer(timestamp)
          |
          +--> write P_CVALL/P_CVALH at 0x2A720000
          |
          X--> compare against shared counter      (현재 구현 없음)
          X--> assert CL0_SYSTEM_TIMER_IRQ 34      (현재 구현 없음)
```

SMD control/read frame과 SI0 counter frame은 모두 같은 `css_system_counter`
객체를 참조한다. 따라서 동일 SystemC timestamp에서 읽은 count는 같아야 한다.

그러나 SI0 `host_gtimer`의 `counter_base=true` 구현은 PCTL, PCTH, FRQ만
동적으로 처리한다. 나머지 CVAL, TVAL, CTL offset은 byte array backing에
저장될 뿐 compare event를 예약하지 않는다. 클래스에 IRQ socket도 없다.
반면 SCP-firmware는 `mod_gtimer::set_timer()`에서 P_CVALL/P_CVALH를 쓰고
`CL0_SYSTEM_TIMER_IRQ = 34`를 alarm interrupt로 사용하도록 구성되어 있다.
또한 `address_map.lua`는 이 frame을 `access = "ro"`로 기록하지만 firmware의
CVAL write 요구와 맞지 않는다. 실제 router가 이 metadata로 write를 막지는
않더라도 coverage 계약도 함께 고쳐야 한다.

따라서 SI0에서 우선 해결해야 할 문제는 AP에서 본 수백 ms 단위 지연이 아니라
MMIO timer의 expiry/IRQ 기능 자체가 빠진 점이다. 현재 boot가 통과하는 것은
해당 boot 경로에서 alarm 동작이 충분히 행사되지 않았다는 의미일 수 있으며,
timer 기능 검증을 의미하지 않는다.

### 4.4 SI1의 현재 구조

```text
   css_system_counter
   actual visible rate: 125 MHz
             |
             v
   si_cl1_timer_counter_bridge
   SystemC time <-> SI1 QEMU virtual time
             |
             v
   Cortex-R82 external Generic Timer
   CNTFRQ property: 100 MHz
             |
             +--> CNTVCT_EL0: provider의 125 MHz count
             +--> CNTV_CVAL_EL0: Zephyr가 100 MHz 기준 deadline 기록
             +--> virtual timer PPI 27 -> SI1 GIC

   Zephyr 설정
   -----------
   CONFIG_ARM_ARCH_TIMER=y
   CONFIG_SYS_CLOCK_TICKS_PER_SEC=100
   CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC=100000000
   CONFIG_TIMER_READS_ITS_FREQUENCY_AT_RUNTIME=n
```

Zephyr driver는 한 tick을 `100,000,000 / 100 = 1,000,000` cycle로 계산한다.
External provider count가 실제로 125 MHz로 증가하므로 1,000,000 count는
8 ms에 도달한다. 의도한 10 ms보다 20% 짧고, Zephyr time은 simulation time보다
`125/100 = 1.25`배 빠르게 진행할 수 있다. 이는 source 수치로 확인되는 강한
추론이며, 전용 SI1 runtime 측정으로 확정해야 한다.

이 불일치는 QBox가 임의로 만든 값은 아니다. 저장된 FVP Iris 측정도 SI1
`CNTFRQ_EL0=100 MHz`와 CSS와 같은 125 MHz visible count를 동시에 보였다.
따라서 현재 QBox는 FVP의 observed register/count contract를 재현하지만,
Zephyr의 timeout 계산 관점에서는 FVP와 QBox 양쪽에 공통된 software/model
consistency gap일 수 있다.

또한 CPU internal deadline이 external provider bridge를 통과하므로 AP에서
확인된 variable late delivery 가능성도 남아 있다. 주파수 불일치에 의한
결정적 fast drift와 scheduler/IRQ 지연에 의한 variable late wakeup이 서로
상쇄되어 겉보기 결과가 정상처럼 보일 수도 있으므로, 단일 boot timestamp만
비교해서는 안 된다.

### 4.5 RSE의 현재 구조

RSE는 CSS 공유 provider가 아니라 RSE QemuInstance 내부의 Local System
Counter를 구현한다. 이 분리는 Zena CSS hardware 구조와 맞는다.

```text
                  RSE QemuInstance / QEMU_CLOCK_VIRTUAL
                                  |
                       qemu_clock_source
                       input: 125 MHz (default)
                                  |
                                  v
                     +--------------------------+
                     | QEMU sse-counter        |
                     | one Local System Counter|
                     +------------+-------------+
                                  |
              same counter state / CNTVALUEB input
          +-----------+-----------+-----------+-----------+
          |           |                       |           |
          v           v                       v           v
      SSE TIMER0  SSE TIMER1              SSE TIMER2  SSE TIMER3
      0x58000000  0x58001000              0x58002000  0x58003000
      IRQ 3       IRQ 4                   IRQ 5       IRQ 27
          |           |                       |           |
          +-----------+-----------> RSE NVIC <-----------+

  reset domain:
  TIMER0..2 -> nWARMRESETSYS_RSS
  LSC/TIMER3 -> nWARMRESETAON
```

`sse-counter`의 현재 count와 `sse-timer` deadline은 모두 같은
`QEMU_CLOCK_VIRTUAL`에서 계산되고, timer expiry도 QEMU `timer_mod_ns()`로
예약된다. SystemC counter callback이나 AP/SI bridge를 통과하지 않으므로,
AP에서 확인된 교차 도메인 deadline 지연이 RSE에 그대로 발생할 가능성은
낮다.

다만 별도의 주파수 계약 문제가 있다.

- QBox `QBOX_APOLLO_RSE_LSC_INPUT_HZ` 기본값은 125 MHz이다.
- TF-M RSE `SYSTIMER0_ARMV8M_DEFAULT_FREQ_HZ`는 32 MHz이다.
- TF-M timer test는 1 ms auto-increment를 `32,000` count로 계산한다.
- QEMU SSE timer의 CNTFRQ register write는 metadata를 바꾸지만 underlying
  counter input clock을 바꾸지 않는다.

따라서 해당 TF-M timer path가 실행되면 32,000 count는 125 MHz에서
0.256 ms에 도달한다. 이것은 AP의 variable delay와 다른, 최대 3.90625배의
fast-rate 문제이다. 현재 production boot에서 이 TF-M test timer가 항상
활성화된다고 단정할 수는 없으므로, 활성 구성과 실제 IRQ 주기를 확인해야
한다.

## 5. AP delay의 원인 분석

### 5.1 문제가 있던 경로

원래 feature는 AP CPU도 external counter wrapper로 만들었다.

```text
  Linux nanosleep(3 s)
          |
          v
  hrtimer/clockevent가 CNTV_CVAL 또는 CNTP_CVAL 기록
          |
          v
  ARMCPU Generic Timer
          |
          v
  ArmGenericTimerCounter provider API
    - count_at_ns(qemu_virtual_ns)
    - deadline_ns(target_count, from_qemu_ns)
          |
          v
  QBox qemu_arm_generic_timer_counter_bridge
    - QEMU virtual ns + epoch offset -> SystemC absolute ns
    - css_system_counter mutex/state 조회
    - target count -> SystemC deadline 계산
    - SystemC absolute ns - epoch offset -> QEMU deadline ns
          |
          v
  QEMU timer_mod_ns(QEMU_CLOCK_VIRTUAL, deadline)
          |
          v
  QEMU timer callback -> PPI -> GIC -> guest timer ISR
          |
          v
  sleeping task wakeup
```

이 구조에서는 Linux의 모든 CPU clockevent가 QEMU 내부의 닫힌 timer 경로가
아니라 SystemC counter provider와의 경계를 통과한다. AP QemuInstance는
`multithread-freerunning`이고, provider는 mutex로 상태를 보호하며, 서로 다른
시간축은 epoch로 변환된다. Counter mutation이 발생하면 QBox observer가
QEMU iothread에 consumer 재계산 작업도 전달한다.

### 5.2 확인된 것과 아직 확인되지 않은 것

확인된 root-cause 경계는 다음과 같다.

- external AP CPU counter 구성에서만 큰 variable overshoot가 재현됐다.
- AP CPU를 native timer로만 바꾸자 같은 image와 firmware에서 지연이
  baseline 수준으로 돌아왔다.
- broken/fixed 모두 Linux clocksource와 CNTFRQ가 같았다.

따라서 **고빈도 CPU clockevent 경로를 SystemC external provider에 연결한
구조**가 원인이다.

하지만 저장된 증거만으로 다음 중 어느 한 항목을 유일한 미세 원인으로
지정할 수는 없다.

- provider callback 및 mutex 경합
- freerunning QEMU thread와 SystemC scheduler 사이의 rendezvous 지연
- QEMU timer callback의 실행 지연
- PPI/GIC 전달 또는 guest ISR servicing 지연

또한 정상적인 count 증가는 매 tick observer notification을 발생시키지
않는다. iothread notification은 provider의 count/control/scale mutation 시
deadline을 다시 계산하기 위한 것이므로, 일반 sleep 지연 전체를 이
notification 하나만의 문제라고 설명해서는 안 된다.

### 5.3 A/B 결과

저장된 결과는 `build/timer-ab/evidence/timer-ab-summary.md`에 있다.

| 구성 | 직접 `time sleep 3` | 반복 측정 평균 | 최소 | 최대 |
| --- | ---: | ---: | ---: | ---: |
| timer 적용 전 Yocto | 3.033 s | 3.093 s | 3.090 s | 3.110 s |
| original timer feature Yocto | 3.160 s | 3.938 s | 3.280 s | 5.450 s |
| AP-native 진단 toggle | 3.173 s | 3.113 s | 3.100 s | 3.130 s |
| 최종 수정 Yocto | 3.068 s | 3.106 s | 3.090 s | 3.120 s |
| 최종 수정 local Buildroot | 3.020 s | 3.068 s | 3.060 s | 3.080 s |

반복 측정은 `/proc/uptime` 전후의 차이이며 두 번의 `cut` 실행과 UART polling
overhead가 포함된다. 따라서 직접 shell `time` 값이 요청한 3초 sleep에 가장
가깝고, 반복 값은 편차와 regression을 비교하는 용도로 봐야 한다.

## 6. 현재 fix의 의미와 한계

현재 QBox Platform의 `ap_compute.lua`는 AP CPU에 external bridge를 전달하지
않는다. Native QEMU 경로는 다음과 같이 단순하다.

```text
  guest CVAL write
       |
       v
  ARMCPU gt_timer[]
       |
       +--> count = QEMU virtual time * 125 MHz
       +--> QEMUTimer deadline, 같은 QEMU virtual clock
       |
       v
  per-core PPI -> GIC -> guest ISR
```

이 변경은 AP의 CPU internal timer ownership을 QEMU `ARMCPU`에 되돌린
최소 변경이다. QEMU와 QBox의 generic provider 기능을 삭제하거나 Apollo
전용 workaround를 QEMU core에 추가하지 않았다.

남은 fidelity trade-off는 다음과 같다.

1. AP CPU와 AP MMIO REFCLK가 더 이상 동일 provider state를 공유하지 않는다.
2. 평상시 nominal rate는 둘 다 125 MHz이지만 QEMU virtual time과 SystemC
   time 및 counter state가 다르므로 exact equality는 보장되지 않는다.
3. SMD가 CSS counter를 stop/rebase/rescale하면 AP MMIO는 따라가지만 AP CPU
   native counter는 따라가지 않는다.
4. AP MMIO timer 자체의 deadline/SPI latency는 이번 Linux `sleep` A/B에서
   검증되지 않았다.

그리고 기존 timer snapshot 도구에는 regression이 있다.
`apollo_timer_snapshot_capture.cc`는 AP CPU가 external bridge를 가진다고
가정하고 `m_ap_cpu.timer_counter_bridge()`를 무조건 호출한다. 현재 native AP
CPU에서는 이 호출이 예외를 발생시키므로 `QBOX_APOLLO_TIMER_SNAPSHOT=1`은
현재 wiring과 호환되지 않는다. 과거 snapshot artifact는 feature 당시의
공유 상태 증거이지, 현재 native AP 구성의 runtime 검증 증거가 아니다.

## 7. Subsystem별 상세 위험 분석

### 7.1 AP REFCLK MMIO

AP MMIO timer는 external CSS provider를 사용하고 CVAL expiry를 QEMU timer로
예약한다. 따라서 이 device를 실제 OS clockevent로 선택하면 AP CPU에서 본
교차 경계 latency가 나타날 가능성이 있다. 현재 Linux `sleep`은 CPU
`arch_sys_counter`/PPI 경로를 사용했기 때문에 이 위험을 행사하지 않았다.

필요한 검증은 frame 0/1에 CVAL을 설정한 뒤 expected provider deadline과
SPI 49/48 assertion 시각의 차이를 여러 부하 조건에서 측정하는 것이다.

### 7.2 SI0

SI0 CPU internal timer는 AP의 과거 경로와 같은 external provider 구조여서
그 timer를 사용하는 firmware에는 같은 종류의 지연 가능성이 있다. 또한
현재 QBox의 visible provider count는 125 MHz인데 CPU reported CNTFRQ는 1 GHz로
관찰됐다. FVP의 SI0 reported CNTFRQ는 0이었다. 그러나 현재 SCP-firmware의
Framework time driver는 CPU system register timer가 아니라 `0x2A720000`
MMIO frame을 사용하므로 이 CPU metadata mismatch는 주 alarm path가 아니다.

그러므로 우선순위는 다음과 같다.

1. QBox Platform의 `host_gtimer` counter-base frame에 physical compare,
   enable/mask/status, expiry event를 구현한다.
2. expiry를 SI0 GIC의 IRQ 34로 연결한다.
3. SCP `mod_timer` alarm을 이용해 1 ms, 10 ms, 1 s 구간을 반복 검증한다.
4. 그 뒤 CPU internal timer에도 AP와 같은 native/external A/B를 수행한다.

SI0 control frame에 대한 SCP의 implementation-defined write는 AArch64의
`uintptr_t` 폭 때문에 64-bit write가 된다. 현재 `host_gtimer`는 이 wide
write를 write-ignore로 처리하므로 `SYSCNT_INCR=8` 주석과 달리 visible
counter는 125 MHz로 유지된다. SCP의 `.frequency`도 125 MHz이므로 현재
Framework 시간 변환은 이 동작과 일치한다. 이 부분을 1 GHz로 바꾸려면
counter rate, FRQ, firmware conversion을 함께 바꿔야 한다.

### 7.3 SI1

SI1은 가장 먼저 전용 runtime 측정을 해야 한다. 현재 구성만 보면 다음 두
문제가 동시에 존재할 수 있다.

- CSS 125 MHz count와 Zephyr 100 MHz cycle 계산의 고정 비율 불일치
- external CPU counter deadline 경로의 variable late delivery

단순히 AP와 같이 native 100 MHz timer로 바꾸면 지연 경계와 Zephyr rate
오차는 제거되지만, FVP에서 확인한 125 MHz shared physical count topology를
깨뜨린다. 반대로 현재 값을 그대로 두면 FVP register/count fidelity는
유지하지만 Zephyr의 100 MHz timeout 계산은 불일치한다.

따라서 먼저 FVP와 QBox에서 같은 Zephyr delay/tick test를 수행해 실제 영향이
양쪽에 공통으로 나타나는지 확정한다. 그 후 다음 중 하나를 명시적으로
선택해야 한다.

- hardware/shared-count fidelity 우선: CSS 125 MHz count를 유지하고 Zephyr의
  cycle-frequency 계약을 125 MHz로 맞춘다.
- 현재 FVP software-visible behavior 우선: 125 MHz count와 100 MHz metadata를
  유지하고 known consistency gap으로 관리한다.
- software time 정확도 우선: SI1 CPU를 native 100 MHz로 분리하되 FVP shared
  count와 달라지는 expected deviation을 기록한다.

어느 경우든 CPU 내부 PPI timer를 platform MMIO timer로 대체해서는 안 된다.

### 7.4 SMD와 multi-chip synchronization

SMD control/read frame은 active CSS counter state를 제공하므로 단순 count
polling에는 AP형 clockevent 지연이 직접 적용되지 않는다. 다만 control write가
external consumers의 deadline을 변경할 수 있고, 이 재계산은 QEMU instance
별 iothread와 rendezvous해야 한다.

현재 sync frame은 ID 및 register access 중심 모델이다. Hardware guide가
설명하는 request-acknowledge, threshold, network-delay, timeout 및 interrupt
동작을 모두 구현한 것은 아니다. 단일-chip boot에는 낮은 위험이지만,
multi-chip time synchronization을 검증할 때는 명시적인 fidelity gap이다.

### 7.5 RSE

RSE SSE counter/timer는 한 QEMU instance 안에서 닫혀 있어 구조적으로 가장
안정적이다. 네 timer가 한 counter를 공유하고 각자 CVAL/IRQ만 소유하는 것도
hardware의 `CNTVALUEB` fan-out 구조와 맞는다.

우선 확인할 것은 scheduler latency가 아니라 input clock 계약이다. TF-M에서
timer test/IRQ 기능을 켠 build로 다음을 비교해야 한다.

- LSC input frequency
- TIMER0 CNTFRQ register
- 32,000-count auto-increment의 QEMU virtual-time 간격
- IRQ 3 assertion 및 TF-M handler 진입 간격

현재 FVP는 RSE Local System Counter window를 구현하지 않고 RSE timer view를
CSS counter에 alias하므로, FVP의 125 MHz 관찰값만으로 hardware LSC input을
결정할 수 없다. Ma1 또는 integration 자료가 32 MHz를 확정한다면 QBox default를
32 MHz로 맞추는 것이 단순하다. 125 MHz가 hardware 의도라면 TF-M default와
reload 계산을 125 MHz 계약으로 정리해야 한다. component source를 QBox 때문에
임의 수정하지 않고, 먼저 QBox Platform configuration을 authoritative hardware
값에 맞추는 것을 우선한다.

## 8. 권장 검증 순서

### P0: 현재 잘못된 기능 계약 확인

1. **SI0 MMIO alarm test**
   - PCTL/PCTH가 증가하는지 확인한다.
   - P_CVAL을 `now + 125000`으로 설정해 1 ms expiry를 요청한다.
   - P_CTL ISTATUS와 GIC IRQ 34를 각각 관찰한다.
   - 현재 구현에서는 count read만 통과하고 expiry/IRQ는 실패할 것으로
     예상한다.

2. **SI1 100/125 MHz test**
   - Zephyr에서 `CNTVCT_EL0`와 uptime을 1초 구간으로 기록한다.
   - simulation time 1초당 count delta와 tick delta를 기록한다.
   - 125,000,000 count 및 약 1.25초의 Zephyr logical time이 보이면 주파수
     mismatch를 확정할 수 있다.

3. **RSE TIMER0 rate test**
   - TF-M timer test를 활성화한다.
   - 1 ms 의도 IRQ의 QEMU virtual-time 간격을 측정한다.
   - 0.256 ms면 32/125 MHz mismatch가 확인된다.

### P1: AP fix의 잔여 경계 검증

1. AP MMIO NS/S frame의 CVAL-to-SPI latency distribution을 측정한다.
2. CSS counter enable, rebase, increment 변경 중 MMIO deadline 재계산을
   측정한다.
3. native AP CPU와 AP MMIO count drift를 normal boot와 mutation test로
   나눠 기록한다.
4. snapshot tool이 native AP CPU와 MMIO bridge를 별도로 관찰하도록 수정한다.

### 공통 측정 규칙

```text
요청한 delay
    |
    +--> counter delta        : rate 오류 검출
    +--> scheduled deadline   : conversion 오류 검출
    +--> IRQ asserted time    : timer model latency 검출
    +--> ISR entered time     : GIC/CPU servicing latency 검출
    +--> task wakeup time     : OS scheduler latency 포함 최종 결과
```

host wall-clock 한 값만으로 판정하지 말고, 같은 실행에서 simulation time,
QEMU virtual time, guest counter, IRQ assertion, guest ISR을 함께 기록해야 한다.
평균뿐 아니라 최소, 최대, percentile 및 sample 수를 남겨 variable latency와
fixed-rate drift를 분리한다.

## 9. 구현 책임 경계 제안

현재 코드 변경을 최소화하면서 fidelity를 높이려면 책임을 다음처럼 둔다.

| 책임 | 권장 위치 |
| --- | --- |
| ARMCPU Generic Timer, PPI, native QEMUTimer | QEMU |
| generic external counter provider ABI | QEMU |
| SystemC shared counter와 QEMU adapter | QBox core |
| Apollo 주파수, instance, memory map, IRQ wiring 정책 | QBox Platform |
| SI0 MMIO timer frame/comparator/IRQ 구현 | QBox Platform SystemC component |
| AP/SI/RSE 구성 선택 및 FVP compatibility | QBox Platform Lua |

특히 AP 해결을 QEMU core의 Apollo 조건문으로 옮기지 않는다. 현재처럼 native
CPU wrapper 선택은 QBox Platform 정책으로 유지하는 것이 upstream-friendly하고
다른 platform에 영향을 주지 않는다.

## 10. 근거 파일과 증거

주요 source 근거:

- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- `hsoc-stack/tools/qbox-platform/systemc-components/host_gtimer/`
- `hsoc-stack/tools/qbox/systemc-components/arm_system_counter/`
- `hsoc-stack/tools/qbox/qemu-components/timer/`
- `hsoc-stack/tools/qemu/hw/timer/arm_generic_timer_counter.c`
- `hsoc-stack/tools/qemu/hw/timer/arm_arch_timer_mmio.c`
- `hsoc-stack/tools/qemu/hw/timer/sse-counter.c`
- `hsoc-stack/tools/qemu/hw/timer/sse-timer.c`
- `hsoc-stack/tools/qemu/target/arm/helper.c`
- `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/`
- `hsoc-stack/components/system_mgmt/scp-firmware/module/gtimer/`
- `hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/timer/arm_arch_timer.c`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/`

저장된 validation 증거:

- `build/timer-ab/evidence/timer-ab-summary.md`
- `build/timer-ab/evidence/fixed-full-map-validation.json`
- `build/timer-ab/evidence/fixed-qbox-core-boundary.json`
- `build/qbox-apollo-qvp/timer-validation/20260722-085755/fvp/p0-decision-record.md`
- `build/qbox-apollo-qvp/timer-ab/baseline-20260723-001641/`
- `build/qbox-apollo-qvp/timer-ab/feature-20260723-002417/`
- `build/qbox-apollo-qvp/timer-ab/toggle-ap-native-20260723-003231/`
- `build/qbox-apollo-qvp/timer-ab/fixed-yocto-20260723-005315/`
- `build/qbox-apollo-qvp/timer-ab/fixed-local-20260723-005714/`

기존 `doc/qbox-fvp-timer-counter-comparison-ko.md`와
`doc/apollo-qvp-timer-counter-implementation-plan-ko.md`의 AP CPU shared-counter
설명 일부는 native AP fix 이전 topology를 기록한다. 현재 동작을 판단할 때는
본 문서와 현재 `ap_compute.lua` wiring을 우선해야 한다.
