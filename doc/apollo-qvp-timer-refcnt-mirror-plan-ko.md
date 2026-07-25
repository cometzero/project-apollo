# Apollo QVP Timer 및 REFCLK Counter Mirror 구현 계획

작성일: 2026-07-24

대상:

- Arm Zena CSS RD-Aspen CFG2
- `FVP_Zena_CSS_Cfg2`
- Apollo QVP의 AP, Safety Island CL0/CL1 timer 및 SMD REFCLK counter

이 문서는 최초 구현 계획과 2026-07-24 구현·검증 결과를 함께 기록한다.
계획 대비 실제 적용 범위와 남은 fidelity debt는 12절에 정리했다.

## 1. 목표

Apollo QVP에서 다음 두 요구를 동시에 만족하는 것이 목표다.

1. FVP에서 관측되는 CSS 공통 PCT 동작과 timer interrupt 동작을 재현한다.
2. CPU counter read와 timer deadline 계산에서 QEMU와 QBox/SystemC 사이의
   동기 callback, 공용 mutex 및 cross-instance bridge를 제거한다.

권장 구조는 다음과 같다.

```text
                    SMD REFCLK authority
              count/rate/enable/epoch/generation
                              |
                    event-driven snapshot
                              |
           +------------------+------------------+------------------+
           |                  |                  |                  |
      AP QEMU mirror     SI0 QEMU mirror    SI1 QEMU mirror   RSE mirror*
           |                  |                  |                  |
      local ARMCPU       local ARMCPU       local ARMCPU       RSE TIMER0~3
      local MMIO timer   local timer state  local timer state  / local counter

* RSE mirror는 설정 가능하며 기본값은 enable이다.

CPU PCT read/deadline hot path:
QEMU local clock + local immutable snapshot only
```

SMD counter는 architectural authority이고, 각 mirror는 성능을 위한 실행상
복제본이다. mirror를 독립적으로 쓰거나 서로 다른 소유 counter로 취급하지 않는다.

## 2. 기준 revision과 실행 환경

| 항목 | 값 |
| --- | --- |
| 상위 저장소 | `2f3b72c0277a03145c506c1fab91e16ee26083f2` |
| QBox | `9886434df730969e34f30ba0dd85b8869d0b7786` |
| QBox Platform | `2e6b210277a72c09f891637c29e383a168bca2ae` |
| QEMU | `080a0c2e4d80aa66298e7e0ca9c7287e2ff5bc29` |
| FVP | Fast Models 11.31.25, 2026-02-25 |
| FVP binary SHA-256 | `246dfb8637d6d4264ce6817089e55a4b8335e47d9f46f92cb128b6eed2df2b37` |
| FVP config SHA-256 | `ef2c583bc162e423e75e0fd691d3fe678fe8545dd3369d0ceccee239ee51c24e` |
| FVP image | `nexios-bsp-initramfs-apollo-fvp-20260723140147.wic` |
| FVP image SHA-256 | `789833b498ad60c91ceb15eace351efa471ba7807bfec3f8c62eb639d7f3ed43` |

활성 Yocto 기본 machine은 `apollo-qvp`이다. 이번 FVP 측정은 비교 reference로
`apollo-fvp` BSP initramfs image를 사용했다.

## 3. 2026-07-24 FVP Iris 실측

### 3.1 측정 방법

FVP를 BSP shell까지 정상 부팅한 뒤 Iris로 전체 모델을 정지했다. 다음 값을
동일한 halted simulation timestamp에서 수집했다.

- SMD `ref_counter`의 `CNTCR`, `CNTFID0`, `CNTINCR`
- SMD `CNTReadBase` PCT
- AP CPU0 `CNTPCT_EL0`, `CNTFRQ_EL0`
- AP non-secure MMIO REFCLK frame PCT
- SI0 CPU0 `CNTPCT_EL0`, `CNTFRQ_EL0`
- SI0 `CNTReadBase` PCT
- SI1 CPU0 `CNTPCT_EL0`, `CNTFRQ_EL0`
- Iris `simulationTime_get()`의 ticks 및 tick rate

PCT memory frame은 64-bit transaction 한 번으로 읽지 않고 firmware와 동일한
32-bit high-low-high 순서로 읽었다.

```text
do {
    high1 = PCTH;
    low   = PCTL;
    high2 = PCTH;
} while (high1 != high2);
```

처음 수행한 단일 64-bit SI0 MMIO read는 count가 `2^32`를 넘은 뒤 high word를
결합하지 못했다. 이 실패 결과는 다음 파일에 보존했다.

```text
build/qbox-apollo-qvp/timer-refcnt-fvp-20260724/
  pct-rate-measurement-64bit-read-invalid.json
```

최종 측정 원본은 다음 파일이다.

```text
build/qbox-apollo-qvp/timer-refcnt-fvp-20260724/
  pct-rate-measurement.json
```

### 3.2 정상 부팅 결과

두 표본 사이의 측정값은 다음과 같다.

| 항목 | 값 |
| --- | ---: |
| Iris timebase | `1,000,000,000,000 ticks/s` |
| simulation time delta | `7,783,204,631,900 ticks` |
| simulation time delta | `7.7832046319 ms` |
| PCT delta | `972,900,579` |
| 125 MHz 예상 floor | `972,900,578` |
| floor 대비 오차 | `+1 tick` |
| 환산 visible rate | `125,000,000.00160602 Hz` |
| `CNTCR` | `0x101` |
| `CNTFID0` | `125,000,000` |
| `CNTINCR` | `0` |

결론은 다음과 같다.

> 현재 정상 배포 FVP의 visible PCT는 125 MHz이다.

소스에 존재하는 `REFCLK 125 MHz * CNTINCR 8 = 1 GHz` 의도는 현재 정상 부팅
실행 결과가 아니다. 현재 배포 firmware와 FVP에서는 `CNTINCR=0`이고, FVP
default effective increment 1에 따라 visible PCT가 125 MHz로 증가한다.

### 3.3 view 동일성

시작 PCT는 `25,757,931,293`, 종료 PCT는 `26,730,831,872`였다. 두 시점에서
다음 view는 모두 SMD PCT와 정확히 같았다.

- AP CPU0 `CNTPCT_EL0`
- AP non-secure MMIO REFCLK PCT
- SI0 CPU0 `CNTPCT_EL0`
- SI0 `CNTReadBase` PCT
- SI1 CPU0 `CNTPCT_EL0`

frequency metadata는 서로 달랐다.

| View | PCT source 실측 | `CNTFRQ_EL0` 또는 FID |
| --- | --- | ---: |
| SMD REFCLK | CSS 공통 PCT | 125 MHz |
| AP CPU0 | SMD와 동일 | 125 MHz |
| AP MMIO NS | SMD와 동일 | 125 MHz |
| SI0 CPU0 | SMD와 동일 | 0 |
| SI0 CNTRead | SMD와 동일 | SMD FID 125 MHz |
| SI1 CPU0 | SMD와 동일 | 100 MHz |

따라서 현재 FVP의 `CNTFRQ_EL0`는 모든 domain에서 PCT 증가율을 직접 결정하는
값이 아니다. 특히 SI1은 reported frequency 100 MHz와 실제 공통 PCT 125 MHz가
불일치한다. QVP가 FVP 실행 동작을 우선할 경우 이 불일치를 임의로 정리해서는
안 되고 explicit fidelity contract로 관리해야 한다.

### 3.4 부팅 evidence

같은 실행에서 다음 BSP marker를 확인했다.

```text
NEXIOS_BSP_TEST name=arch_timer result=PASS
NEXIOS_BSP_INITRAMFS_READY machine=apollo-fvp
```

로그:

```text
build/qbox-apollo-qvp/timer-refcnt-fvp-20260724/run/
  fvp_stdout.log
  uarts/rse.log
  uarts/safety_island_cl0.log
  uarts/safety_island_cl1.log
  uarts/tf_a.log
  uarts/u_boot_linux.log
```

## 4. 과거 direct shared-counter 구현의 문제

제거된 과거 구현은 다음 hot path를 사용했다.

```text
guest CNTVCT/CNTPCT or timer programming
  -> QEMU ARM generic timer
  -> counter-provider proxy
  -> libqemu callback
  -> QBox per-instance bridge
  -> shared SystemC counter
  -> mutex
  -> count/deadline calculation
```

문제는 모델링된 TLM delay 하나가 아니라 다음 비용의 결합이었다.

- 모든 CPU PCT read가 QEMU/QBox ABI 경계를 통과
- comparator rearm도 외부 deadline callback을 사용
- AP, SI0, SI1 vCPU가 하나의 counter mutex에 경쟁
- counter state 변경 알림이 QEMU I/O thread job으로 늦게 전달
- 각 QEMU instance의 local virtual time과 fixed epoch offset 사이에 skew 가능
- proxy, observer, drain, lifecycle 및 ABI negotiation 코드가 필요

`14b73e8e95582eec665814fb492d7ae49bc5b34a`는 AP CPU timer만 native QEMU로
복구하고 AP MMIO bridge는 유지했다. 이 변경 후 Linux late wakeup이 해소된
기록은 CPU timer hot path의 외부 callback이 핵심 위험이었다는 증거다.

새 구현은 다음 금지 조건을 갖는다.

- CPU PCT read에서 QBox/SystemC callback 금지
- CPU timer deadline 계산에서 QBox/SystemC callback 금지
- 모든 QEMU instance가 경쟁하는 global counter mutex 금지
- timer read 때마다 bridge synchronization 금지

## 5. 설계 계약

### 5.1 authoritative state

SMD에는 하나의 authoritative affine counter state를 둔다.

```text
RefclkState {
    anchor_sim_time;
    anchor_count;
    input_frequency;
    increment;
    enabled;
    generation;
}
```

현재 count는 다음과 같이 계산한다.

```text
effective_rate = input_frequency * effective_increment

count(t) =
    enabled
      ? anchor_count + scale(t - anchor_sim_time, effective_rate)
      : anchor_count
```

정수 계산은 64-bit wrap과 floor 규칙을 정의하고, 중간 곱셈에는 충분한 폭을
사용한다.

### 5.2 frame state와 count state 분리

다음 상태는 frame 또는 timer마다 독립이다.

- `CVAL`, `TVAL`
- enable, mask, ISTATUS
- security/access control
- IRQ output
- reset state

다음 상태는 CSS PCT consumer 사이에서 공유한다.

- count epoch
- count value
- effective rate
- counter enable
- generation

즉 comparator와 IRQ는 local이고 PCT time authority만 공유한다.

### 5.3 QEMU local mirror

AP, SI0, SI1 `QemuInstance`마다 하나의 local affine mirror를 둔다. RSE는
platform 옵션이 enable일 때 RSE counter/timer component가 사용하는 local
mirror를 추가한다.

```text
LocalCounterMirror {
    local_anchor_qemu_ns;
    anchor_count;
    effective_rate;
    enabled;
    generation;
}
```

QEMU 내부 hot path는 `QEMU_CLOCK_VIRTUAL`과 local mirror만 읽는다.

```text
local_count(qemu_ns) =
    anchor_count +
    scale(qemu_ns - local_anchor_qemu_ns, effective_rate)
```

mirror update는 QBox가 snapshot setter를 호출하는 push 방식으로 한다. QEMU가
read 때마다 SMD를 pull하면 과거 구조와 같은 문제가 다시 생긴다.

### 5.4 QEMU 구현 최소화

QEMU 변경은 다음 기능만 포함한다.

1. QEMU 내부에 local affine snapshot 보관
2. ARM Generic Timer count/deadline 계산이 local snapshot을 선택 가능
3. snapshot generation 변경 시 기존 timer deadline 재계산
4. libqemu 또는 QOM을 통한 event-driven snapshot setter
5. VMState 또는 QBox coordinated checkpoint 계약

QEMU에서 제외할 기능:

- SystemC callback
- QBox observer callback
- cross-instance locking
- SMD register model
- power/reset policy
- Apollo-specific address 및 topology

Apollo-specific authority, power/reset policy와 mirror 배포는
`qbox-platform`이 소유한다.

### 5.5 RSE mirror 옵션

RSE의 SMD counter mirroring은 platform elaboration 시점에 선택한다.

```text
QBOX_APOLLO_RSE_SMD_COUNTER_MIRROR=true
```

계약은 다음과 같다.

| 값 | 동작 |
| --- | --- |
| `true` 또는 미지정 | SMD authority snapshot을 RSE local mirror에 배포한다. 현재 FVP의 CSS counter alias 동작과 비교하기 위한 기본 모드다. |
| `false` | RSE Local System Counter가 독립적인 epoch, rate, enable 및 reset state를 소유한다. Zena hardware 구조 검증용 모드다. |

Lua는 환경값을 boolean으로 해석한 뒤 `qemu_sse_counter_mirror`에 전달할
authority object를 선택한다. `true`이면 `platform.css_system_counter`,
`false`이면 `rse_local_system_counter`를 전달한다. 두 mode가 같은 mirror
component를 사용하고 authority만 달라지므로 별도 CCI mode parameter는
추가하지 않았다. 환경변수 미지정 기본값은 `true`다.

이 옵션은 runtime register로 변경하지 않는다. 실행 중 mode 변경은 PCT
monotonicity, pending deadline 및 checkpoint state를 동시에 바꿔야 하므로 첫
구현 범위에서 제외한다.

## 6. synchronization 정책

### 6.1 반드시 snapshot을 갱신할 시점

- simulation start
- cold reset 후 초기 epoch 확정
- CPU 또는 subsystem reset deassert 직전
- SMD `CNTCR`, `CNTCV`, `CNTINCR`, FID/rate 관련 write
- counter enable/disable
- subsystem power-on 및 resume 직전
- checkpoint restore
- local QEMU clock policy 변경
- QEMU/SystemC coordinated synchronization barrier
- RSE mirror가 enable인 경우 RSE reset/power release 직전

snapshot update 후에는 다음 순서를 지킨다.

```text
domain quiesce
  -> new snapshot publish
  -> old comparator event cancel
  -> deadline recalculate
  -> ISTATUS/IRQ update
  -> reset/power release
```

### 6.2 갱신하지 않을 시점

- `CNTVCT/CNTPCT` read
- `TVAL/CVAL` read
- 일반 comparator write
- timer IRQ polling
- debug register read

일반 comparator write는 이미 적용된 local mirror를 사용한다. snapshot generation이
변할 때만 기존 comparator를 reschedule한다.

### 6.3 power/reset

- AP/SI local warm reset은 SMD authority를 초기화하지 않는다.
- local reset은 comparator/control/IRQ state만 reset한다.
- power-off 동안 SMD REFCLK가 유지되면 PCT는 계속 affine하게 진행한다.
- power-on 시 reset deassert 전에 최신 authority snapshot을 적용한다.
- SMD authority reset은 full-platform reset에만 적용하는 것을 초기 정책으로 한다.
- RSE SMD mirror가 enable이면 RSE local reset은 comparator/IRQ만 reset하고
  mirror count는 SMD authority를 계속 따른다.
- RSE SMD mirror가 disable이면 RSE Local System Counter는 PD_AON 및
  `nWARMRESETAON` 계약에 따라 독립적으로 reset한다.
- 실제 SMD power/reset domain은 FVP reset experiment 또는 추가 Arm integration
  문서로 확정한다.

### 6.4 monotonicity

- 실행 중인 guest-visible PCT를 뒤로 이동시키지 않는다.
- correction이 음수이면 quiesced reset boundary에서만 reanchor하거나, 기존
  count가 새 authority를 따라잡을 때까지 hold/slew하는 정책을 선택한다.
- 첫 구현에서는 quiesced boundary reanchor만 지원한다.
- unsupported active backward correction은 진단 오류로 처리한다.

## 7. subsystem별 계획

### 7.1 SMD

- `CNTControlBase`, `CNTReadBase`가 같은 authority를 참조하게 한다.
- sync frame에 별도 count 변수를 두지 않는다.
- `host_gtimer`의 read 횟수 기반 `m_counter += increment` 동작을 제거한다.
- `transport_dbg`는 observational이어야 하며 count나 state를 변경하지 않는다.
- 32-bit H-L-H read와 64-bit wrap을 검증한다.

### 7.2 AP

- CPU Generic Timer PPI는 기존 `ARMCPU`가 소유한다.
- AP MMIO secure/non-secure frame은 frame별 comparator와 SPI 48/49를 유지한다.
- CPU와 MMIO frame은 동일 AP mirror snapshot을 사용한다.
- AP `CNTFRQ_EL0`와 MMIO `CNTFRQ`는 FVP baseline 125 MHz를 보고해야 한다.
- CPU timer를 SystemC MMIO timer로 대체하지 않는다.

### 7.3 SI0

- CPU Generic Timer는 local QEMU mirror를 사용한다.
- SI0 `CNTCTLBase/CNTBase`의 comparator state는 local이다.
- SI0 SMD ATW `CNTControlBase/CNTReadBase`는 SMD authority view이다.
- SCP가 control aperture와 local timer aperture를 하나의 logical gtimer로
  사용하는 계약을 유지한다.
- SI0 `CNTFRQ_EL0=0` FVP 동작을 그대로 재현할지는 firmware dependency를
  조사한 뒤 P1 gate에서 결정한다. PCT rate는 125 MHz authority를 따른다.

### 7.4 SI1

- 이번 FVP 실측에서는 `CNTFRQ_EL0=100 MHz`지만 PCT는 SMD 125 MHz count와
  동일했다.
- FVP equivalence target에서는 SI1도 CSS mirror를 사용한다.
- reported `CNTFRQ_EL0=100 MHz`와 effective PCT rate 125 MHz 차이는 명시적인
  FVP compatibility contract로 기록한다.
- hardware-led mode를 별도로 만들지 않는다. Zena hardware integration 근거가
  추가되면 이 계약 자체를 재검토한다.

### 7.5 RSE

- `QBOX_APOLLO_RSE_SMD_COUNTER_MIRROR` 옵션을 제공하고 기본값은 `true`로
  한다.
- 기본 enable 모드에서는 SMD authority를 RSE local mirror에 배포하고,
  RSE TIMER0~3의 count input이 이 mirror를 사용하게 한다. comparator, CVAL,
  mask, IRQ 및 reset-visible register state는 RSE timer마다 독립적으로 유지한다.
- disable 모드에서는 RSE Local System Counter가 독립적인 timebase를 소유하고
  TIMER0~3에 count를 공급한다. 이 모드는 Zena hardware의 PD_AON local counter
  구조를 검증하는 용도다.
- 기본 enable은 현재 FVP가 RSE timer를 CSS counter에 alias하는 동작과 비교하기
  위한 선택이다. 이는 RSE hardware가 본질적으로 SMD counter를 소유한다는
  의미가 아니다.
- 이번 2026-07-24 rate 측정은 RSE TIMER view를 다시 수집하지 않았다. 기존
  Iris characterization의 alias 결과를 기준으로 옵션을 정의하되, P5에서
  default-enable RSE PCT를 새로 수집해 SMD equality를 다시 검증한다.
- enable/disable 선택은 elaboration 전에 고정하며 runtime switching은 지원하지
  않는다.

## 8. 구현 단계

### P0. FVP contract 고정

상태: 이번 문서에서 완료.

- 정상 boot visible PCT 125 MHz
- `CNTCR=0x101`, `CNTFID0=125 MHz`, `CNTINCR=0`
- AP/SI0/SI1 PCT와 SMD PCT 동일
- 32-bit H-L-H read 필수

산출물:

```text
build/qbox-apollo-qvp/timer-refcnt-fvp-20260724/
```

### P1. SystemC SMD authority 구현

소유 저장소: `hsoc-stack/tools/qbox-platform`

예상 변경:

- reusable affine counter 또는 Apollo SMD authority component
- SMD control/read aperture adapter
- SI0 ATW view
- `host_gtimer` read-driven counter 제거 또는 component 교체
- authority math, reset, access 및 rollover unit test

QEMU 변경: 없음.

Gate:

- simulation time 대비 125 MHz PCT 증가가 floor ±1 tick
- control/read/SI0 ATW view 동일
- debug read side effect 없음

### P2. QEMU local snapshot provider

소유 저장소:

- generic provider: `hsoc-stack/tools/qemu`
- libqemu wrapper가 필요한 경우: `hsoc-stack/tools/qemu`
- QBox wrapper: `hsoc-stack/tools/qbox`

예상 변경:

- local affine snapshot state
- ARMCPU optional local provider 선택
- local deadline conversion
- generation update 및 timer reschedule
- event-driven setter
- QEMU qtest

계획 규모:

- QEMU: 중간, 약 6~10개 파일
- QBox core: 작음, 약 2~4개 파일

이는 일정 산정을 위한 범위이며 LOC 목표가 아니다.

Gate:

- PCT read와 deadline 계산에서 QEMU→QBox callback 0회
- shared mutex 획득 0회
- provider 미사용 machine의 QEMU timer 동작 변화 없음
- snapshot update 후 pending timer deadline/IRQ 재계산

### P3. Apollo 및 RSE mirror orchestration

소유 저장소: `hsoc-stack/tools/qbox-platform`

예상 변경:

- AP, SI0, SI1 instance별 mirror publisher
- RSE SMD mirror option parsing, 기본 enable 및 RSE mirror publisher
- Lua topology와 reset/power event 연결
- SMD generation 변경 배포
- reset deassert 전 synchronization
- checkpoint contract

Gate:

- synchronized halt 지점에서 SMD/AP/SI0/SI1 PCT 동일
- RSE mirror enable 시 SMD/RSE TIMER0~3 PCT 동일
- RSE mirror disable 시 RSE PCT가 독립 timebase/reset 계약을 따름
- 두 표본 사이 rate 125 MHz floor ±1 tick
- warm reset 전후 PCT monotonic
- power-off/on 후 comparator deadline 정상

### P4. AP MMIO 및 SI0 timer frame 연결

- AP MMIO S/NS frame이 AP local mirror 사용
- frame별 CVAL/TVAL/CTL/IRQ 독립
- secure/non-secure access control 유지
- SPI 48/49 유지
- SI0 local timer frame과 SMD control view 분리

Gate:

- MMIO frame qtest 및 SystemC component test
- AP secure/non-secure frame count 동일
- mask, ISTATUS, CVAL 및 IRQ deadline 검증

### P5. full-system 검증

- QBox local build
- Apollo full-system boot
- timer snapshot
- Linux/Zephyr sleep 및 timer interrupt probe
- FVP differential
- reset/power scenario
- 성능 측정
- RSE SMD mirror enable/disable 양쪽 mode 검증

## 9. 검증 계획

### 9.1 정적 및 unit test

```bash
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py

cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target host-gtimer-tests --parallel

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R 'timer|counter|gtimer' --output-on-failure
```

추가 test:

- affine count math
- enable/disable/reanchor
- 64-bit rollover와 H-L-H read
- annotated TLM delay
- `transport_dbg` 무부작용
- snapshot generation
- deadline reschedule
- warm reset monotonicity

### 9.2 QEMU test

- native ARM Generic Timer regression
- snapshot provider count/deadline
- provider 없는 기존 machine
- snapshot update와 pending IRQ
- VMState 또는 coordinated restore

### 9.3 QBox runtime

```bash
./local_build.sh qbox

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 600
```

필수 관측:

- AP Linux boot와 login/BSP-ready marker
- SI0/SI1 live marker
- AP/SI timer interrupt
- SMD/AP/SI0/SI1 normalized PCT
- 기본 RSE mirror enable에서 SMD/RSE TIMER0~3 PCT equality
- RSE mirror disable에서 독립 RSE Local Counter rate/reset
- reset 및 power transition

### 9.4 FVP differential

FVP와 QBox에서 다음을 같은 logical point 두 곳에서 수집한다.

- simulation timestamp
- SMD PCT
- AP CPU PCT
- AP MMIO NS/S PCT
- SI0 CPU 및 CNTBase PCT
- SI1 CPU PCT
- RSE TIMER0~3 PCT
- CNTCR, CNTFID0, CNTINCR

비교 기준:

- producer 사이 absolute count는 비교하지 않는다.
- 각 producer 내부 view 동일성과 두 sample 사이 rate를 비교한다.
- 125 MHz 예상 floor 대비 ±1 tick을 허용한다.

### 9.5 성능 gate

다음 두 기준을 모두 사용한다.

1. 구조적 gate
   - CPU PCT read당 cross-boundary callback 0
   - deadline 계산당 cross-boundary callback 0
   - global counter mutex 0
2. runtime gate
   - Linux `clock_nanosleep`/hrtimer overshoot
   - Zephyr timer tick 안정성
   - QEMU I/O thread queue latency
   - native timer baseline 대비 host CPU time

절대 wall-time 숫자는 host 부하에 민감하므로 구조적 gate가 우선이다.

## 10. 결정 및 blocker

### 10.1 현재 결정

- production comparison baseline은 정상 실행 FVP의 visible 125 MHz이다.
- `CNTINCR=8` source intent를 자동 적용하지 않는다.
- CPU timer는 QEMU ARMCPU 소유를 유지한다.
- mirror는 pull이 아니라 event-driven push 방식이다.
- SI1은 이번 FVP equivalence 범위에서 CSS PCT mirror를 사용한다.
- RSE SMD counter mirror는 설정 가능하며 기본값은 enable이다.
- RSE mirror disable mode에서는 RSE Local Counter가 별도 timebase를
  유지한다.

### 10.2 구현 중 해결할 blocker

1. SCP `CNTINCR=8` source 의도와 정상 실행 `CNTINCR=0` 불일치
2. SI0 `CNTFRQ_EL0=0`과 실제 125 MHz PCT
3. SI1 `CNTFRQ_EL0=100 MHz`와 실제 125 MHz PCT
4. SMD REFCLK의 정확한 power/reset domain
5. QEMU VMState와 SystemC authority의 atomic checkpoint 경계
6. RSE mirror disable mode에서 사용할 Local System Counter input rate

이 blocker들은 generic counter math와 unit test를 막지는 않는다. 그러나 full
fidelity sign-off 전에 결정 또는 명시적 debt 승인이 필요하다.

## 11. 완료 조건

다음 조건을 모두 만족해야 구현 완료로 판단한다.

- SMD control/read 및 SI0 view가 한 authority를 사용
- read 횟수가 아니라 simulation time으로 PCT 증가
- AP/SI0/SI1 mirror가 synchronization point에서 SMD와 일치
- 기본 RSE mirror enable에서 RSE TIMER0~3 PCT가 SMD와 일치
- RSE mirror disable에서 독립 Local Counter의 rate/reset 계약이 통과
- PCT rate가 125 MHz floor ±1 tick
- CPU read/deadline hot path에 QBox callback과 global mutex가 없음
- AP timer PPI와 MMIO SPI 48/49 topology 유지
- reset/power 후 PCT monotonic 및 timer IRQ 정상
- QEMU qtest, SystemC unit test, QBox build 통과
- Apollo QBox full-system BSP boot 통과
- FVP/QBox differential report 통과
- 구현 결과와 남은 fidelity debt를 관련 문서에 반영

## 12. 2026-07-24 구현 및 검증 결과

### 12.1 구현 상태

권장한 `SystemC authority + QEMU local affine mirror + event-driven push`
구조를 적용했다.

- `arm_system_counter`가 CSS REFCLK의 125 MHz authority를 소유한다.
- `host_gtimer`의 counter read는 read 횟수가 아니라 SystemC simulation
  timestamp로 계산한다.
- AP, SI0, SI1의 ARMCPU는 각 QEMU instance 내부 local affine mirror만 읽는다.
- AP secure/non-secure MMIO frame과 RSE SSE counter도 local mirror를 사용한다.
- authority publish 시 QEMU virtual time에 anchor count, running state,
  frequency 및 generation을 한 번에 push한다.
- snapshot 적용 시 ARM generic timer와 MMIO/SSE comparator deadline을
  QEMU 내부에서 다시 계산한다.
- `QBOX_APOLLO_RSE_SMD_COUNTER_MIRROR`의 미지정 기본값은 `true`다.
  `true`에서는 RSE TIMER0~3가 CSS authority snapshot을 사용하고,
  `false`에서는 별도 `rse_local_system_counter`를 사용한다.
- RSE local counter는 125 MHz, increment 1로 동작하며 AoN reset
  assert/deassert에 따라 reset·정지·재시작한다.
- timer snapshot은 같은 SystemC sample barrier에서 모든 local mirror를
  먼저 동기화한 뒤 관측한다.

QEMU의 CNTVCT/CNTPCT read 및 deadline hot path에는 QBox/SystemC callback이나
공용 counter mutex가 없다. provider를 사용하지 않는 QEMU machine은 기존
`QEMU_CLOCK_VIRTUAL` 경로를 그대로 사용한다.

### 12.2 변경 범위

| 저장소 | 주요 변경 |
| --- | --- |
| QEMU | ARMCPU generic timer local mirror, AP MMIO/SSE counter snapshot setter, deadline reschedule, libqemu timer/clock wrapper |
| QBox core | AArch64 counter mirror C++ wrapper와 ARM component API |
| QBox Platform | `arm_system_counter`, `host_gtimer`, AP/SI/RSE mirror publisher, snapshot collector, reset adapter, Apollo Lua topology |
| 상위 저장소 | timer snapshot schema/comparator, 정적 map 검사, Python test, 본 문서 |

독립 QEMU 실행 파일 빌드에서는 `accel/tcg/cpu-exec.c`가 libqemu 전용 PC-entry
callback을 `CONFIG_LIBQEMU` 없이 참조하는 문제가 드러났다. 다른 TCG callback
경계와 같은 조건부 컴파일을 적용하여 libqemu 비활성 QEMU와 libqemu 빌드를
모두 통과시켰다.

### 12.3 정적·단위·빌드 검증

| 검증 | 결과 |
| --- | --- |
| QEMU/QBox/QBox Platform `git diff --check` | 통과 |
| Apollo Lua `loadfile()` | 통과 |
| Python `py_compile` | 통과 |
| timer schema/map/runner pytest | `60 passed` |
| `arm_system_counter-tests`, `host_gtimer-tests` | `2/2 passed` |
| timer 정적 map 검사 | 통과 |
| QBox core boundary audit | 통과 |
| standalone QEMU aarch64/arm 빌드 | 통과 |
| `arm-arch-timer-mmio-test` | 통과, 3 subtests |
| `sse-timer-test` | 통과, 3 subtests |
| `./local_build.sh qbox` | 통과, `apollo_fvp_full_system` 포함 |

주요 생성 evidence:

```text
build/qemu-timer-qtest-standalone/timer-qtest-build.log
build/qemu-timer-qtest-standalone/timer-qtest-results.log
build/qbox-apollo-fvp/timer-refcnt-mirror/local-build-qbox-final.log
build/qbox-apollo-fvp/timer-refcnt-mirror/static-map.json
```

### 12.4 QBox full-system 검증

두 실행 모두 AP Linux login, RSE runtime, SI0 SCP-firmware 및 SI1 Zephyr/PFDI
marker를 통과했다.

| RSE mode | 결과 | 1 ms | 2 ms | login |
| --- | --- | ---: | ---: | ---: |
| mirror 미지정/default `true` | pass | 모든 CSS/RSE view `125,000` | 모든 CSS/RSE view `250,000` | 40.982 s |
| mirror `false` | pass | RSE local TIMER0~3 `125,000` | RSE local TIMER0~3 `250,000` | 41.574 s |

default mode에서는 SMD, AP CPU0, AP MMIO NS/S, SI0 CPU0/CNTBase, SI1 CPU0,
RSE TIMER0~3의 `counter`와 QEMU가 실제 관측한 `observed_counter`가 두
sample 모두 정확히 같았다. disable mode에서는 RSE view의
`counter_basis`가 `rse_local`이고 1 ms 동안 정확히 125,000 tick 증가했다.

최종 evidence:

```text
build/qbox-apollo-fvp/timer-refcnt-mirror/default-enabled/result.json
build/qbox-apollo-fvp/timer-refcnt-mirror/default-enabled/timer-snapshot.json
build/qbox-apollo-fvp/timer-refcnt-mirror/disabled-local/result.json
build/qbox-apollo-fvp/timer-refcnt-mirror/disabled-local/timer-snapshot.json
```

### 12.5 post-login qualification과 FVP 재수집 제한

일반 root-shell post-login probe도 별도로 실행했다. Linux login과 root shell,
timer probe, AP/SI/RSE boot marker, architected timer interrupt, AP MMIO timer,
UART, virtio, RPMsg/SI network는 관측했다. 그러나 현재 공용 Buildroot
rootfs에 `pfdi-cli`가 없어 PFDI 명령이 모두 `127`을 반환했고 SMMUv3 driver
pattern도 확인되지 않아 최종 runner 결과는
`qbox_post_login_probe_failed`다. 이는 timer mirror 또는 full-system boot
실패가 아니라 rootfs qualification blocker다.

```text
build/qbox-apollo-fvp/timer-refcnt-mirror/default-enabled-post-login/
```

기존 2026-07-24 FVP Iris 측정은 125 MHz와 CSS view identity를 증명했고,
통합 중 생성한 FVP differential report도 pass 상태다. 다만 최종 검증 시점에는
그 report의 입력이었던 FVP 원본 snapshot이 생성물 정리 후 남아 있지 않았다.
동일 Yocto FVP BSP image를 세 번 새로 부팅해 모두
`NEXIOS_BSP_INITRAMFS_READY`까지 확인했으나, 다음 program breakpoint가
실행을 정지시키지 않아 원본 snapshot을 재생성하지 못했다.

1. SI1 `z_cstart`, `Hyp` memory space
2. SI1 `z_cstart`, target 기본 memory space
3. AP U-Boot `_start`, `Hyp` memory space

따라서 현재 보존된 `fvp-differential.json`은 통합 당시 pass evidence로는
사용할 수 있지만 최종 소스 상태에서 재현한 fresh differential로 간주하지
않는다. 또한 fresh FVP RSE TIMER0~3 view는 아직 수집되지 않았다.

### 12.6 완료 판정과 남은 fidelity debt

핵심 목표인 read-time bridge 제거, QEMU-local count/deadline 계산, AP/SI/RSE
mirror 배포, RSE default-enable 옵션 및 두 mode의 full-system boot는 구현과
동적 검증을 완료했다.

다음 항목은 full fidelity sign-off 전 남은 debt다.

- SystemC authority와 모든 QEMU mirror를 하나의 atomic checkpoint로 저장·복원
- snapshot generation 변경과 pending deadline 재예약 전용 QEMU qtest
- 별도 warm-reset 전후 monotonicity 자동 시나리오
- power-off/on 중 pending comparator deadline과 IRQ 자동 시나리오
- fresh FVP CSS 및 RSE TIMER0~3 Iris snapshot 재수집
- `pfdi-cli`와 SMMUv3 probe를 포함한 qualification rootfs에서 coverage audit

따라서 Apollo QVP timer mirror 기능 구현과 BSP boot 검증은 완료했지만,
11절의 checkpoint, reset/power 자동 시나리오, fresh FVP differential까지
포함한 full fidelity sign-off는 완료 상태로 표시하지 않는다.
