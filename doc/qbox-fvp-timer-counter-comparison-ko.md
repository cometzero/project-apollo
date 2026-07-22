# Arm Zena CSS FVP 대비 QBox Timer, Counter 및 Reference Clock 분석

작성일: 2026-07-21, 최종 갱신 2026-07-22

FVP 기준: `FVP_Zena_CSS_Cfg2`, Fast Models 11.31.25

QBox Platform 기준: `e202776ed4fe0b5502271fc06c545ef953d323f2` 기반 working tree

QBox Core 기준: `9886434df730969e34f30ba0dd85b8869d0b7786` 기반 working tree

QEMU 기준: `7d0cdacac296be62e3310b24546b660aabd65179` 기반 working tree

## 1. 결론

Apollo QBox의 single-chip CFG2 timer topology를 FVP 측정과 Zena CSS hardware
구조에 맞게 전환했다.

핵심 결과는 다음과 같다.

1. 하나의 125MHz `css_system_counter`가 SMD, AP, SI0, SI1의 physical count
   state를 소유한다. 각 QEMU instance의 bridge가 이 provider를 CPU Generic
   Timer와 AP MMIO Generic Timer에 전달한다.
2. CPU별 comparator와 PPI는 QEMU `ARMCPU`에 남고, AP MMIO frame 0/1의
   comparator/control 및 SPI 49/48도 `arm_arch_timer_mmio`에 남는다. 공유하는
   것은 physical count뿐이다.
3. SMD와 SI0 `host_gtimer` view는 read-side `+4096` stub이 아니라 같은
   clock-driven provider를 관측한다.
4. AP MMIO reset state는 FVP의 `CNTNSAR=1`, `CNTACR0=0x3f`, `CNTACR1=0`과
   일치한다. secure frame은 정상 RAZ이고 임시 enable 대조군에서 공통 count를
   반환한다.
5. RSE는 CSS와 독립된 local `sse-counter` 하나와 `sse-timer` 네 개를 사용한다.
   secure/non-secure alias, PPC policy, IRQ 3/4/5/27과 reset target split을
   구현했다.
6. QBox full-system boot, FVP Iris snapshot 및 QBox/FVP differential 44/44를
   통과했다.

현재 구조를 한 문장으로 정리하면 다음과 같다.

> AP와 Safety Island는 하나의 CSS timebase를 공유하고 RSE는 독립 local
> timebase를 유지하며, 각 timer의 comparator와 interrupt state는 consumer별로
> 독립적이다.

FVP와 하드웨어 기준에 대한 상세 분석은
[`arm-zena-css-fvp-timer-counter-analysis-ko.md`](arm-zena-css-fvp-timer-counter-analysis-ko.md)를
참조한다.

## 2. 비교 기준

### 2.1 FVP에서 확인된 기준 동작

현재 FVP를 Iris로 측정한 결과는 다음과 같다.

- 물리 REFCLK: 125MHz
- 정상 SMD `CNTINCR`: 0, FVP default 실효 increment: 1
- 정상 visible count 증가율: 125MHz
- debugger 강제 `CNTINCR=8`: 1GHz 대조군이며 정상 boot 계약이 아님
- 같은 simulation timestamp에서 SMD, AP CPU, SI0 CPU, SI1 CPU 및 RSE
  `TIMER0`~`TIMER3`의 count가 동일
- AP MMIO non-secure frame 0은 정상 boot에서 CSS count와 125MHz를 반환한다.
  secure frame 1은 `CNTACR1=0`에서 RAZ이며, `0x3f`로 강제 enable한 대조군에서
  같은 CSS count와 125MHz를 반환한다. IRQ는 각각 SPI 49, SPI 48이다.
- CFG2 SI1 FVP timer PPI는 `CNTP=29`, `CNTV=27`, `CNTHPS=20`이고, `CNTHP`,
  `CNTHV`, `CNTHVS`, `CNTPS` comparator register는 해당 CPU에 없다.
- RSE Local System Counter address는 FVP에서 unmapped이며, RSE timer는 CSS
  공통 counter에 alias된 모델 단순화

### 2.2 하드웨어 목표 동작

Zena CSS 하드웨어 기준으로는 다음 두 count domain을 구분해야 한다.

1. CSS REFCLK System Counter: AP와 Safety Island에 공통 시간 축 제공
2. RSE Local System Counter: RSE `TIMER0`~`TIMER3`의 `CNTVALUEB` 제공

FVP의 RSE alias 동작은 하드웨어 목표가 아니라 필요할 경우에만 제공할 수 있는
FVP compatibility mode로 보아야 한다.

## 3. 구현 전 QBox topology와 전환 결과

3.1~3.7은 문제를 재현한 2026-07-21 baseline이다. 이 절 안의 "현재"는 해당
baseline을 뜻하며, 구현 후 상태는 3.8과 4절에 정리한다.

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
**62.5MHz**이다. 현재 wrapper가 노출하는 NS physical, virtual, NS hypervisor,
secure physical timer output은 PPI 30/27/26/29에 연결되어 있다. 그러나 QEMU가
갖는 HYPVIRT와 Secure EL2 physical/virtual timer output(PPI 28/20/19)은 wrapper가
노출하지 않으므로 AP timer PPI wiring 전체가 완료됐다고 볼 수 없다. 또한
125MHz AP MMIO timer 및 FVP의 125MHz 공통 count와도 state를 공유하지 않는다.

### 3.4 AP memory-mapped Generic Timer

`ap_compute.lua:453-474`은 local QEMU의 `qemu_arm_arch_timer_mmio`를 사용한다.

| 항목 | 현재 값 | FVP/하드웨어 기준 | 상태 |
| --- | ---: | ---: | --- |
| Control base | `0x1A810000` | `0x1A810000` | 일치 |
| Secure frame | `0x1A820000`, frame 1 | 동일 | 일치 |
| Non-secure frame | `0x1A830000`, frame 0 | 동일 | 일치 |
| Secure IRQ | SPI 48 | SPI 48 | 일치 |
| Non-secure IRQ | SPI 49 | SPI 49 | 일치 |
| `cntfrq` | 125MHz | 정상 FVP CSS/AP MMIO NS frame 125MHz | rate 일치, state는 분리 |

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

interrupt wiring도 timer class 기준으로 교정이 필요하다. 현재 Lua는 wrapper의
generic physical/virtual/hypervisor/secure output을 PPI 20/27/19/29에 연결한다
(`si_cl0.lua:489-492,1085-1095`). 그러나 SI0 hardware table은 Secure EL2 physical
`CNTHPS=PPI20`, virtual `CNTV=PPI27`, secure physical `CNTPS=PPI29`만 정의하고
PPI 19를 reserved로 둔다
(`09-programmers-model-for-zena-css.md:1644-1656`). generic physical output을
PPI20에 연결하거나 hypervisor output을 PPI19에 연결하는 현재 mapping은 이름만
바꿔 유지할 수 없으며 QEMU output의 architected identity부터 분리해야 한다.

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
System Counter의 consumer와 compare register가 없으며, RSE NVIC의 timer IRQ
3/4/5/27에도 연결된 device가 없다.

RSE security path도 timer를 연결할 준비가 끝난 상태는 아니다. 현재
`rse_protection_ctrl`은 PPC register state를 제공하지만 downstream transaction을
차단하는 bus filter가 아니며, QEMU initiator의 RequestContext normalization은
secure bit만 채우고 `MemTxAttrs.user`를 privileged bit로 전달하지 않는다
(`qbox/systemc-components/common/include/tlm-extensions/request-context.h:65-75`,
`qbox/qemu-components/common/include/ports/initiator.h:706-720`). 따라서 향후 S/NS
timer alias를 단순 route만 하면 PPC0/PPC2 policy가 실제 access에 적용되지 않는다.

현재 구조는 하드웨어의 별도 RSE local counter도 완성하지 못했고, FVP의 CSS
공통 counter alias도 재현하지 못한다.

두 object 모두 명시적인 frequency를 받지 않아 `host_gtimer` 기본값 125MHz를
register field에 사용한다. 반면 TF-M common RSE 설정은 system timer의 기본
frequency를 32MHz로 정의한다. 하드웨어 guide는 RSE Local System Counter의
입력 clock source/rate를 직접 명시하지 않으며, 현재 FVP는 CSS 125MHz count를
RSE timer에 alias한다. 따라서 QBox RSE에 적용할 실제 frequency는 이 세 값을
구분한 후 별도로 확정해야 한다.

### 3.8 구현 후 topology

```text
SystemC simulation time
        |
        +--> css_system_counter, 125MHz x increment 1
        |      |
        |      +--> SMD control/read frontends
        |      +--> AP QEMU bridge
        |      |      +--> A720AE CPU timers and PPIs
        |      |      +--> AP MMIO frame 0/1 and SPIs 49/48
        |      +--> SI0 QEMU bridge
        |      |      +--> R82 CPU timers and PPIs
        |      |      +--> SI0 CNTBase frontend
        |      +--> SI1 QEMU bridge
        |             +--> R82 CPU timers and PPIs
        |
        +--> RSE-local QEMU Clock
               +--> one sse-counter
                      +--> TIMER0, IRQ 3
                      +--> TIMER1, IRQ 4
                      +--> TIMER2, IRQ 5
                      +--> TIMER3, IRQ 27
```

MULTI TCG QEMU instance는 SystemC sample 시점보다 local virtual clock이 앞설 수
있다. QBox snapshot은 각 raw count를 bridge epoch로 해당 SystemC observation
time에 역매핑해 provider count와 일치하는지 확인한 뒤, 공통 sample 시점의
`counter`로 정규화한다. 따라서 timestamp 숫자의 우연한 일치가 아니라 실제
provider identity를 검증한다.

## 4. 주파수 및 state 비교표

| View | FVP 현재 동작 | QBox 구현 후 동작 | 판정 |
| --- | --- | --- | --- |
| SMD counter | 정상 125MHz REFCLK × 실효 1 = 125MHz count | shared `css_system_counter`, 125MHz × 1 | 일치 |
| AP CPU `CNTPCT` | SMD count와 동일, reported 125MHz | AP bridge를 통해 CSS count 공유, reported 125MHz | 일치 |
| AP MMIO S/NS | NS frame 0은 공유, S frame 1은 RAZ/enable 대조군에서 공유 | 같은 access reset과 CSS count, frame별 state 및 SPI 49/48 독립 | 일치 |
| SI0 CPU `CNTPCT` | SMD count와 동일, reported metadata는 별도 | SI0 bridge를 통해 CSS count 공유, reported metadata 독립 | 일치 |
| SI0 CNTBase | SMD count와 동일 | shared provider frontend, read side effect 없음 | 일치 |
| SI1 CPU `CNTPCT` | SMD count 공유, reported 100MHz | CSS count 공유, reported 100MHz | 일치 |
| RSE LSC | FVP에서 미구현, TIMER0~3은 CSS alias | 독립 local state, provisional input 125MHz | hardware 구조 우선, expected deviation |
| RSE TIMER0~3 | FVP SMD count alias | 한 local counter 공유, IRQ 3/4/5/27 | hardware 구조 우선, expected deviation |

## 5. Fidelity gap 평가

### 5.1 해소: 공통 CSS counter

SMD, AP CPU/MMIO, SI0 CPU/CNTBase와 SI1 CPU가 한 provider를 사용한다. QBox
구조화 snapshot 두 지점에서 7개 view의 공통 sample count가 정확히 같았고 각 raw
QEMU observation도 epoch-mapped provider count와 일치했다.

### 5.2 해소: clock-driven `host_gtimer`

SMD와 SI0 frontend는 read 횟수가 아니라 `arm_system_counter`의 SystemC time을
관측한다. stable-read, partial write, enable/halt/reset과 deadline notification을
unit test로 검증했다.

### 5.3 해소: physical count와 reported frequency 분리

CSS physical count는 모두 125MHz이다. AP는 125MHz, SI1은 FVP처럼 100MHz를
보고하며 SI0의 architected metadata도 physical source와 독립적으로 유지한다.
AP MMIO는 125MHz를 보고하고 CPU와 같은 physical count를 사용한다.

### 5.4 해소, hardware debt 유지: RSE local timer

RSE Local System Counter, `TIMER0`~`TIMER3`, IRQ, S/NS alias, PPC와 reset target
split을 구현했다. 다만 공개된 Zena 자료로 physical LSC input rate와 실제
`nWARMRESETAON` source를 확정할 수 없어 각각 provisional 설정과 미연결 debt로
남긴다.

### 5.5 Medium: cross-chip sync가 register stub

PID/CID와 일부 register access만 제공하며 request-acknowledge, threshold,
network delay 및 failure state가 없다. single-chip boot에는 당장 영향이 작을 수
있지만 multi-chip fidelity에는 필요하다.

### 5.6 Medium: SI external frame 누락

`REFCLK_SSYSCLK_CNTBase0`의 system-visible alias가 직접 구현되어 있지 않다.
debugger 또는 다른 requester가 이 view를 사용할 때 하드웨어 map과 달라진다.

## 6. 구현된 QBox 목표 구조

### 6.1 기본 결정

QBox의 기본 구현은 FVP binary의 RSE 단순화를 그대로 복제하지 말고 Zena CSS
하드웨어 구조를 따른다.

```text
SystemC simulation time
        |
        +--> zena_css_ref_counter
        |      source_hz = 125MHz
        |      normal effective increment = 1
        |      count_hz  = 125MHz
        |      one coherent CNTCV state
        |          |
        |          +--> SMD control/read frames
        |          +--> AP CPU architectural timers
        |          +--> AP MMIO secure/non-secure frames
        |          +--> SI0 CPU and CNTBase views
        |          +--> SI1 CPU timers
        |
        +--> rse_local_system_counter
               source_hz = 125MHz provisional, runtime override 가능
               independent CNTCV state
               |
               +--> RSE TIMER0
               +--> RSE TIMER1
               +--> RSE TIMER2
               +--> RSE TIMER3

cross-chip synchronization: separate control/state-machine block
```

초기 구현에는 RSE `TIMER0`~`TIMER3` source를 CSS counter로 바꾸는
`fvp_compat` mode를 넣지 않는다. 하드웨어-correct local domain이 검증된 뒤에도
byte-for-byte FVP 실험이 실제로 필요하다는 별도 요구가 있을 때만 후속 옵션으로
검토한다.

### 6.2 공통 counter backend

재사용 가능한 SystemC counter component는 다음 state를 갖는다.

- `base_count`
- `base_sc_time`
- physical `source_hz`
- per-source `increment` 또는 명시적인 `count_hz`
- enable 및 halt 상태
- frequency ID와 scaling 설정
- physical reset source와 retention policy

read는 다음과 같이 simulation time에서 계산하며 side effect가 없어야 한다.

```text
count(now) = base_count + elapsed(now, base_sc_time) * count_hz
```

enable, frequency, scaling 또는 `CNTCV`가 바뀔 때 현재 count를 새 anchor로
고정하고 consumer에 deadline 재계산 notification을 보낸다.

### 6.3 QEMU CPU timer와 연결

CPU internal Generic Timer의 register, comparator, PPI 및 virtualization state는
QEMU `ARMCPU`에 남겨야 한다. `CNTPCT`를 MMIO timer로 대체하거나 PPI를 SPI로
우회하면 안 된다.

local QEMU의 `gt_get_countervalue()`와 deadline conversion에 opt-in external
counter-provider hook를 추가했고, Apollo CPU wrapper가 shared SystemC counter
service를 연결한다. hook가 없는 다른 QEMU machine은 기존
`QEMU_CLOCK_VIRTUAL` 동작을 그대로 유지한다.

provider 연결과 PPI 연결은 별도 문제이다. AP wrapper는 hardware의
PPI 19/20/26/27/28/29/30 timer class를 필요한 PE feature에 맞게 노출해야 하고,
SI0은 PPI 20/27/29만 사용해야 한다. CFG2 SI1은 FVP 전용이며 Iris로 확인한
`CNTHPS=PPI20`, `CNTV=PPI27`, `CNTP=PPI29`만 적용한다. 이 FVP CPU에 없는
`CNTHP`, `CNTHV`, `CNTHVS`, `CNTPS` comparator를 추정해 연결하거나 AP/SI에
같은 mapping을 공통 적용해서는 안 된다.

### 6.4 AP MMIO timer와 연결

`arm_arch_timer_mmio`의 frame별 comparator/IRQ 구현은 유지하고 counter 계산만
같은 external provider를 사용하도록 구현했다. 다음 특성을 동시에 보존한다.

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

RSE Local System Counter는 CSS counter와 별도 state를 가지며 다음을 구현했다.

- control/read frame coherence
- `CNTVALUEB`를 TIMER0~3에 공급
- timer별 CVAL/control/IRQ 3/4/5/27
- 모든 TIMER0~3/Local Counter의 PD_AON 소속과 TIMER0~2 대비 TIMER3/LSC의
  reset-source/retention 차이
- Secure/Non-secure alias 및 PPC access policy

### 6.6 주파수 계약 선결 조건

정상 배포 FVP의 executed contract는 125MHz REFCLK, `CNTINCR=0`, 실효 increment
1, visible count 125MHz이다. debugger로 `CNTINCR=8`을 강제한 대조군에서만
1GHz가 측정됐다. SCP source의 `SYSCNT_INCR=8` 의도와 달리 배포 ELF는 32-bit
impdef register에 64-bit store를 수행하고 FVP가 이를 WI로 처리한다. component를
이 작업에서 변경하지 않았다. 사용자 결정에 따라 정상 배포 FVP의 executed
125MHz를 Apollo production 기준으로 사용하고 source 불일치는 별도 component
debt로 유지했다.

완료된 검증은 다음과 같다.

1. 정상 FVP boot의 `CNTINCR`, `CNTFID0`, `CNTFRQ_EL0` 수집: 완료
2. 알려진 FVP simulation interval의 125MHz count delta 측정: 완료
3. 강제 `CNTINCR=8`의 1GHz control 측정: 완료
4. shared CSS provider와 AP/SI production wiring: 완료
5. QBox/FVP two-sample differential: 44/44 pass

RSE local domain은 CSS와 별도 결정 항목이다. 실제 hardware clock 자료가 없으므로
QBox는 override 가능한 125MHz provisional input을 사용하고 TF-M의 32MHz write는
reported metadata로 유지한다. 이 값은 hardware frequency signoff가 아니다.

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
- 모든 RSE timer의 PD_AON 소속과 TIMER0~2 대비 TIMER3/LSC의
  reset-source/retention 차이
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

## 8. 구현 완료 순서와 후속 항목

1. **P0 완료**: FVP boot-time Iris 측정과 125MHz executed contract 확정
2. **P1 완료**: SMD control/read와 SI timer view를 하나의 clock-driven backend로 교체
3. **P2 완료**: AP/SI CPU timer와 AP MMIO timer를 shared provider에 연결
4. **P3 완료**: 독립 RSE Local System Counter와 TIMER0~3 구현
5. **P4 일부 후속**: timer alias/PPC는 완료, cross-chip sync state machine과
   외부 SI frame은 single-chip 이후 fidelity debt
6. **P5 완료**: FVP/QBox identity와 count rate differential 44/44 통과

각 단계에서 component source가 아니라 `hsoc-stack/tools/qbox`,
`hsoc-stack/tools/qbox-platform`, `hsoc-stack/tools/qemu` 경계 안에서 수정하는 것이
프로젝트의 ownership 원칙과 맞다.

최종 검증 evidence:

- QBox full-system: `build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final/`
- FVP Iris snapshot: `build/qbox-apollo-qvp/timer-validation/final-differential/fvp/timer-snapshot-final.json`
- differential 44/44 pass: `build/qbox-apollo-qvp/timer-validation/final-differential/timer-differential.json`
- map/coverage: `build/qbox-apollo-qvp/ap-map-9-1-1/ap-map-audit.json`,
  `build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final/full-coverage-audit.json`

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

- QBox 결론은 구현 후 source와 runtime artifact를 함께 사용했다. live CL0+CL1
  full-system boot, QBox snapshot, FVP Iris snapshot과 differential을 실행했다.
- codebase-memory index는 관련 repository에서 `ready`였으나 일부 index coverage
  metadata를 제공하지 못했다. 모든 핵심 판정과 negative claim은 해당 source를
  직접 읽고 Apollo Lua 전체를 검색해 재확인했다.
- 여러 `QemuInstance`의 virtual clock은 SystemC scheduler와 temporal decoupling될
  수 있다. snapshot은 bridge epoch로 raw observation time을 검증하고 공통 sample
  time으로 정규화하므로 local clock 숫자의 일치에 의존하지 않는다.
- FVP AP MMIO frame의 정상 access-control과 count identity를 확인했다. secure
  frame 1의 정상 RAZ는 연결 부재가 아니라 `CNTACR1=0`의 결과다.
- 정상 배포 FVP의 architecture-visible CSS frequency는 125MHz로 측정됐고 QBox
  production contract도 이를 사용한다. SCP source/deployed instruction 불일치는
  component source를 건드리지 않고 별도 debt로 유지한다.
- RSE LSC의 실제 clock, S/NS 정책과 integration reset runtime signoff는 미확정이다.
