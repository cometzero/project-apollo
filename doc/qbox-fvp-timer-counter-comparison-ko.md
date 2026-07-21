# Arm Zena CSS FVP 대비 QBox Timer, Counter 및 Reference Clock 분석

작성일: 2026-07-21

FVP 기준: `FVP_Zena_CSS_Cfg2`, Fast Models 11.31.25

QBox Platform 기준: `e202776ed4fe0b5502271fc06c545ef953d323f2`

QBox Core 기준: `9886434df730969e34f30ba0dd85b8869d0b7786`

QEMU 기준: `7d0cdacac296be62e3310b24546b660aabd65179`

## 1. 결론

현재 Apollo QBox의 address와 interrupt 배치는 AP MMIO Generic Timer를 중심으로
상당 부분 FVP와 맞지만, counter topology는 아직 FVP 및 Zena CSS 하드웨어와
다르다.

핵심 차이는 다음과 같다.

1. FVP에서는 AP, SI0 및 SI1 CPU가 같은 CSS System Counter state를 읽는다.
   AP MMIO frame도 하드웨어상 같은 counter를 사용해야 하지만 bare FVP에서는
   pre-boot PCT가 0이어서 정상 boot 확인이 남아 있다. 현재 QBox는 이 경로들을
   서로 다른 QEMU instance 또는 `host_gtimer` object로 구현한다.
2. 현재 QBox의 SMD, SI0 및 RSE `host_gtimer`는 simulation time으로 증가하지
   않는다. `PCTL` low-word를 읽을 때마다 기본값 4096를 더하는 read-side-effect
   stub이다.
3. 현재 AP CPU timer는 62.5MHz, AP MMIO timer는 125MHz, SI0 CPU timer는
   1GHz, SI1 CPU timer는 100MHz로 서로 다르다. FVP에서 관측한 공통 count의
   실효 증가율은 1GHz이다.
4. AP MMIO secure/non-secure frame 자체는 하나의 QEMU device 안에서 count를
   공유하고, frame별 compare/control/IRQ를 유지하므로 구조가 올바르다. 그러나
   AP CPU architectural timer와는 count source를 공유하지 않는다.
5. RSE Local System Counter의 control/read address만 서로 독립된
   `host_gtimer` object로 존재하고, `TIMER0`~`TIMER3` consumer는 구현되어 있지
   않다.
6. QBox의 목표 구조는 CPU timer를 platform MMIO timer로 대체하는 것이 아니다.
   CPU별 comparator/PPI는 QEMU `ARMCPU`에 유지하면서, count value provider만
   공통 CSS counter에 연결해야 한다.

현재 구조를 한 문장으로 정리하면 다음과 같다.

> QBox에는 하나의 reference counter가 배포되는 구조가 아니라, 서로 다른
> 주파수와 증가 규칙을 가진 여러 counter island가 존재한다.

FVP와 하드웨어 기준에 대한 상세 분석은
[`arm-zena-css-fvp-timer-counter-analysis-ko.md`](arm-zena-css-fvp-timer-counter-analysis-ko.md)를
참조한다.

## 2. 비교 기준

### 2.1 FVP에서 확인된 기준 동작

현재 FVP를 Iris로 측정한 결과는 다음과 같다.

- 물리 REFCLK: 125MHz
- SMD `CNTINCR`: 8
- visible count 증가율: 1GHz
- 같은 simulation timestamp에서 SMD, AP CPU, SI0 CPU, SI1 CPU 및 RSE
  `TIMER0`~`TIMER3`의 count가 동일
- AP MMIO secure/non-secure frame은 하드웨어상 같은 CSS count를 사용해야 하며
  IRQ는 각각 SPI 48, SPI 49이다. bare FVP pre-boot PCT는 0이어서 정상 boot
  count 연결은 추가 확인 대상이다.
- RSE Local System Counter address는 FVP에서 unmapped이며, RSE timer는 CSS
  공통 counter에 alias된 모델 단순화

### 2.2 하드웨어 목표 동작

Zena CSS 하드웨어 기준으로는 다음 두 count domain을 구분해야 한다.

1. CSS REFCLK System Counter: AP와 Safety Island에 공통 시간 축 제공
2. RSE Local System Counter: RSE `TIMER0`~`TIMER3`의 `CNTVALUEB` 제공

FVP의 RSE alias 동작은 하드웨어 목표가 아니라 필요할 경우에만 제공할 수 있는
FVP compatibility mode로 보아야 한다.

## 3. 현재 QBox topology

### 3.1 전체 그림

```text
Current Apollo QBox

  SMD QBox/SystemC
    host_gtimer CNTControl object  -- private m_counter, no time source
    host_gtimer CNTRead object     -- private m_counter, +4096 per PCTL read
    host_gtimer Sync object        -- register/ID stub only

  AP QEMU instance
    Cortex-A720AE CPU timers       -- QEMU virtual time, 62.5MHz
    Arm MMIO Generic Timer         -- QEMU virtual time, 125MHz
      +-- frame 0 NS, SPI 49
      +-- frame 1 S,  SPI 48

  SI0 QEMU/SystemC
    Cortex-R82 CPU timer           -- QEMU virtual time, 1GHz
    local CNTCTL host_gtimer       -- register storage only
    local CNTBase host_gtimer      -- private counter, +4096/read

  SI1 QEMU instance
    Cortex-R82 CPU timers          -- QEMU virtual time, 100MHz

  RSE QBox/SystemC
    LSC control host_gtimer        -- private object, default 125MHz field
    LSC read host_gtimer           -- private object, +4096/read
    TIMER0..3                      -- absent
```

각 QEMU counter가 모두 `QEMU_CLOCK_VIRTUAL`을 사용하더라도 서로 다른
`QemuInstance`와 서로 다른 frequency를 사용한다. 같은 simulation time에 같은
값을 반환한다는 보장은 없으며, 하나의 `CNTCV` state를 공유하는 구조도 아니다.

### 3.2 SMD CSS counter와 sync frame

`platforms/apollo/hw-block/system_mgmt.lua:407-438`은 하드웨어의 세 frame 주소에
각각 별도 `host_gtimer` object를 생성한다.

| Object | 주소 | 설정 | 실제 동작 |
| --- | --- | --- | --- |
| `host_css_counters_timers` | `0x20000_D010_0000` | `counter_control=true` | register storage와 `CNTFID0` reset value만 제공 |
| `host_css_counters_timers_read` | `0x20000_D011_0000` | `counter_read=true` | 자체 `m_counter`, `PCTL` read마다 4096 증가 |
| `host_css_counters_timers_sync` | `0x20000_D012_0000` | `sync_frame=true` | 일부 register 및 PID/CID 제공, 동기화 state machine 없음 |

`host_gtimer`는 object마다 `uint64_t m_counter`를 별도로 갖는다
(`host_gtimer.h:39-41`). `PCTL` read는 `next_counter_value()`를 호출해 count를
증가시키고, `PCTH`는 현재 high word만 반환한다(`:120-151`). 기본 increment는
4096이다(`:267-275`).

더 중요한 문제는 write가 `m_regs` byte array만 변경하고 `m_counter`를 변경하지
않는다는 점이다(`:211-222`). 따라서 다음 동작이 성립하지 않는다.

- control frame에서 enable/disable한 결과가 read frame에 반영
- control frame에서 `CNTCV`를 쓴 뒤 read frame에서 같은 값 관측
- REFCLK 또는 SystemC simulation time에 따른 연속 증가
- control/read frame 사이 하나의 coherent 64-bit counter 공유

SI0의 ATW5 translated view가 SMD physical frame으로 route되더라도, physical
control object와 read object 자체가 이미 서로 독립적이므로 공통 counter 문제는
해결되지 않는다.

### 3.3 AP CPU architectural timer

AP CPU는 `ap_compute.lua:587-625`에서 `cpu_arm_cortexA720AE`로 생성되며
`cntfrq_hz`를 지정하지 않는다. wrapper는 이 parameter가 기본값이 아닐 때만
QEMU의 `cntfrq` property를 설정한다
(`cortex-a720ae.h:107`, `:146-149`).

로컬 QEMU의 Cortex-A720AE 모델은 `aarch64_a710_initfn()`을 먼저 호출하고,
A710은 `ARM_FEATURE_BACKCOMPAT_CNTFRQ`를 설정한다
(`target/arm/tcg/cpu64.c:963-973`, `:1333-1363`). QEMU CPU realize 경로는
명시값이 없고 이 feature가 있으면 62.5MHz를 선택한다
(`target/arm/cpu.c:1718-1735`).

따라서 현재 AP CPU의 `CNTFRQ_EL0` 및 architectural timer count frequency는
**62.5MHz**이다. per-core physical, virtual, hypervisor, secure timer interrupt는
각각 GIC PPI로 올바르게 연결되어 있지만, 125MHz AP MMIO timer 및 FVP의 1GHz
공통 count와 시간 축이 맞지 않는다.

### 3.4 AP memory-mapped Generic Timer

`ap_compute.lua:453-474`은 local QEMU의 `qemu_arm_arch_timer_mmio`를 사용한다.

| 항목 | 현재 값 | FVP/하드웨어 기준 | 상태 |
| --- | ---: | ---: | --- |
| Control base | `0x1A810000` | `0x1A810000` | 일치 |
| Secure frame | `0x1A820000`, frame 1 | 동일 | 일치 |
| Non-secure frame | `0x1A830000`, frame 0 | 동일 | 일치 |
| Secure IRQ | SPI 48 | SPI 48 | 일치 |
| Non-secure IRQ | SPI 49 | SPI 49 | 일치 |
| `cntfrq` | 125MHz | CSS target 계약은 125MHz/1GHz 결정 필요, FVP normal-boot frame count 미측정 | 미확정 |

두 frame은 하나의 `ArmArchTimerMMIOState`에 속한다. QEMU source는
`QEMU_CLOCK_VIRTUAL * cntfrq`로 하나의 count를 계산하고 각 frame의 CVAL/control
상태와 IRQ를 별도로 유지한다(`hw/timer/arm_arch_timer_mmio.c:17-49`,
`:60-107`). 이 부분은 "공통 counter + 독립 frame comparator" 구조를 올바르게
구현한다.

다만 이 device의 counter 함수는 AP CPU의 `gt_get_countervalue()`와 별도이며,
각각 125MHz와 62.5MHz를 사용한다. 동일 AP QEMU instance 안에 있다는 사실만으로
두 count가 공유되지는 않는다. 이는 FVP 정상 boot 결과와 무관하게 Zena CSS의
공통 CSS count source라는 목표 구조에는 맞지 않는다.

### 3.5 Safety Island CL0

SI0에는 다음 세 가지 timer path가 서로 분리되어 있다.

1. Cortex-R82 architectural timer
2. `0x2A6F0000`의 `si_cl0_timer_cntctl`
3. `0x2A720000`의 `si_cl0_timer_cntbase`

`si_cl0_timer_cntctl`은 `host_gtimer` flag를 하나도 설정하지 않아 일반 register
storage처럼 동작한다. `si_cl0_timer_cntbase`는 `counter_base=true`,
`frequency=125000000`, `counter_increment=4096`으로 생성된다
(`si_cl0.lua:623-646`). 두 object는 state를 공유하지 않는다.

SI0 Cortex-R82 wrapper도 `cntfrq_hz`가 기본값일 때 QEMU property를 설정하지
않는다(`cortex-r82.h:63-67`, `:104-106`). local QEMU Cortex-R82 정의는 Generic
Timer feature를 설정하지만 `ARM_FEATURE_BACKCOMPAT_CNTFRQ`를 설정하지 않는다
(`target/arm/tcg/cpu64.c:1715-1805`). 따라서 QEMU의 새 CPU 기본값인 **1GHz**를
사용한다.

결과적으로 SI0 CPU count는 1GHz virtual-time 기반이지만, local timer frame은
125MHz를 register에 표시하면서 실제로는 low-word read마다 4096씩 증가한다.
둘은 같은 count source가 아니다.

하드웨어 guide의 외부 `REFCLK_SSYSCLK_CNTBase0` 주소 `0x01_7072_0000`은 현재
Apollo Lua에 직접 model object로 존재하지 않는다. SI0 local `0x2A720000` frame과
SMD translated view만 있다.

### 3.6 Safety Island CL1

CL1 Lua는 `ARCH_TIMER_FREQUENCY_HZ = 100000000`을 정의하고 모든 Cortex-R82
CPU에 `cntfrq_hz`를 명시한다(`si_cl1.lua:91-95`, `:299-327`). 따라서 CL1 CPU
timer는 **100MHz**이다.

CL1에는 platform REFCLK MMIO counter/frame model이 없다. CFG2 FVP에서 CL1
CPU `CNTPCT`가 SI0/AP와 같은 SMD count를 읽는 실측 결과와 다르다.

### 3.7 RSE

RSE Lua는 하드웨어의 Local System Counter 주소에 두 개의 `host_gtimer`를
배치한다.

| Object | 주소 | 동작 |
| --- | --- | --- |
| `rse_syscntr_cntrl_regs` | `0x5015A000` | 독립 control register object |
| `rse_syscntr_read_regs` | `0x5015B000` | 독립 read-side-effect counter object |

근거는 `rse.lua:433-453`이다. Apollo platform Lua 전체를 검색하면
`0x58000000`~`0x58003000` RSE `TIMER0`~`TIMER3` instance는 없다. 따라서 Local
System Counter의 consumer, compare register 및 IRQ 39~42도 존재하지 않는다.

현재 구조는 하드웨어의 별도 RSE local counter도 완성하지 못했고, FVP의 CSS
공통 counter alias도 재현하지 못한다.

두 object 모두 명시적인 frequency를 받지 않아 `host_gtimer` 기본값 125MHz를
register field에 사용한다. 반면 TF-M common RSE 설정은 system timer의 기본
frequency를 32MHz로 정의한다. 하드웨어 guide는 RSE Local System Counter의
입력 clock source/rate를 직접 명시하지 않으며, 현재 FVP는 CSS 1GHz count를
RSE timer에 alias한다. 따라서 QBox RSE에 적용할 실제 frequency는 이 세 값을
구분한 후 별도로 확정해야 한다.

## 4. 주파수 및 state 비교표

| View | FVP 현재 동작 | QBox 현재 동작 | 같은 state 공유 여부 |
| --- | --- | --- | --- |
| SMD counter | 125MHz REFCLK × 8 = 1GHz count | `host_gtimer`, +4096/PCTL read | 아니오 |
| AP CPU `CNTPCT` | SMD count와 동일 | 62.5MHz QEMU CPU count | 아니오 |
| AP MMIO S/NS | hardware상 SMD count 공유, bare FVP pre-boot PCT=0 | 125MHz, 두 frame끼리만 공유 | QBox 내부만 부분적, FVP normal-boot 비교 pending |
| SI0 CPU `CNTPCT` | SMD count와 동일 | 1GHz QEMU CPU count | 아니오 |
| SI0 CNTBase | SMD count와 동일 | 125MHz 표시, +4096/read | 아니오 |
| SI1 CPU `CNTPCT` | SMD count와 동일 | 100MHz QEMU CPU count | 아니오 |
| RSE LSC | FVP에서 미구현, TIMER0~3은 CSS 1GHz alias | 125MHz 표시, 독립 control/read stub, TF-M은 32MHz 가정 | 아니오 |
| RSE TIMER0~3 | FVP SMD count alias | timer instance 없음 | 미구현 |

## 5. Fidelity gap 평가

### 5.1 Critical: 공통 CSS counter 부재

AP, SI0, SI1, AP MMIO frame이 같은 timestamp에서 다른 값을 반환한다. timer
deadline, cross-domain timestamp, SCMI/FWU timeout 및 firmware time conversion이
FVP와 달라질 수 있다.

### 5.2 Critical: `host_gtimer`가 clock-driven counter가 아님

read 횟수가 시간이 되는 현재 구현은 polling 빈도에 따라 시간이 달라진다.
`PCTH-PCTL-PCTH` stable-read sequence도 low read 자체가 시간을 진행시키므로
실제 free-running counter 의미와 다르다.

### 5.3 High: CPU와 AP MMIO timer frequency 불일치

AP 안에서도 CPU 62.5MHz와 MMIO 125MHz가 다르며, SI0 1GHz와 SI1 100MHz도
일관되지 않다. DTS 또는 firmware가 기대하는 `CNTFRQ`와 count delta가 다를 수
있다.

### 5.4 High: RSE local timer path 미완성

RSE Local System Counter control/read coherence, `TIMER0`~`TIMER3` comparator,
IRQ, reset 및 PD_AON 동작이 없다.

### 5.5 Medium: cross-chip sync가 register stub

PID/CID와 일부 register access만 제공하며 request-acknowledge, threshold,
network delay 및 failure state가 없다. single-chip boot에는 당장 영향이 작을 수
있지만 multi-chip fidelity에는 필요하다.

### 5.6 Medium: SI external frame 누락

`REFCLK_SSYSCLK_CNTBase0`의 system-visible alias가 직접 구현되어 있지 않다.
debugger 또는 다른 requester가 이 view를 사용할 때 하드웨어 map과 달라진다.

## 6. 권장 QBox 목표 구조

### 6.1 기본 결정

QBox의 기본 구현은 FVP binary의 RSE 단순화를 그대로 복제하지 말고 Zena CSS
하드웨어 구조를 따른다.

```text
SystemC simulation time
        |
        +--> zena_css_ref_counter
        |      source_hz = 125MHz
        |      increment = 8
        |      count_hz  = 1GHz
        |      one coherent CNTCV state
        |          |
        |          +--> SMD control/read frames
        |          +--> AP CPU architectural timers
        |          +--> AP MMIO secure/non-secure frames
        |          +--> SI0 CPU and CNTBase views
        |          +--> SI1 CPU timers
        |
        +--> rse_local_system_counter
               source_hz = TBD (TF-M current default: 32MHz)
               independent CNTCV state
               |
               +--> RSE TIMER0
               +--> RSE TIMER1
               +--> RSE TIMER2
               +--> RSE TIMER3

cross-chip synchronization: separate control/state-machine block
```

FVP와 byte-for-byte timer behavior 비교가 필요한 경우에만 RSE `TIMER0`~`TIMER3`
source를 CSS counter로 바꾸는 명시적 `fvp_compat` mode를 추가할 수 있다. 기본
mode로 두면 안 된다.

### 6.2 공통 counter backend

재사용 가능한 SystemC counter component는 최소 다음 state를 가져야 한다.

- `base_count`
- `base_sc_time`
- physical `source_hz`
- per-source `increment` 또는 명시적인 `count_hz`
- enable 및 halt 상태
- frequency ID와 scaling 설정
- reset domain

read는 다음과 같이 simulation time에서 계산하며 side effect가 없어야 한다.

```text
count(now) = base_count + elapsed(now, base_sc_time) * count_hz
```

enable, frequency, scaling 또는 `CNTCV`가 바뀔 때 현재 count를 새 anchor로
고정하고 consumer에 deadline 재계산 notification을 보내야 한다.

### 6.3 QEMU CPU timer와 연결

CPU internal Generic Timer의 register, comparator, PPI 및 virtualization state는
QEMU `ARMCPU`에 남겨야 한다. `CNTPCT`를 MMIO timer로 대체하거나 PPI를 SPI로
우회하면 안 된다.

local QEMU의 `gt_get_countervalue()`와 deadline conversion에 opt-in external
counter-provider hook를 추가하고, Apollo CPU wrapper가 shared SystemC counter
service를 연결하는 방법을 권장한다. hook가 없는 다른 QEMU machine은 현재
`QEMU_CLOCK_VIRTUAL` 동작을 그대로 유지해야 upstream-friendly하다.

### 6.4 AP MMIO timer와 연결

현재 `arm_arch_timer_mmio`의 frame별 comparator/IRQ 구현은 유지하고 counter
계산 함수만 같은 external provider를 사용하게 한다. 그러면 다음을 동시에
보존할 수 있다.

- frame 0/1의 독립 CVAL/control/IRQ
- AP CPU와 MMIO frame의 동일 `CNTCV`
- SPI 49/48 wiring
- 기존 non-Apollo QEMU machine의 기본 동작

### 6.5 RSE timer 구현

local QEMU의 `sse-counter`와 `sse-timer`는 clock-driven count, scaling 및 consumer
notification 구조를 이미 제공한다
(`hw/timer/sse-counter.c:100-187`). 이를 Apollo RSE memory map과 reset/IRQ에
맞게 재사용하거나, 같은 pattern의 QBox SystemC component를 구현하는 것이
register-only stub보다 적절하다.

RSE Local System Counter는 CSS counter와 별도 state를 가져야 하며 다음을
구현해야 한다.

- control/read frame coherence
- `CNTVALUEB`를 TIMER0~3에 공급
- timer별 CVAL/control/IRQ 39~42
- TIMER3와 local counter의 PD_AON/reset 특성
- Secure/Non-secure alias 및 PPC access policy

### 6.6 주파수 계약 선결 조건

공통 backend 구현 전에 125MHz/1GHz 계약을 하나로 확정해야 한다. 현재
SCP-firmware는 125MHz REFCLK와 `CNTINCR=8`을 사용하지만 `.frequency`와 TF-A는
125MHz를 광고한다. FVP 실측 count는 1GHz이다.

권장 검증 순서는 다음과 같다.

1. 정상 FVP boot에서 SCP 초기화 직후 `CNTINCR`, `CNTFID0`, `CNTFRQ_EL0` 수집
2. 알려진 FVP simulation interval의 count delta 측정
3. firmware time conversion이 사용하는 frequency 확인
4. architecture owner와 visible count frequency 결정
5. QBox backend, CPU `cntfrq`, MMIO `cntfrq`, DTS/TF-A/SCP 값을 한 번에 정렬

RSE local domain은 CSS와 별도 결정 항목이다. TF-M의 32MHz 설정, Corstone Ma1
integration 자료, 실제 hardware clock 연결을 확인한 뒤 Local System Counter와
TIMER0~3에 동일한 값을 적용해야 한다. FVP의 1GHz alias는 hardware frequency
근거로 사용하지 않는다.

## 7. 구현 후 검증 계약

### 7.1 동일 timestamp invariant

같은 SystemC timestamp에서 다음 값이 같아야 한다.

```text
SMD.CNTCV
  == AP.CNTPCT_EL0
  == AP_MMIO_NS.CNTPCT
  == AP_MMIO_S.CNTPCT
  == SI0.CNTPCT_EL0
  == SI0_CNTBase.PCT
  == SI1.CNTPCT_EL0
```

RSE Local System Counter와 `TIMER0`~`TIMER3`의 `PCT`는 서로 같아야 하지만,
CSS `SMD.CNTCV`와 같을 필요는 없다.

### 7.2 필수 unit/integration test

- 주어진 simulation interval의 count delta와 configured frequency 일치
- 반복 read가 count를 임의로 진행시키지 않음
- 32-bit high-low-high read coherence
- control/read/alias frame에서 동일 count 관측
- enable/disable 및 `CNTCV` write 반영
- frame별 CVAL/TVAL 만료와 올바른 PPI/SPI/IRQ 발생
- AP MMIO frame 0/1이 count는 공유하고 compare state는 독립
- CSS counter write/reset이 RSE local counter를 변경하지 않음
- RSE TIMER3의 reset-domain 차이
- FVP compatibility mode가 명시된 경우에만 RSE timer가 CSS count를 사용

### 7.3 FVP differential test

FVP와 QBox에서 다음 snapshot을 같은 logical boot point에 수집한다.

```text
CNTFID0 / CNTFRQ
CNTINCR / scaling
SMD CNTCV
AP CNTPCT and MMIO PCT
SI0/CL1 CNTPCT
RSE Local Counter and TIMER0..3 PCT
timer CVAL, enable, mask, ISTATUS
interrupt assertion timestamp
```

FVP의 RSE local-counter 미구현은 expected model deviation으로 별도 표기하고,
하드웨어-correct QBox 결과를 실패로 판정하지 않도록 한다.

## 8. 권장 구현 순서

1. **P0 - frequency contract 확정**: FVP boot-time Iris 측정과 firmware 값 정렬
2. **P1 - shared CSS counter**: SMD control/read와 SI timer view를 하나의
   clock-driven backend로 교체
3. **P2 - QEMU 연결**: AP/SI CPU timer와 AP MMIO timer가 shared provider 사용
4. **P3 - RSE local domain**: Local System Counter와 TIMER0~3 구현
5. **P4 - sync 및 alias**: cross-chip sync state machine과 외부 SI frame 완성
6. **P5 - differential validation**: FVP/QBox count, deadline 및 interrupt 비교

각 단계에서 component source가 아니라 `hsoc-stack/tools/qbox`,
`hsoc-stack/tools/qbox-platform`, `hsoc-stack/tools/qemu` 경계 안에서 수정하는 것이
프로젝트의 ownership 원칙과 맞다.

## 9. 주요 source 근거

### QBox Platform/SystemC

- `hsoc-stack/tools/qbox-platform/systemc-components/host_gtimer/include/host_gtimer.h:20-40`,
  `:120-166`, `:168-222`, `:255-281`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua:407-438`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua:453-474`,
  `:587-625`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua:623-646`,
  `:1056-1097`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua:91-95`,
  `:299-327`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua:433-453`
- `hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_a720ae/include/cortex-a720ae.h:73-107`,
  `:146-149`
- `hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_r82/include/cortex-r82.h:40-67`,
  `:98-106`

### local QEMU

- `hsoc-stack/tools/qemu/target/arm/tcg/cpu64.c:963-973`, `:1333-1363`,
  `:1715-1805`
- `hsoc-stack/tools/qemu/target/arm/cpu.c:1718-1735`
- `hsoc-stack/tools/qemu/target/arm/helper.c:1348-1353`
- `hsoc-stack/tools/qemu/hw/timer/arm_arch_timer_mmio.c:17-49`, `:60-107`
- `hsoc-stack/tools/qemu/hw/timer/sse-counter.c:100-187`

### FVP 및 하드웨어 기준

- [`arm-zena-css-fvp-timer-counter-analysis-ko.md`](arm-zena-css-fvp-timer-counter-analysis-ko.md)
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:110-112`,
  `:293-295`, `:674-677`, `:700-703`, `:1227-1230`, `:1415-1416`,
  `:9295-9297`, `:14940-14948`, `:15014-15043`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/config/device_cfg.h:91-94`

## 10. 분석 범위와 한계

- QBox 결론은 current source topology를 직접 읽어 얻었다. 이번 작업에서는 QBox
  source를 변경하거나 full-system runtime을 실행하지 않았다.
- codebase-memory index는 관련 repository에서 `ready`였으나 일부 index coverage
  metadata를 제공하지 못했다. 모든 핵심 판정과 negative claim은 해당 source를
  직접 읽고 Apollo Lua 전체를 검색해 재확인했다.
- 여러 `QemuInstance`의 virtual clock이 SystemC scheduler와 동기화되는 방식은
  count state 공유를 뜻하지 않는다. 이 문서의 결론은 각 counter 함수, 주파수
  property 및 object state가 분리되어 있다는 source 사실에 기반한다.
- FVP AP MMIO frame의 normal-boot count identity는 미확정이다. bare pre-boot
  read가 0인 결과를 shared-counter 부정 증거로 사용하지 않았고, hardware
  topology를 QBox 목표로 사용했다.
- 125MHz/1GHz 중 최종 architecture-visible frequency는 아직 결정되지 않았다.
  이를 확정하기 전에는 숫자만 일괄 변경하지 말아야 한다.
