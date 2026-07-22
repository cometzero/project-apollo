# Apollo QVP Timer, Counter 및 Reference Clock 구현 계획

작성일: 2026-07-22

상태: **single-chip CFG2 구현 및 검증 완료**. CSS shared-counter, AP/SI CPU와
MMIO timer, RSE local counter/timer, 구조화 QBox/FVP snapshot 및 differential
검증을 working tree에 구현했다. RSE LSC의 실제 hardware input frequency,
`nWARMRESETAON` source, cross-chip synchronization 및 migration은 아래에 명시한
후속 fidelity debt이며, 검증된 single-chip 계약을 실패로 처리하지 않는다.

기준 문서:

- [Arm Zena CSS FVP Timer, Counter 및 Reference Clock 분석](arm-zena-css-fvp-timer-counter-analysis-ko.md)
- [Arm Zena CSS FVP 대비 QBox Timer, Counter 및 Reference Clock 분석](qbox-fvp-timer-counter-comparison-ko.md)
- [Arm Zena CSS FVP Iris 디버깅 가이드](fvp-iris-debugging-guide-ko.md)

활성 기준은 `apollo-qvp`, RD-Aspen CFG2, AP 4 CPU,
`build/tmp_baremetal`이다(`build/conf/local.conf:6-24`). 구현 대상은
`hsoc-stack/tools/qemu`, `hsoc-stack/tools/qbox`,
`hsoc-stack/tools/qbox-platform`과 top-level 검증 도구뿐이다.
SCP-firmware, TF-M, TF-A, Linux, Zephyr 등 `components/` source는 관측 근거와
빌드 입력으로만 사용하고 이 계획에서 수정하지 않는다.

### 2026-07-23 AP CPU timer 회귀 교정

동일 Yocto image를 사용한 A/B에서 timer 적용 전 `sleep 3`은 3초 근처로
안정적이었지만, AP `ARMCPU`까지 external CSS counter bridge에 연결한 구성은
3초 요청이 평균 3.938초, 최대 5.45초까지 늦게 깨어났다. 양쪽 모두 Linux
clocksource는 `arch_sys_counter`, 주파수는 125MHz였으므로 고정 비율 오차가 아니라
external provider의 deadline 재평가/전달 지연으로 판정했다.

최종 구성에서는 AP CPU internal Generic Timer를 native
`cpu_arm_cortexA720AE` 경로로 복원한다. `ap_timer_counter_bridge`와 shared CSS
provider는 제거하지 않고 AP REFCLK MMIO frame에만 사용한다. 수정 후 Yocto는
`time sleep 3` 3.068초와 10회 평균 3.106초, local Buildroot는 3.02초와
10회 평균 3.068초였다. `/proc/uptime` 반복 측정에는 두 번의 `cut` 및 UART poll
비용이 포함된다. Evidence는
`build/qbox-apollo-qvp/timer-ab/fixed-yocto-20260723-005315/`와
`build/qbox-apollo-qvp/timer-ab/fixed-local-20260723-005714/`에 있다. 이후 절의
AP CPU external-provider 연결 설명은 구현 이력을 나타내며, production wiring은
이 교정 사항을 우선한다.

## 0. 구현 및 검증 결과

2026-07-22 현재 구현은 QEMU, QBox core, QBox Platform과 top-level 검증 도구
경계에만 존재하며 `components/` source는 수정하지 않았다. 최종 evidence는 다음과
같다.

| 검증 | 결과 | Evidence |
| --- | --- | --- |
| QEMU AP MMIO access/reset qtest | 9/9 pass | `build/qbox-apollo-qvp/timer-validation/20260722-final/qemu-mmio-qtest-2.log` |
| QBox 표준 local build | pass | `build/qbox-apollo-qvp/timer-validation/20260722-final/local-build-qbox.log` |
| Apollo static map | 76/76 pass | `build/qbox-apollo-qvp/ap-map-9-1-1/ap-map-audit.json` |
| live CL0+CL1 full-system boot | pass, Linux login 55.101초 | `build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final/result.json` |
| QBox timer snapshot | pass, CSS 7개 view exact identity | `build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final/timer-snapshot.json` |
| FVP Iris two-sample snapshot | pass | `build/qbox-apollo-qvp/timer-validation/final-differential/fvp/timer-snapshot-final.json` |
| QBox/FVP differential | 44/44 pass | `build/qbox-apollo-qvp/timer-validation/final-differential/timer-differential.json` |
| full coverage audit | pass | `build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final/full-coverage-audit.json` |

QBox의 여러 `QemuInstance`는 MULTI TCG에서 서로 다른 local virtual time까지
진행할 수 있다. 따라서 snapshot은 각 consumer의 raw count를 bridge epoch로
SystemC observation time에 매핑해 같은 provider 값인지 먼저 검증하고, JSON의
`counter`는 공통 sample timestamp 값으로 정규화한다. `observed_counter`와
`observation_time_ns`는 이 검증을 재현할 수 있도록 그대로 보존한다. 서로 다른
timebase의 두 sample rate는 count 양자화 오차 1 tick을 포함해 비교한다.

full-system 검증은 minimal Buildroot image에 `pfdi-cli`와 `systemctl`이 없으므로
일반 post-login qualification을 요구하지 않고 `--no-post-login-probe`로 실행했다.
대신 timer probe, RSE/SI0/SI1 marker, TF-A/U-Boot/Linux boot 및 login gate를 모두
통과했다. 이 선택은 timer 검증 범위를 줄이지 않으며, 배포 image에 없는 도구를
성공 조건으로 오인하지 않게 한다.

## 1. 최종 결정 요약

Apollo QVP는 하나의 전역 timer device를 만드는 방식이 아니라 다음 두 counter
domain을 구현해야 한다.

1. **CSS System Counter domain**
   - 물리적으로 하나인 CSS REFCLK 기반 count state를 SMD, AP, SI0 및 CFG2
     SI1이 공유한다.
   - count state는 QBox core의 재사용 가능한 SystemC provider가 소유한다.
   - AP, SI0, SI1은 서로 다른 QEMU DSO/`QemuInstance`이므로 각 instance 안에
     proxy를 하나씩 만들고 모두 같은 SystemC provider에 연결한다.
   - CPU Generic Timer의 comparator, virtualization register와 PPI는 QEMU
     `ARMCPU`에 그대로 둔다.
   - AP memory-mapped Generic Timer의 frame별 CVAL/control/ISTATUS와 SPI 48/49도
     QEMU `arm_arch_timer_mmio`에 그대로 둔다.
   - 정상 배포 FVP의 실행 기준은 physical 125MHz, `CNTINCR=0`, FVP default
     실효 increment 1, visible count 125MHz이다. `CNTINCR=8`의 1GHz 결과는
     debugger 강제 쓰기 대조군으로만 관리한다.

2. **RSE Local System Counter domain**
   - CSS counter와 독립된 state를 갖는다.
   - RSE의 모든 consumer가 같은 RSE QEMU instance 안에 있으므로 기존 QEMU
     `sse-counter`와 `sse-timer`를 우선 재사용한다.
   - Local System Counter 하나가 `TIMER0`~`TIMER3`에 `CNTVALUEB`를 공급한다.
   - 현재 FVP가 RSE timer를 CSS counter에 alias하는 동작은 model simplification
     이다. 첫 구현에는 `fvp_compat` mode를 넣지 않고 expected FVP deviation으로
     관리한다.

Cross-chip timer synchronization block은 count source가 아니다. single-chip CFG2
완료 gate에서는 기존 identification/register surface만 보존하고, request/ack 및
multi-chip synchronization state machine은 후속 fidelity 항목으로 남긴다.

## 2. 성공 조건

다음 조건을 모두 만족해야 이 계획을 완료로 판정한다.

1. 동일한 frozen simulation timestamp에서 다음 CSS view의 64-bit count가 정확히
   같다.

   ```text
   SMD.CNTCV
     == AP.CNTPCT_EL0
     == AP_MMIO_NS.CNTPCT
     == AP_MMIO_S.CNTPCT
     == SI0.CNTPCT_EL0
     == SI0_CNTBase.PCT
     == SI1.CNTPCT_EL0
   ```

2. 반복 read 횟수와 순서가 counter 값에 영향을 주지 않는다.
3. 알려진 simulation interval에서 count delta가 확정된 REFCLK/increment 계약과
   정확히 일치한다.
4. AP/SI CPU timer는 core별 PPI를 유지하고, AP MMIO frame 0/1은 count만
   공유하면서 compare/control/IRQ state는 독립적으로 유지한다.
5. provider의 enable, halt, CNTCV, rate 또는 scaling 변경 후 모든 pending
   deadline이 즉시 다시 계산된다. count 값만 맞고 interrupt 시점이 틀리면
   실패이다.
6. external provider를 사용하지 않는 QEMU machine과 QBox platform의 기존 timer
   동작은 변경되지 않는다.
7. RSE `TIMER0`~`TIMER3`은 RSE local count를 공유하고 CSS write/reset과
   독립적이다.
8. RSE timer IRQ는 `TIMER0=3`, `TIMER1=4`, `TIMER2=5`, `TIMER3=27`로 RSE
   NVIC에 연결된다. `39~42`는 timer IRQ가 아니므로 사용하지 않는다
   (`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:1522-1558`,
   `trusted-firmware-m/.../device/include/platform_irq.h:33-58`).
9. 모든 RSE timer/LSC가 PD_AON 소속임을 유지하면서 `TIMER0`~`TIMER2`와
   `TIMER3`/Local System Counter의 reset target을 분리한다. SYS_RSS 반복 reset은
   unit/runtime에서 검증하고, 실제 `nWARMRESETAON` source는 확인 전까지 임의
   신호에 연결하지 않는다.
10. live CL0+CL1 QBox full-system boot, coverage audit와 FVP differential evidence가
    모두 같은 source revision에 연결된다.

Sequential live guest read의 raw 값이 같아야 한다고 요구하지 않는다. 정확한
동일성은 한 timestamp에서 simulation을 정지하거나 zero-delay snapshot으로
수집할 때만 판정하고, 실행 중 표본은 epoch와 elapsed time으로 정규화한다.

## 3. 현재 구조와 변경 이유

### 3.1 현재 CSS counter가 분리되어 있음

- `host_gtimer`는 instance마다 private `m_counter`를 갖고 low word read 시
  `counter_increment`를 더한다
  (`qbox-platform/systemc-components/host_gtimer/include/host_gtimer.h:39-40`,
  `:120-151`).
- SMD control/read/sync는 서로 다른 세 `host_gtimer` instance이다
  (`platforms/apollo/hw-block/system_mgmt.lua:407-438`).
- SI0 control/base도 별도 instance이며 CNTBase는 125MHz와 read당 4096 증가를
  설정한다(`platforms/apollo/hw-block/si_cl0.lua:623-646`).
- AP MMIO timer는 자체 QEMU virtual-clock counter를 125MHz로 계산한다
  (`platforms/apollo/hw-block/ap_compute.lua:453-474`).
- AP 및 SI0 CPU는 counter provider를 지정하지 않고, SI1 CPU만 별도 100MHz를
  지정한다(`ap_compute.lua:587-625`, `si_cl0.lua:1056-1097`,
  `si_cl1.lua:91-95,299-329`).

따라서 address가 맞더라도 같은 physical count state를 공유하지 않는다. 현재
`host_gtimer-tests`도 read-side increment를 정상 동작으로 검증하므로 새 계약으로
교체해야 한다(`tests/components/host_gtimer/host_gtimer-tests.cc:79-143`).

### 3.2 QEMU는 count뿐 아니라 deadline도 자체 계산함

QEMU `ARMCPU`는 `gt_get_countervalue()`에서 virtual clock으로 count를 계산하고,
`gt_recalc_timer()`와 WFIT에서 counter tick을 QEMU deadline으로 변환한다
(`target/arm/helper.c:1348-1353,1475-1534`,
`target/arm/tcg/op_helper.c:425-465`). AP MMIO timer도 별도 count/deadline 계산을
수행한다(`hw/timer/arm_arch_timer_mmio.c:17-49`).

그러므로 `CNTPCT` read callback만 바꾸는 방식은 올바르지 않다. provider ABI는
현재 count, count-to-deadline 변환과 state-change notification을 모두 제공해야
한다.

### 3.3 현재 RSE timer consumer가 없음

RSE Lua에는 `0x5015A000` control과 `0x5015B000` read stub만 있고
`TIMER0`~`TIMER3` device가 없다(`platforms/apollo/hw-block/rse.lua:433-453`).
반면 하드웨어는 별도 Local System Counter가 네 timer에 `CNTVALUEB`를 공급한다고
명시한다(`09-programmers-model-for-zena-css.md:15014-15043`).

RSE timer의 source-backed map은 다음과 같다.

| Block | Secure address | Non-secure address | NVIC IRQ | Reset |
| --- | ---: | ---: | ---: | --- |
| `TIMER0` | `0x58000000` | `0x48000000` | 3 | `nWARMRESETSYS_RSS` |
| `TIMER1` | `0x58001000` | `0x48001000` | 4 | `nWARMRESETSYS_RSS` |
| `TIMER2` | `0x58002000` | `0x48002000` | 5 | `nWARMRESETSYS_RSS` |
| `TIMER3` | `0x58003000` | `0x48003000` | 27 | `nWARMRESETAON` |
| LSC control | `0x5015A000` | 미노출(guide 충돌) | 해당 없음 | `nWARMRESETAON` |
| LSC read | `0x5015B000` | 미노출(guide 충돌) | 해당 없음 | `nWARMRESETAON` |

Timer address는 TF-M
`platform/ext/target/arm/rse/common/partition/platform_base_address.h:65-68,131-134`,
IRQ는 `device/include/platform_irq.h:38-40,58`과 Zena guide
`:1528-1544`가 근거이다. Local System Counter의 non-secure 설명은 guide
`:15023`, `:15029`, `:15041` 사이에 충돌이 있으므로 owner 해결 전에는 추정 alias를
노출하지 않는다.

## 4. 목표 topology

```text
                         SystemC simulation time
                                  |
                      +-----------+-----------+
                      |                       |
              CSS REFCLK domain          RSE local domain
                      |                       |
          QBox arm_system_counter      RSE QEMU Clock source
          one coherent count state              |
          125MHz / effective 1            QEMU sse-counter
                      |                       |
          +-----------+----------+      +-----+-----+-----+-----+
          |           |          |      |     |     |     |     |
       SMD/SI0     AP proxy    SI proxies   TIMER0 TIMER1 TIMER2 TIMER3
       MMIO views     |         |    |      IRQ3  IRQ4  IRQ5  IRQ27
                      |         |    |
                  AP QEMU     SI0  SI1 QEMU
                 /       \      \    \
          ARMCPU timers  AP MMIO   ARMCPU timers
            per-core PPI  frame0/1  per-core PPI
                          SPI49/48

Cross-chip sync: independent request/ack block, not a count provider
```

QOM object link는 서로 다른 QEMU DSO 사이를 연결할 수 없다. 따라서 AP, SI0,
SI1 각 QEMU instance 안에 proxy object를 하나씩 생성하되, proxy의 host callback
opaque가 동일한 QBox `arm_system_counter`를 가리키게 한다. RSE는 이 CSS proxy를
사용하지 않는다.

## 5. 상세 설계 계약

### 5.1 QBox CSS counter provider

QBox core에 `systemc-components/arm_system_counter/`를 추가한다. 이 module은
MMIO register를 직접 소유하지 않고 physical counter state와 consumer API만
제공한다.

최소 state는 다음과 같다.

- `anchor_count`
- `anchor_time_ns`
- `input_tick_remainder` 또는 동일한 source-clock phase state
- scaling을 사용할 때의 24-bit fractional count accumulator
- `input_frequency_hz`
- `integer_increment` 또는 architected fixed-point scale
- `enabled`
- `halt_on_debug`와 실제 debug-halted input
- software-visible `cntfid_hz`
- state-change `generation`

read는 side effect 없이 anchor로부터 계산한다. 물리 REFCLK edge마다 increment가
적용되는 계약이면 다음 정수식을 사용한다.

```text
input_ticks = floor((now_ns - anchor_time_ns) * input_frequency_hz / 1e9)
count(now)  = anchor_count + input_ticks * integer_increment
```

P0 executed contract에 따라 production FVP-comparison 기본값은
`input_frequency_hz=125MHz`, `integer_increment=1`이다. `125MHz/8`은 provider의
일반적인 rate 제어 unit test와 강제 `CNTINCR=8` control에는 사용할 수 있지만
정상 Apollo boot 기본값으로 사용하지 않는다. 별도의 ad-hoc mode를 만들지 않고
하나의 rational counter 계약으로 표현한다. 중간 곱은 overflow-safe integer
연산을 사용하며 floating point를 사용하지 않는다. 실제 구현은 위 요약식에 더해
`input_tick_remainder`를 다음 anchor로 넘겨야 한다. 임의 시점의 enable/halt/rate
write가 REFCLK edge phase를 다시 시작하면 안 된다. 8.24 scale을 지원하는 경우에는
visible 64-bit count 아래의 24-bit fractional accumulator도 보존하고 deadline
역변환에 같은 remainder를 사용한다.

physical input frequency, integer increment, enable/halt 또는 architected scale이
바뀌는 절차는 다음과 같이 고정한다.

1. write의 effective timestamp에서 기존 count를 materialize한다.
2. 그 값과 timestamp를 새 anchor로 만든다.
3. 새 control/rate 값을 적용한다.
4. generation을 증가시킨다.
5. provider lock을 해제한 후 consumer에 변경을 통지한다.

`CNTFID`/CPU `CNTFRQ` 같은 reported-frequency metadata write는 physical rate를
바꾸지 않으며 counter re-anchor나 deadline notification을 발생시키지 않는다.
CNTSCR/scaling register는 programmer model의 enable/CNTID override 조건을
검사하고, 허용되지 않은 running-state write를 임의로 적용하지 않는다. register
frontend test에서 physical clock change, reported-frequency write와 scale write를
서로 다른 case로 고정한다.

provider API는 최소 다음 의미를 제공한다.

- `count_at(absolute_ns)`
- `deadline_ns(target_count, from_ns)`; disabled/halted/unrepresentable이면 없음
- immutable state snapshot과 nominal/reported frequency
- observer 등록/해제
- re-anchoring mutation
- physical reset input

QEMU thread에서 이 API를 호출할 때 SystemC kernel API를 호출하면 안 된다.
provider는 absolute nanoseconds와 lock-protected immutable snapshot만 사용한다.
observer callback은 provider mutex를 잡은 상태에서 호출하지 않는다.

deadline은 provider state가 다음에 바뀌지 않는다는 전제에서 `from_ns` 이후
visible unsigned count가 target과 같거나 처음 넘어서는 absolute time이다.
현재 comparator condition이 이미 true이면 `from_ns`를 반환한다. increment가
8처럼 1보다 커 target을 정확히 밟지 못하면 첫 crossing edge를 ceiling division으로
선택한다. 64-bit wrap 이전에 표현할 수 없는 target, disabled/halted state 또는
QEMU signed-nanosecond 범위를 넘는 결과는 deadline 없음으로 반환한다. CPU
virtualization offset과 unsigned wrap condition은 기존 `gt_recalc_timer()`가 먼저
계산하며 provider에 모호한 modulo target을 넘기지 않는다. unit test는 exact-hit,
skipped target, already-due, wrap-boundary와 8.24 fractional case를 모두 포함한다.

### 5.2 Zena MMIO frame frontend

Zena-specific register layout은 QBox Platform의 `host_gtimer`에 남긴다. 다만 각
control/read/SI frame은 private counter를 제거하고 Lua constructor object
reference로 같은 `arm_system_counter` interface를 받아야 한다.

- control/read frame은 같은 provider state를 사용한다.
- architected 32-bit register access, alignment, byte-enable 및 streaming-width
  규칙을 명시적으로 검사한다.
- PCT low/high read는 각각 해당 effective timestamp를 sample하고 state를
  변경하지 않는다. software의 high-low-high retry가 rollover coherence 계약이다.
- CNTCV half write는 write timestamp의 full count에서 선택한 half만 교체하고
  re-anchor한다.
- `transport_dbg` read는 side effect가 없어야 하고 debug write 정책은 명시적으로
  제한한다.
- DMI는 제공하지 않는다.

QEMU initiator가 전달하는 TLM delay는 local virtual time이다
(`qbox/qemu-components/common/include/ports/initiator.h:659-668`). Future-dated
mutation을 현재 SystemC time에 즉시 적용하면 다른 QEMU instance가 미래 state를
보게 된다. 반대로 writer가 annotated delay만 소비하는 것으로도 충분하지 않다.
다른 QEMU instance가 temporal-decoupling quantum 안에서 mutation effective time을
이미 지나 실행했다면 notification으로 deadline을 다시 계산해도 guest side effect를
rollback할 수 없기 때문이다.

초기 정확성 구현은 shared-counter consumer를 위한 conservative synchronization
contract를 사용한다.

1. CSS provider에 연결된 각 `QemuInstance`는 local virtual-time frontier를 공통
   coordinator에 등록한다.
2. counter가 write/reset/rate-change 가능한 동안 participant는 global committed
   SystemC time을 넘어 실행하지 않는 zero-lookahead mode를 사용한다.
3. state-changing frontend는 annotated delay를 소비한 뒤 모든 participant가 해당
   effective time을 지나지 않았음을 rendezvous에서 확인하고 나서 anchor를
   변경한다. 이미 지난 instance가 있으면 근사 적용하지 않고 assertion/evidence
   failure로 중단한다.
4. timestamp-ordered PEQ는 barrier를 통과한 동시 mutation의 순서를 정하는 용도로만
   사용한다. 이미 앞서 실행한 QEMU의 rollback 대체물로 사용하지 않는다.
5. 모든 control frontend와 physical reset/rate input이 architecturally immutable한
   phase에서만 일반 temporal decoupling을 다시 허용한다. 향후 non-zero lookahead는
   scheduler가 rollback 없이 안전한 horizon을 증명할 때 별도 최적화한다.

이 rendezvous가 현재 `runonsysc` SC_THREAD 및 QemuInstance scheduler에서 안전한지
multi-instance test로 먼저 검증한다. 단순히 `sc_time_stamp()`를 읽거나 writer 한
instance만 동기화하는 구현은 허용하지 않는다.

현재 sync frame은 CSS provider에 포함하지 않는다. single-chip 단계에서는 기존
ID/register 동작만 별도 state로 유지한다. 향후 cross-chip request/ack 구현도
counter state와 분리한다.

### 5.3 QEMU external counter provider

QEMU에 Apollo 전용 global callback을 넣지 않는다. nullable QOM link로 선택하는
재사용 가능한 Arm Generic Timer counter-provider interface를 추가한다. 제안
경로는 다음과 같다.

- `include/hw/timer/arm_generic_timer_counter.h`
- `hw/timer/arm_generic_timer_counter.c`
- `hw/timer/meson.build`

interface operation은 다음 의미를 갖는다.

- 주어진 absolute `QEMU_CLOCK_VIRTUAL` nanoseconds의 count
- target count에 도달하는 absolute QEMU virtual-clock nanoseconds
- enabled/halted 및 nominal frequency snapshot
- consumer register/unregister
- provider 변경 notification

external provider link가 없으면 현재 QEMU clock 기반 경로를 그대로 사용한다.
link가 있으면 다음 consumer만 provider를 사용한다.

1. `ARMCPU`
   - `gt_get_countervalue()`의 source를 provider로 바꾼다.
   - `gt_recalc_timer()`와 WFIT는 provider가 반환한 absolute deadline을
     `timer_mod_ns()`에 사용한다.
   - provider notification 시 모든 enabled Generic Timer와 WFIT deadline을
     다시 계산하고 IRQ/PPI 상태를 갱신한다.
   - CPU register, comparator, virtualization offset, mask, ISTATUS와 PPI 출력은
     기존 QEMU code에 남긴다.

2. `arm_arch_timer_mmio`
   - frame별 register/CVAL/control/ISTATUS와 IRQ state는 유지한다.
   - count와 count-to-deadline만 provider에 위임한다.
   - provider notification 시 frame별 timer를 다시 arm/cancel하고 IRQ를
     재평가한다.

provider의 reported frequency와 CPU `cntfrq`, MMIO `cntfrq`가 executed 125MHz contract와
다르면 realization 단계에서 fail-fast한다. null provider의 기존 default와
migration format은 바꾸지 않는다. external provider mode에서는 counter state를
QEMU VMState에 중복 저장하지 않으며, migration/post-load 정책이 구현될 때까지
해당 mode의 migration을 명시적으로 비지원 처리한다.

CPU timer output은 domain별 hardware interrupt matrix를 그대로 보존한다. 단순히
현재 wrapper의 네 output index를 기존 PPI에 다시 연결하는 것으로 완료 처리하지
않는다.

| Domain | Architected timer output | PPI | 구현 원칙 |
| --- | --- | ---: | --- |
| AP | Secure EL2 virtual `CNTHVS` | 19 | PE 기능과 사용 여부를 P0에서 확인한 뒤 정확한 QEMU output을 노출 |
| AP | Secure EL2 physical `CNTHPS` | 20 | 위와 동일 |
| AP | Non-secure EL2 physical `CNTHP` | 26 | 기존 hypervisor physical output 유지 |
| AP | virtual `CNTV` | 27 | 기존 virtual output 유지 |
| AP | EL2 virtual `CNTHV` | 28 | wrapper에 누락된 output 추가 |
| AP | secure physical `CNTPS` | 29 | 기존 secure physical output 유지 |
| AP | non-secure physical `CNTPNS` | 30 | 기존 physical output 유지 |
| SI0 | Secure EL2 physical `CNTHPS` | 20 | CL0 hardware matrix의 세 timer output 중 하나 |
| SI0 | virtual `CNTV` | 27 | CL0 hardware matrix의 세 timer output 중 하나 |
| SI0 | secure physical `CNTPS` | 29 | CL0 hardware matrix의 세 timer output 중 하나 |

AP matrix는 Zena guide table 9-33
(`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:1331-1348`),
SI0 matrix는 table 9-38(`:1644-1656`)이 근거이다. 현재 A720AE wrapper는 QEMU
output index 0~3만 노출해 AP PPI 19/20/28을 표현하지 못하고, SI0 Lua는 generic
physical output을 PPI 20, hypervisor output을 PPI 19에 연결한다. 이는 timer class를
혼동할 수 있으므로 QEMU output의 architected identity부터 확인해 wrapper를
확장한다. CFG2 SI1은 FVP 전용이고 같은 hardware table이 없으므로 SI0 matrix를
복사하지 않는다. Iris target/output 및 FVP GIC 상태로 별도 matrix를 P0에서
확정한다.

### 5.4 libqemu 및 QBox per-instance bridge

QEMU provider proxy의 callback 등록/해제와 change notification을
`libqemu/wrappers/target/arm.{h,c}` 및 `libqemu/exports.py`에 노출한다. 현재
`libqemu_init()`은 크기나 version 정보 없이 library 내부 `LibQemuExports *`를
반환하므로, 기존 struct 뒤에 field를 붙이고 null을 검사하는 방식은 ABI-safe하지
않다(`libqemu/libqemu.h:50-56`, `libqemu/libqemu.c:170-178`).

따라서 기존 `libqemu_init`은 legacy consumer용으로 보존하고 새
`libqemu_init_v2(argc, argv, requested_abi, caller_struct_size, &actual_size)` symbol을
추가한다. v2 caller는 symbol 존재를 먼저 확인하고, ABI version과 반환된 struct
size가 필요한 마지막 field까지 포함하는지 확인한 뒤에만 export를 읽는다.
`libqemu.version`에도 새 symbol을 명시한다. external provider mode는 v2 API를
필수로 하며, 오래된 system libqemu에서는 struct를 추측해 읽지 않고 QEMU 시작
전에 명확히 실패한다. QBox와 QEMU를 항상 같은 source revision으로 빌드하는
lockstep 방식도 허용하지만, system libqemu 경로에서는 v2 negotiation을 생략하지
않는다.

QBox core에
`qemu-components/timer/qemu_arm_generic_timer_counter_bridge/`를 추가한다. 각
bridge는 하나의 `QemuInstance`와 하나의 `arm_system_counter`를 constructor
argument로 받는다.

필수 threading/lifecycle 규칙은 다음과 같다.

- QEMU read/deadline callback은 그 instance의 `qemu_ns`를 provider에 전달한다.
  QEMU thread에서 `sc_time_stamp()`를 읽지 않는다.
- 최초 synchronization point에서 QEMU virtual-clock epoch와 SystemC absolute
  time의 대응을 assert한다. 차이가 있으면 bridge가 검증된 per-instance offset을
  적용하며 암묵적으로 0이라고 가정하지 않는다.
- provider mutation notification은 generation별로 coalesce한다.
- provider lock을 해제한 뒤 instance별 cancellable iothread executor를 사용하고,
  한 번에 하나의 QEMU BQL만 잡아 provider proxy의 consumer notification을
  실행한다. bridge를 임의의 CPU0 lifetime에 결합하지 않도록 libqemu/QBox
  `QemuInstance`에 generic enqueue/drain API를 추가한다.
- 두 QEMU instance의 BQL을 동시에 잡지 않는다.
- callback 실행 중 counter reset/write가 발생해도 lock inversion이 없어야 한다.
- teardown 순서는 observer 해제, pending job drain/cancel, QEMU callback clear,
  proxy destroy이다. pending job이 raw dangling `this`를 참조하면 안 된다.
- QEMU `Clock` 생성/입력 연결과 QOM device reset은 QEMU 내부 API로 수행한다.
  QBox가 QEMU private struct를 조작하지 않도록 versioned libqemu export와 RAII
  wrapper를 함께 제공한다.

AP, SI0, SI1 CPU wrapper와 AP MMIO wrapper는 동일 QEMU instance의 proxy object를
두 번째 constructor argument로 받아 QOM link를 설정한다. 현재 one-argument
constructor는 non-Apollo/legacy config를 위해 유지한다.

### 5.5 RSE Local System Counter와 timer

RSE는 cross-instance 공유가 필요 없으므로 QEMU의 검증된 `sse-counter`와
`sse-timer`를 직접 사용한다. 이 모델은 clock-driven count, tick-to-time,
consumer notification과 deadline 재계산 구조를 이미 갖는다
(`include/hw/timer/sse-counter.h:63-103`,
`hw/timer/sse-timer.c:136-187,387-424`).

구현 전에 Corstone SSE register map과 Zena/Ma1 RSE LSC 및 Timestamp Timer
register map의 offset, reset value, scaling, access size와 interrupt semantics를
표로 비교한다. 차이가 있으면 QEMU model을 재사용 가능한 방식으로 확장하며,
register-only SystemC stub으로 되돌아가지 않는다.

QBox core에는 다음 wrapper가 필요하다.

- `qemu_clock_source`: QEMU `Clock` 생성, frequency 설정과 input 연결
- `qemu_sse_counter`: control/read 두 MMIO region 노출
- `qemu_sse_timer`: counter QOM link, 한 MMIO region과 한 IRQ 노출

이 object들은 outer AP QEMU가 아니라 `rse_cpu_pass` 내부의 active RSE
`QemuInstance`에 생성한다(`platforms/apollo/hw-block/rse.lua:611-683,763-806`).
Secure/Non-secure timer address는 같은 QEMU device backing을 QBox router를 통해
alias하고, timer state를 두 벌 만들지 않는다. 현재 `rse_protection_ctrl`은 PPC
register bank이지 downstream transaction을 차단하는 bus filter가 아니다. 따라서
QBox Platform에 Apollo 전용 `rse_ppc_filter`를 추가해
`RequestContextTlmExtension`의 secure/privileged 속성과 PPC0 policy state를 실제
access path에서 검사한다. deny는 architected TLM error/fault로 반환하고 secure와
non-secure alias가 같은 backing device로 전달되는지 test한다. LSC도 PPC2 policy와
specific map 충돌을 P0에서 해결한 범위만 같은 방식으로 노출한다.

현재 `RequestContext` type에는 privileged field가 있지만 QEMU normalization은
secure만 설정하고, libqemu-cxx `MemTxAttrs`도 QEMU의 `user` bit를 버린다
(`systemc-components/common/include/tlm-extensions/request-context.h:65-75`,
`qemu-components/common/include/ports/initiator.h:706-720`). PPC filter보다 먼저
QBox core에서 QEMU `MemTxAttrs.user`를 libqemu-cxx에 보존하고 regular access의
`privileged = !user`, `privileged_valid = true`를 RequestContext에 설정한다. debug,
direct 및 DMI path의 privilege policy도 명시하고, policy가 필요한데 valid bit가
없으면 filter가 fail-closed한다. secure/privileged 네 조합이 실제 filter까지
전달되는지 core unit test로 고정한다.

reset은 QEMU instance 전체 reset에 묶지 않는다. wrapper별 reset input을 제공해
`TIMER0`~`TIMER2`는 `nWARMRESETSYS_RSS`, `TIMER3`과 Local System Counter는
`nWARMRESETAON` equivalent fanout에 연결한다. 모든 timer와 LSC는 PD_AON 소속을
유지한다(`09-programmers-model-for-zena-css.md:14940-14948,15027-15043`).

현재 Apollo system-reset fanout에는 `rse_cpu_pass.qemu_inst.reset`이 포함되어
QEMU instance의 모든 device를 함께 reset한다(`config.lua:99-123`). 이 연결을
그대로 둔 채 wrapper reset만 추가하면 reset source가 분리되지 않는다. P4의
구체적인 교체 topology는 다음과 같다.

1. system reset target에서 `&rse_cpu_pass.qemu_inst.reset`을 제거한다.
2. CPU는 기존 `&rse_cpu_pass.cpu_0.cpu.reset` signal로 실제 Cortex-M55 reset을
   수행한다. 현재 `cpu_0.accel_reset`은 accelerator runtime state만 지우므로 CPU
   reset 대체물이 아니다(`rse-cpu/src/apollo_rse_cpu.h:50-53`).
3. NVIC, optional QEMU pflash와 새 `TIMER0`~`TIMER2`는 versioned libqemu의
   per-device reset API를 감싼 signal wrapper로 system reset에 연결한다.
4. `TIMER3`과 LSC는 system reset에 연결하지 않고 별도의 AON/cold-reset fanout에
   연결한다. 해당 platform input의 정확한 source는 P0 reset decision record에서
   확정한다.
5. whole-instance reset은 모든 AON state도 지워야 하는 cold/power-on 경로에서만
   허용한다. reset 뒤 LSC/TIMER3 state를 software로 복원하는 방식은 허용하지
   않는다.

또한 현재 `sse_counter_reset()`은 새 state 설치 후 consumer notifier를 호출하지
않는다(`hw/timer/sse-counter.c:376-386`). LSC reset 뒤 `TIMER0`~`TIMER3`가 stale
deadline을 유지하지 않도록 reset 완료 후 notify/rearm하고, consumer unregister
경로도 추가해 qtest로 고정한다.

## 6. P0 선결 결정

### 6.1 CSS frequency contract

정상 배포 FVP에서 확정된 executed contract는 physical REFCLK 125MHz,
`CNTINCR=0`, FVP default 실효 increment 1, visible count 125MHz이다. exact delta는
1THz simulation tick `1,030,743,023` 동안 `128,842` count로, 125MHz 기대값의
정확한 floor와 같다. debugger로 `CNTINCR=8`을 강제한 대조군에서만 정확히
1GHz가 측정됐다.

SCP source는 `SYSCNT_INCR=8`을 의도하지만 배포 AArch64 ELF는 32-bit impdef
register에 `str x5` 64-bit store를 수행하고 FVP가 이 malformed write를 WI로
처리한다. 이후 같은 init 함수의 `CNTFID0=125MHz`와 `CNTCR=0x101` write는 정상
반영되어 init 미실행이나 별도 alias로 설명할 수 없다. component source는 이
계획에서 변경하지 않는다.

다음 값의 정상 boot 동시 snapshot은 완료됐다.

- `CNTCR`, `CNTINCR`, `CNTFID0`
- known simulation interval의 SMD CNTCV delta
- 모든 AP CPU의 `CNTFRQ_EL0`, `CNTPCT_EL0`
- AP MMIO non-secure frame 0 `CNTFRQ`, `CNTPCT`; secure frame 1은
  `CNTACR1=0`에서 RAZ이고 `0x3f` 대조군에서 같은 count/125MHz
- SI0/SI1 `CNTFRQ_EL0`, `CNTPCT_EL0`
- firmware delay/timeout marker

기존 실행기는 `scripts/debug/run_local_fvp_debug.sh`이고 breakpoint/stop 기능은
이미 있다. 이 helper의 `--no-attach` 경로는 reset 상태에서 halt된 Iris server를
시작하므로, 단순 attach 직후 register를 읽어서는 boot-time contract가 되지 않는다.
구조화 snapshot helper와 raw 결과는 구현되어
`build/qbox-apollo-qvp/timer-validation/20260722-085755/fvp/`에 보존돼 있다.
`p0-decision-record.md`가 배포 artifact hash, marker, raw register, simulation time,
delta와 forced-increment control을 연결한다. 구체적 사용 절차는
`doc/fvp-iris-debugging-guide-ko.md`를 따른다.

최종 contract는 `input_frequency_hz`, `integer_increment`, `visible_delta_hz`,
`cntfid_hz`, CPU/MMIO reported frequency를 서로 다른 필드로 기록한다. component
source 변경이 필요한 결론이 나오면 이 timer/QBox 작업 안에서 임의로 수정하지
않는다. 다만 보고만 하고 production integration을 계속 진행하지도 않는다.
generic P1/P2 작업은 측정된 125MHz baseline으로 진행할 수 있다. 그러나 source와
executed behavior가 불일치한다. 사용자 결정에 따라 component를 수정하지 않고
정상 배포 FVP의 executed 125MHz 계약을 Apollo QBox 기준으로 채택했다. source의
64-bit malformed write는 별도 component debt로 기록하되 P3/P5를 차단하지 않는다.

### 6.2 RSE frequency, reset 및 access contract

TF-M의 32MHz는 현재 software default이지 Zena integration clock의 증명이 아니다
(`trusted-firmware-m/.../device/config/device_cfg.h:75-95`). 현재 FVP의 125MHz는
CSS alias이므로 RSE hardware rate 근거로 사용하지 않는다. RSE LSC rate는 Ma1
integration 자료 또는 hardware owner 결정으로 확정한 후 하나의 QEMU Clock에
적용한다.

추가로 다음을 P0 decision record에 포함한다.

- CSS physical counter reset source; AP/SI/QEMU reset에서 임의로 추론하지 않음
- RSE LSC의 secure/non-secure map과 PPC2 정책
- RSE `TIMER0`~`TIMER3` PPC0 privileged/security policy
- SSE model과 Ma1 register compatibility 결과

RSE timer/LSC는 모두 PD_AON이며 `TIMER0`~`TIMER2`는
`nWARMRESETSYS_RSS`, `TIMER3`/LSC는 `nWARMRESETAON`이라는 문서 계약을 확인했다.
구현은 secure LSC window, secure/non-secure TIMER alias, PPC0/PPC2 enforcement와
SYS_RSS/AON reset target split을 적용했다. 실제 LSC rate 자료가 없으므로 input은
override 가능한 125MHz provisional default를 사용하고 guest의 32MHz `CNTFRQ`는
reported metadata로 유지한다. 정확한 `nWARMRESETAON` platform source 연결은
후속 hardware-signoff debt다.

## 7. Repository별 변경 목록

### 7.1 `hsoc-stack/tools/qemu`

| 파일/영역 | 변경 |
| --- | --- |
| `include/hw/timer/arm_generic_timer_counter.h` | nullable provider interface와 consumer contract 추가 |
| `hw/timer/arm_generic_timer_counter.c` | proxy/provider 공통 helper와 notification 구현 |
| `hw/timer/meson.build` | 새 generic timer source 등록 |
| `target/arm/cpu.h`, `cpu.c` | optional provider link, notifier lifecycle, timer initialization 검증 |
| `target/arm/helper.c` | count와 Generic Timer deadline provider 경로 추가 |
| `target/arm/tcg/op_helper.c` | WFIT deadline provider 경로 추가 |
| `include/hw/timer/arm_arch_timer_mmio.h`, `hw/timer/arm_arch_timer_mmio.c` | frame state는 유지하고 optional counter source/deadline 연결 |
| `libqemu/wrappers/target/arm.{h,c}` | proxy callback 등록/해제/notify export |
| `libqemu/libqemu.{h,c}`, `libqemu/libqemu.version` | size/version-negotiated `libqemu_init_v2` 추가, legacy init 보존 |
| `libqemu/exports.py` | v2 export table에 timer/clock/reset API 생성 |
| `libqemu/wrappers/timer.{h,c}` 또는 신규 clock wrapper | QEMU-owned `Clock` 생성, frequency와 input 연결 API |
| `libqemu/wrappers/qdev.{h,c}` | QOM device 단위 reset API |
| libqemu iothread job helper | CPU에 종속되지 않는 cancellable enqueue/drain API |
| `tests/qtest/arm-arch-timer-mmio-test.c` | external count, frame 독립성, notification/deadline test 추가 |
| 신규/기존 Arm CPU qtest | CPU counter, PPI, WFIT와 legacy fallback test |

QEMU 변경은 Apollo address나 IRQ 숫자를 포함하지 않는다. 모든 platform-specific
값은 QBox Platform Lua에 남긴다.

### 7.2 `hsoc-stack/tools/qbox`

| 파일/영역 | 변경 |
| --- | --- |
| `systemc-components/arm_system_counter/` | anchored shared counter, observer와 reset API |
| `systemc-components/CMakeLists.txt` | component 등록 |
| `tests/components/arm-system-counter/` | time, rate, mutation, rollover, reset, concurrency unit test |
| `qemu-components/timer/qemu_arm_generic_timer_counter_bridge/` | QemuInstance별 SystemC↔libqemu bridge |
| `qemu-components/timer/qemu_arm_arch_timer_mmio/` | optional proxy constructor/link 지원 |
| `qemu-components/timer/qemu_clock_source/` | RSE counter용 QEMU Clock wrapper |
| `qemu-components/timer/qemu_sse_counter/` | RSE LSC control/read wrapper |
| `qemu-components/timer/qemu_sse_timer/` | RSE timestamp timer/IRQ wrapper |
| `qemu-components/common/src/libqemu-cxx/` | v2 ABI negotiation, clock/device-reset와 callback lifetime RAII wrapper |
| `systemc-components/common/include/tlm-extensions/request-context.h` | secure와 privileged QEMU attrs normalization |
| `qemu-components/common/include/ports/initiator.h` | `MemTxAttrs.user`를 RequestContext privilege로 전달 |
| libqemu-cxx memory attrs/test | QEMU `user` bit 보존 및 secure/privileged 조합 검증 |
| `qemu-components/common/include/qemu-instance.h` | instance-owned iothread executor와 drain lifecycle |
| 관련 CMake/test | bridge, multi-instance, reset/teardown test 등록 |

### 7.3 `hsoc-stack/tools/qbox-platform`

| 파일/영역 | 변경 |
| --- | --- |
| `systemc-components/host_gtimer/` | private counter 제거, Zena frame frontend로 전환 |
| `systemc-components/rse_ppc_filter/` | RequestContext 기반 PPC0/PPC2 access enforcement |
| `tests/components/host_gtimer/` | read-side increment 기대를 제거하고 shared/time contract 검증 |
| `qemu-components/cpu_arm/cpu_arm_cortex_a720ae/` | optional provider link와 AP PPI 19/20/26/27/28/29/30 output |
| `qemu-components/cpu_arm/cpu_arm_cortex_r82/` | optional provider link와 domain별 architected timer output |
| `platforms/apollo/hw-block/system_mgmt.lua` | CSS provider와 SMD control/read view 연결 |
| `platforms/apollo/hw-block/ap_compute.lua` | AP proxy, CPU와 MMIO frame 연결 |
| `platforms/apollo/hw-block/si_cl0.lua` | SI0 proxy, CPU와 local frame 연결 |
| `platforms/apollo/hw-block/si_cl1.lua` | SI1 proxy와 CPU 연결; 100MHz 독립 island 제거 |
| `platforms/apollo/hw-block/rse.lua` | RSE LSC stub 교체, TIMER0~3/alias/IRQ/reset 연결 |
| `platforms/apollo/hw-block/config.lua` | source-backed RSE timer map/IRQ와 resolved frequency contract |
| Apollo platform tests/README | topology, runtime option과 fidelity deviation 문서화 |

`patch-qbox/`의 archived patch는 자동 적용하지 않는다.

### 7.4 Top-level repository

| 파일/영역 | 변경 |
| --- | --- |
| `scripts/debug/capture_fvp_timer_snapshot.py` | halted Iris snapshot을 정규화 JSON으로 저장 |
| `scripts/run/run_qbox_apollo_fvp_full.py` | 향후 `--timer-probe`와 구조화 timer/IRQ evidence 추가 |
| `scripts/test/validate_qbox_apollo_fvp_full_map.py` | CSS/RSE timer map, IRQ, forbidden alias와 ownership 검사 |
| `scripts/test/compare_qbox_fvp_timer_snapshots.py` | logical-point별 FVP/QBox differential report |
| `doc/` timer 문서 | 확정 frequency, reset, implementation/result 갱신 |
| top-level submodule pointers | nested repository commit을 순서대로 pin |

생성 evidence는 source가 아니며 다음 경로만 사용한다.

```text
build/qbox-apollo-qvp/timer-validation/<timestamp>/
  static/
  unit/
  qemu-qtest/
  integration/
  qbox-full/
  fvp/
  differential/
  coverage/
```

## 8. 단계별 실행 계획

### P0. Hardware/FVP contract 고정

상태: **완료, hardware 미확정값은 provisional contract로 격리**. CSS executed
contract, AP access control, AP/SI PPI, RSE map/IRQ/reset split과 SSE compatibility를
고정했다. RSE physical input rate와 AON reset source는 구현값과 hardware 확정값을
혼용하지 않도록 명시적인 debt로 남겼다.

작업:

- `TMR-000`: 현재 QBox/FVP baseline revision, active config와 artifact hash 기록
- `TMR-001`: 기존 Iris helper로 SCP timer 초기화 직후와 TF-A 진입 후 stop point
  정의
- `TMR-002`: FVP timer snapshot helper와 JSON schema 구현
- `TMR-003`: CSS frequency/reported-frequency contract 결정
- `TMR-004`: RSE rate, LSC access, CSS/RSE reset contract 결정
- `TMR-005`: SSE/Ma1 register compatibility matrix 작성
- `TMR-006`: AP, SI0와 FVP-only SI1의 architected timer-output/PPI matrix 확정

완료 gate:

- 같은 snapshot에 register 값과 simulation interval/delta가 모두 기록된다.
- `input_hz`, increment, visible rate와 reported frequency를 혼용하지 않는다.
- 미확정 값에는 owner와 차단되는 후속 phase가 명시된다.
- component source와 executed behavior가 다르면 선택한 production 계약과 남은
  component debt를 명시한다.
- component source는 변경되지 않는다.

### P1. QEMU provider와 consumer hook

상태: **완료**. nullable provider, CPU/MMIO/SSE consumer, deadline notification,
versioned libqemu ABI, QEMU Clock/reset/job API와 legacy fallback을 구현했다. strict
ARM/AArch64 build와 SSE 5/5, MMIO 9/9 qtest가 통과했다.

작업:

- `TMR-100`: generic counter-provider QOM interface와 host proxy 구현
- `TMR-101`: ARMCPU count/deadline/notification 경로 연결
- `TMR-102`: WFIT deadline 경로 연결
- `TMR-103`: AP MMIO timer count/deadline/notification 경로 연결
- `TMR-104`: size/version-negotiated `libqemu_init_v2`와 legacy init 공존 구현
- `TMR-105`: generic per-instance iothread enqueue/drain API 추가
- `TMR-106`: legacy null-provider 및 external-provider qtest 추가
- `TMR-107`: QEMU-owned Clock 연결과 per-device reset libqemu API 추가

완료 gate:

- provider가 없을 때 기존 QEMU qtest 결과가 변하지 않는다.
- provider count를 바꾸지 않고 read 수만 늘려도 값/IRQ 시점이 같다.
- enable/disable/CNTCV/rate notification 후 CPU, WFIT와 MMIO deadline이 모두
  재계산된다.
- AP MMIO frame 0/1 count는 같고 CVAL/control/ISTATUS/IRQ는 독립이다.

### P2. QBox shared provider와 per-instance bridge

상태: **single-chip production scope 완료**. `arm_system_counter`, instance별 bridge,
QEMU wrapper, iothread ordering과 `MemTxAttrs.user` propagation을 구현했다. QBox core
timer CTest 4/4와 세 QEMU instance의 runtime snapshot이 통과했다. simulation 시작
후 structural rate/scale 변경은 금지하므로 현재 Apollo 경로에는 future-dated
reanchor rendezvous가 필요하지 않으며, 일반화된 mutable rendezvous는 P6로 이동했다.

작업:

- `TMR-200`: `arm_system_counter` state, rational math와 observer 구현
- `TMR-201`: reset, halt, partial CNTCV write와 generation 구현
- `TMR-202`: input-tick phase/fractional accumulator와 deadline edge case 구현
- `TMR-203`: QEMU provider proxy의 libqemu-cxx wrapper 구현
- `TMR-204`: AP/SI instance별 bridge와 epoch alignment 구현
- `TMR-205`: deferred notification, BQL ordering과 teardown 구현
- `TMR-206`: 2개 이상 QEMU instance가 같은 provider를 사용하는 integration test
- `TMR-207`: Apollo structural rate/scale을 simulation 시작 후 immutable로 고정;
  일반 mutable cross-instance rendezvous는 P6로 이동
- `TMR-208`: `MemTxAttrs.user`를 privileged RequestContext로 보존하고 core test 추가

완료 gate:

- frozen time의 모든 bridge count가 정확히 같다.
- 각 QEMU raw observation은 bridge epoch로 변환한 SystemC time의 provider count와
  정확히 같다.
- simulation 시작 후 structural rate/scale 변경 시 fail-fast한다.
- provider lock 밖에서 notification을 enqueue하고 owning IOThread에서 drain한다.
- queued notification teardown unit test와 full-system 종료가 callback-after-free
  없이 통과한다. 별도 ASan/race stress는 P6 test debt다.

### P3. Apollo CSS topology 전환

상태: **완료**. 정상 FVP executed 125MHz 계약으로 SMD/AP/SI0/SI1을 하나의 CSS
provider에 연결하고, CPU PPI와 AP MMIO SPI/access reset값을 FVP 측정에 맞췄다.

작업:

- `TMR-300`: SMD control/read와 SI0 view를 하나의 provider에 연결
- `TMR-301`: AP, SI0, SI1 QEMU bridge instance 생성
- `TMR-302`: A720AE/R82 CPU를 optional provider에 연결
- `TMR-303`: AP MMIO secure/non-secure frame을 AP proxy에 연결
- `TMR-304`: independent SI1 100MHz island와 read-side `+4096` stub 제거
- `TMR-305`: sync frame이 counter provider로 오인되지 않도록 ownership 검사 추가
- `TMR-306`: AP/SI별 architected timer output을 wrapper에 노출하고 PPI matrix 교정

완료 gate:

- CSS same-timestamp invariant가 0 tick tolerance로 통과한다.
- AP는 사용 가능한 PPI 19/20/26/27/28/29/30, SI0은 PPI 20/27/29를 각
  architected timer class에 맞게 연결한다. SI1은 P0에서 확정한 FVP matrix를 따른다.
- AP MMIO non-secure frame 0은 SPI49, secure frame 1은 SPI48을 유지한다.
- AP/SI/QEMU reset이 CSS counter를 암묵적으로 reset하지 않는다.
- static validator에 별도 CSS counter instance를 추가하면 실패한다.

### P4. RSE local domain 구현

상태: **구현 및 scoped 검증 완료**. 독립 RSE LSC, TIMER0~3, S/NS alias,
PPC filter, IRQ 3/4/5/27과 SYS_RSS/AON reset target split을 구현했다. physical
LSC rate와 실제 AON reset source만 hardware-signoff debt로 남는다.

작업:

- `TMR-400`: QEMU Clock, SSE counter/timer QBox wrapper 구현
- `TMR-401`: RSE LSC control/read stub을 하나의 `sse-counter`로 교체
- `TMR-402`: `TIMER0`~`TIMER3`를 같은 counter에 QOM-link
- `TMR-403`: S/NS timer alias와 `rse_ppc_filter` PPC0 enforcement 연결
- `TMR-404`: LSC map에 `rse_ppc_filter` PPC2 enforcement 연결
- `TMR-405`: NVIC IRQ 3/4/5/27 연결
- `TMR-406`: RSE whole-instance system reset을 CPU/NVIC/pflash/timer별 reset으로 전환
- `TMR-407`: TIMER0~2 system reset과 TIMER3/LSC AON reset 분리
- `TMR-408`: LSC reset 후 counter consumer notify/rearm 구현
- `TMR-409`: CSS/RSE write-reset isolation과 PPC allow/deny test 추가

완료 gate:

- 네 timer PCT는 같은 frozen RSE timestamp에서 LSC와 같다.
- 각 timer의 compare/mask/ISTATUS/IRQ가 독립적으로 동작한다.
- TIMER0~2 reset은 TIMER3/LSC count/state를 바꾸지 않는다.
- system reset은 CPU/NVIC/optional pflash/TIMER0~2만 reset하고 QEMU instance 전체를
  reset하지 않는다.
- CSS reset/write는 RSE local state를 바꾸지 않는다.
- secure/non-secure alias는 같은 backing state를 공유하고 PPC deny가 실제 access
  error로 관측된다.

### P5. Local build와 full-system runtime

상태: **완료**. 같은 working tree에서 targeted build/test, live CL0+CL1 boot,
구조화 QBox/FVP snapshot, 44/44 differential과 coverage audit를 수집했다.

작업:

- `TMR-500`: QEMU/qbox/qbox-platform narrow test 실행
- `TMR-501`: `QBOX_USE_SYSTEM_LIBQEMU=OFF`와 `QBOX_LIBQEMU_BUILD_ALWAYS=ON`으로
  수정된 local QEMU 재빌드를 강제한 QBox unit build 실행
- `TMR-502`: live CL0+CL1 full-system QBox boot와 model-side timer probe 실행
- `TMR-503`: full coverage audit와 per-domain log 수집
- `TMR-504`: normal FVP boot 및 같은 logical point Iris snapshot 수집
- `TMR-505`: differential JSON과 expected RSE FVP-deviation 판정
- `TMR-506`: 필요 시 최종 `./yocto_build.sh` integration gate 실행

완료 gate:

- static/unit/qtest/integration/full boot/FVP/differential artifact가 한 evidence root에
  존재한다.
- full QBox run이 RSE, SI0, SI1, secure console, primary Linux gate를 모두 통과한다.
- runtime timer probe가 count뿐 아니라 deadline과 실제 IRQ identity를 확인한다.
- FVP의 RSE CSS alias는 expected deviation으로만 기록되고 hardware-correct QBox를
  실패로 처리하지 않는다.

### P6. 후속 fidelity

다음은 single-chip CFG2 timer topology 완료 후 별도 작업으로 남긴다.

- SMD cross-chip synchronization request/ack, threshold, delay와 failure state
- SI external `REFCLK_SSYSCLK_CNTBase0` alias
- migration/post-load 시 SystemC provider와 QEMU consumer 재동기화
- future-dated mutable reanchor의 일반 cross-instance rendezvous
- RSE LSC의 실제 hardware input frequency와 `nWARMRESETAON` source 연결
- full-system이 아닌 `apollo-pc.lua`/legacy primary-compute entrypoint의 동일 topology 전환
- 실제 요구가 생겼을 때만 명시적 RSE FVP-compatibility experiment

P6 항목이 미구현이라는 이유만으로 P0~P5의 single-chip 완료를 실패로 판정하지
않되 fidelity ledger에 남긴다.

## 9. 검증 ladder와 명령

각 단계는 좁은 test부터 실행하고 입력이 바뀐 경우에만 넓힌다.

### T0. Static

```bash
git -C hsoc-stack/tools/qemu diff --check
git -C hsoc-stack/tools/qbox diff --check
git -C hsoc-stack/tools/qbox-platform diff --check

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --out build/qbox-apollo-qvp/timer-validation/<id>/static/map.json
python3 scripts/test/audit_qbox_core_boundary.py
```

추가 validator는 다음을 실패로 처리한다.

- AP REFCLK에 `qemu_hexagon_qtimer`, `qct-qtimer` 또는 compatibility alias 사용
- CSS consumer별 별도 counter state 생성
- AP MMIO frame/IRQ 교환
- RSE timer IRQ를 39~42로 연결
- RSE LSC를 CSS provider에 기본 연결
- sync block을 count provider로 선언

### T1. QBox/SystemC unit

다음 명령으로 QBox/SystemC counter와 bridge를 검증했다.

```bash
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target arm_system_counter-tests host_gtimer-tests --parallel <jobs>

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R '^(arm_system_counter-tests|host_gtimer-tests)$' \
  --output-on-failure
```

필수 case:

- 125MHz/1 tick은 8ns마다 1 증가
- 125MHz/8 tick은 8ns마다 8 증가(강제/control 및 generic provider case이며
  production Apollo 기본값 아님)
- disable/freeze/re-enable continuity
- low/high partial write와 `0xffffffff` rollover
- high-low-high retry coherence
- sub-tick phase와 24-bit fractional accumulator 보존
- exact/skipped/already-due/wrap target의 ceiling deadline
- deadline 직전에는 미만, deadline에서는 target 이상
- reset-source/retention isolation과 observer unregister
- malformed TLM, DMI false와 debug read side-effect 없음

### T2. QEMU qtest

독립 QEMU build directory를 먼저 구성한다. 이 directory와 configure 명령이 없는
`meson test -C <qemu-build-dir>` placeholder는 재현 가능한 gate가 아니다.

```bash
mkdir -p build/qemu-timer-qtest
(
  cd build/qemu-timer-qtest
  ../../hsoc-stack/tools/qemu/configure \
    --target-list=arm-softmmu,aarch64-softmmu \
    --enable-debug
)
ninja -C build/qemu-timer-qtest

meson test -C build/qemu-timer-qtest --list | \
  rg 'arm-arch-timer-mmio|arm.*generic.*timer|sse-timer'

meson test -C build/qemu-timer-qtest \
  qtest-arm/sse-timer-test \
  qtest-aarch64/arm-arch-timer-mmio-test \
  --print-errorlogs
```

새 CPU/provider qtest 이름도 같은 명령에 추가한다. test는 frozen QEMU clock,
exact delta, deadline, mask/ISTATUS, PPI/SPI, WFIT와 notification을 확인한다.

### T3. QBox build 및 platform integration

```bash
PATH="$PWD/build/qemu-host-tools:$PATH" ./local_build.sh qbox

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --out build/qbox-apollo-qvp/timer-validation/<id>/integration/map.json
```

`apollo_timer_snapshot`은 실제 Lua topology를 elaborate하고 SMD, AP, SI0, SI1,
RSE view를 각 owner API로 관측한다. 각 QEMU raw observation은 bridge epoch의
SystemC time에 대해 provider count와 먼저 일치해야 하며, 그 뒤 공통 sample time의
count로 정규화된다.

### T4. QBox full-system runtime

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 600 \
  --no-post-login-probe \
  --timer-probe \
  --out-dir \
    build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json \
    build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final/result.json \
  --ap-map-audit \
    build/qbox-apollo-qvp/ap-map-9-1-1/ap-map-audit.json \
  --output \
    build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final/full-coverage-audit.json
```

`--timer-probe`는 AP CPU/MMIO count, frame deadline/SPI, SI CPU/CNTBase와 RSE
TIMER0~3 상태를 `timer-snapshot.json`에 기록한다. minimal Buildroot image에는 일반
post-login probe가 요구하는 `pfdi-cli`와 `systemctl`이 없으므로 이 timer gate에서는
`--no-post-login-probe`를 사용했다. Linux login 및 모든 live-domain marker는 별도로
통과했다.

### T5. FVP baseline과 differential

```bash
MACHINE=apollo-fvp ./local_build.sh build

python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/qbox-apollo-qvp/timer-validation/<id>/fvp/boot \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login

scripts/debug/run_local_fvp_debug.sh \
  --no-attach \
  --iris-port 7100 \
  --session apollo-fvp-timer-final \
  --out-dir \
    build/qbox-apollo-qvp/timer-validation/final-differential/fvp/run-final-2

python3 scripts/debug/capture_fvp_timer_snapshot.py \
  --manifest \
    build/qbox-apollo-qvp/timer-validation/final-differential/fvp/debug/symbols.json \
  --port 7100 \
  --breakpoint-memory-space Hyp \
  --sample 'start=u-boot:_start' \
  --sample 'end=u-boot:board_init_f' \
  --view 'smd=RD_ASD.css.smb.si.cluster0.cpu0:memory:SP:0xd0040008:8' \
  --view 'ap_cpu0=RD_ASD.css.app00.cluster.cpu0:register:AArch64 System.CNTPCT_EL0' \
  --view 'ap_refclk_ns=RD_ASD.css.app00.cluster.cpu0:memory:SP:0x1a830000:8' \
  --view 'ap_refclk_s=RD_ASD.css.app00.cluster.cpu0:memory:SP:0x1a820000:8' \
  --view 'si0_cpu0=RD_ASD.css.smb.si.cluster0.cpu0:register:AArch64 System.CNTPCT_EL0' \
  --view 'si0_cntbase=RD_ASD.css.smb.si.cluster0.cpu0:memory:SP:0xd0050000:8' \
  --view 'si1_cpu0=RD_ASD.css.smb.si.cluster1.cpu0:register:AArch64 System.CNTPCT_EL0' \
  --enable-secure-frame \
  --secure-access-memory \
    'RD_ASD.css.app00.cluster.cpu0:SP:0x1a810044' \
  --output \
    build/qbox-apollo-qvp/timer-validation/final-differential/fvp/timer-snapshot-final.json

python3 scripts/test/compare_qbox_fvp_timer_snapshots.py \
  --qbox \
    build/qbox-apollo-qvp/timer-validation/20260722-full-runtime-final/timer-snapshot.json \
  --fvp \
    build/qbox-apollo-qvp/timer-validation/final-differential/fvp/timer-snapshot-final.json \
  --output \
    build/qbox-apollo-qvp/timer-validation/final-differential/timer-differential.json
```

FVP snapshot은 U-Boot `_start`와 `board_init_f`에서 각각 모든 CSS view가 같은
count임을 확인했다. QBox snapshot은 공통 SystemC sample time에서 같은 invariant를
확인한다. producer 사이에는 absolute count가 아니라 두 sample의 증가율을 각
native timebase로 비교하며, 최종 differential은 44/44 pass다.

## 10. Atomic commit 및 dependency 순서

Nested repository dependency 때문에 다음 순서로 commit한다. 각 commit은
Conventional Commit, English message와 `git commit -s`를 사용한다.

1. `qemu`: generic external counter provider, CPU/MMIO consumer와 qtests
2. `qbox`: SystemC provider, libqemu bridge와 unit tests
3. `qbox`: QEMU Clock/SSE counter/timer wrapper와 tests
4. `qbox-platform`: CSS frontend/Lua/CPU wrapper 전환
5. `qbox-platform`: RSE LSC/timer/IRQ/reset/security 전환
6. top-level: Iris/differential 도구, docs와 nested submodule pointer

각 nested commit은 그 repository의 focused test를 통과한 뒤 다음 consumer
repository가 참조한다. `qbox-platform` commit이 아직 존재하지 않는 qbox/qemu
API를 가리키는 중간 상태를 push하지 않는다.

## 11. 위험과 차단 조건

| 위험 | 영향 | 완화/차단 조건 |
| --- | --- | --- |
| 정상 125MHz와 강제 1GHz control 혼용 | timeout과 deadline이 8배 어긋남 | normal-boot executed contract만 production 기준으로 사용 |
| 선택한 frequency 계약이 component source 의도와 불일치 | QBox만 맞춰도 firmware timebase가 틀릴 수 있음 | 정상 FVP executed 125MHz를 production 기준으로 고정하고 malformed component write는 별도 debt로 추적 |
| count read만 provider화 | CVAL/IRQ/WFIT가 stale deadline 사용 | count/deadline/notify qtest 세 항목을 하나의 gate로 묶음 |
| unversioned libqemu struct 확장 | 오래된 DSO에서 out-of-bounds function pointer read | v2 ABI/size negotiation, legacy init 분리 |
| QEMU instance별 time epoch 불일치 | 같은 source인데 count가 다름 | startup epoch assertion과 multi-instance frozen-time test |
| consumer QEMU가 mutation time보다 run-ahead | 이미 실행된 guest side effect는 notification으로 복구 불가 | mutable phase zero-lookahead와 all-instance rendezvous |
| provider mutex/BQL deadlock | full-system hang | provider lock 밖 notification, one-BQL rule, stress test |
| future TLM anchor 조기 적용 | 다른 domain이 미래 state 관측 | annotated delay consume 또는 ordered PEQ 검증 |
| QEMU reset이 CSS를 reset | AP/SI reset 때 global time jump | physical reset만 provider에 연결, QEMU reset isolation test |
| RSE IRQ 39~42 오사용 | ATU/MHU IRQ 충돌 | source-backed 3/4/5/27 static validator |
| SSE/Ma1 register 차이 | TF-M register access 실패 | P0 compatibility matrix, QEMU model 확장; stub 금지 |
| RSE LSC NS map 추정 | security/fault behavior 오류 | guide 충돌 해결 전 secure map만 구현 |
| duplicate migration state | restore 후 counter/IRQ 분리 | external mode migration 비지원 또는 단일 owner post-load 계약 |
| callback teardown race | use-after-free | observer unregister와 pending-job drain test |
| RSE whole-instance reset | TIMER3/LSC AON state까지 소실 | system reset을 granular device reset으로 전환 |
| SSE reset notification 누락 | TIMER0~3 stale deadline/IRQ | reset 후 notify/rearm qtest |
| PPC register만 구현하고 access를 허용 | secure/privileged policy가 실제 bus에 적용되지 않음 | RequestContext 기반 `rse_ppc_filter` allow/deny test |
| `MemTxAttrs.user` 유실 | PPC privileged check가 항상 잘못된 값 사용 | libqemu-cxx attrs 보존과 four-combination propagation test |
| stale local libqemu ExternalProject stamp | 수정한 QEMU가 QBox build에 반영되지 않음 | local QEMU 및 `QBOX_LIBQEMU_BUILD_ALWAYS=ON` 강제 |
| AP/SI timer class를 같은 PPI에 복사 | reserved PPI 사용 또는 잘못된 EL timer IRQ | domain별 PPI matrix와 QEMU output identity test |

기록되지 않은 provisional hardware 값, legacy QEMU regression, deadline test 실패,
BQL deadlock, 잘못된 RSE IRQ 또는 full-system boot 실패 중 하나라도 있으면 해당
phase는 완료가 아니다.

## 12. Definition of Done

최종 완료 보고서는 다음 evidence를 같은 revision에 대해 제시해야 한다.

- 세 nested repository의 exact base commit과 working-tree diff 상태; commit 후에는
  top-level submodule pointer
- P0 frequency/reset/access decision record 및 FVP raw snapshot
- QEMU legacy/external provider qtest 결과
- QBox counter/bridge/RSE wrapper unit 및 multi-instance 결과
- Apollo map validator JSON
- live CL0+CL1 full-system `result.json`과 per-domain log
- coverage audit JSON
- FVP/QBox timer differential JSON
- 남은 cross-chip sync, SI external alias와 migration fidelity debt

위 증거 없이 address가 추가되었거나 Linux가 한 번 boot했다는 사실만으로는
FVP-equivalent timer/counter/reference-clock 구조가 완료되었다고 판정하지 않는다.
