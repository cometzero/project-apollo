# Arm Zena CSS FVP Timer, Counter 및 Reference Clock 분석

작성일: 2026-07-21, 최종 갱신 2026-07-22

대상: `FVP_Zena_CSS_Cfg2` / RD-Aspen CFG2

FVP 버전: Fast Models 11.31.25 (2026-02-25)

상위 저장소 기준: `8e1b107c27b1fec01b325832e362a1e851bd7b64` 기반 working tree

## 1. 결론

Arm Zena CSS의 timer 구조를 단순히 "subsystem마다 독립 counter가 하나씩
있다"고 해석하면 안 된다. 하드웨어 사양과 현재 FVP 동작을 구분한 결론은
다음과 같다.

1. AP와 Safety Island가 사용하는 Arm Generic Timer는 timer comparator와
   interrupt 상태는 CPU core 또는 MMIO frame별로 독립적이지만, 시간의 기준인
   System Counter 값은 CSS REFCLK 계열의 공통 counter를 사용하도록 구성된다.
2. 물리 REFCLK 입력과 정상 배포 image에서 실제 실행되는 visible count는 모두
   125MHz이다. 정상 boot의 SMD `CNTINCR=0`은 FVP reset/default 의미의 실효
   increment 1로 동작한다. debugger로 `CNTINCR=8`을 강제했을 때의 1GHz 결과는
   rate 제어가 동작함을 확인한 대조군일 뿐 정상 boot 계약이 아니다.
3. Zena CSS 하드웨어 사양에는 RSE 전용 Local System Counter가 별도로 존재하며,
   RSE `TIMER0`~`TIMER3`의 `CNTVALUEB` 입력을 공급한다. 따라서 하드웨어 관점의
   기본 구조는 "CSS 공통 counter 하나 + RSE local counter 하나"이다.
4. 그러나 현재 `FVP_Zena_CSS_Cfg2`는 RSE Local System Counter register window를
   구현하지 않았고, RSE `TIMER0`~`TIMER3`도 CSS SMD `ref_counter`와 같은 count를
   보도록 alias한다. 이것은 FVP 모델의 단순화이며 하드웨어 구조와 다르다.
5. System Generic Timer Synchronization block은 AP, SI, RSE 내부에서 매 cycle
   counter를 배포하는 블록이 아니다. primary chip과 secondary chip 사이의
   cross-chip 시간 동기화 제어 블록이다.

즉, 질문에 대한 짧은 답은 다음과 같다.

> CPU와 subsystem마다 timer 상태와 comparator는 따로 유지되지만, AP와 SI의
> 시간 원점은 공통 CSS System Counter이다. RSE는 하드웨어상 별도 Local System
> Counter를 갖지만, 현재 FVP에서는 그 local counter가 생략되고 CSS 공통
> counter로 대체되어 있다.

## 2. 분석 기준과 확실성 표기

이 문서는 다음 세 층을 분리해서 분석한다.

| 층 | 의미 | 주 근거 |
| --- | --- | --- |
| 하드웨어 의도 | Zena CSS programmer model이 정의하는 block 및 연결 | `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md` |
| FVP 구현 | 현재 설치된 CFG2 모델이 실제 제공하는 parameter, instance, register 및 count 동작 | FVP `--list-params`, `--list-instances`, `--list-regs`, Iris 동적 측정 |
| 소프트웨어 계약 | SCP-firmware, TF-A, TF-M, DTS가 설정하거나 기대하는 주소와 주파수 | 각 component source |

본문에서 사용하는 확실성은 다음과 같다.

- **확정**: 문서 또는 source가 직접 정의하고, 필요한 경우 Iris로도 확인했다.
- **FVP 측정**: 현재 설치된 FVP 버전에서 동적으로 관측한 모델 동작이다.
- **미확정**: 로컬 공개 자료만으로 연결 source를 단정할 수 없다.

관련 source 기준 commit은 다음과 같다.

| Source | Commit |
| --- | --- |
| `arm-zena-css` | `bf34d9e71f674e11beea3b8e84ea54486f555d2a` |
| `scp-firmware` | `6d2e1e8094c7575c8a9b7fb2410dc2748a550882` |
| `trusted-firmware-m` | `0e172f0b18e29a28f60b804bb01ddcd527e4d4b4` |
| `trusted-firmware-a` | `059ccacc64711bd4164d71a7b0e495749197680d` |

## 3. 용어 정리

Arm Generic Timer에서 counter와 timer는 같은 것이 아니다.

| 용어 | 역할 |
| --- | --- |
| REFCLK | System Counter를 구동하는 물리 reference clock. Zena FVP 기본값은 125MHz이다. |
| System Counter | 시간 경과에 따라 단조 증가하는 64-bit count인 `CNTCV`를 유지한다. |
| CPU Generic Timer | 각 CPU core 안의 `CNTP_*`, `CNTV_*`, `CNTHP_*` comparator/control 상태이다. count source를 읽어 `CVAL`과 비교하고 PPI를 발생시킨다. |
| MMIO Generic Timer frame | System Counter를 공유하면서 frame별 `CVAL`, `TVAL`, control 및 SPI를 갖는 memory-mapped timer이다. |
| Timestamp-based Timer | 외부 `CNTVALUEB` count 입력과 자신의 compare/control 상태를 이용해 interrupt를 발생시키는 RSE timer이다. |
| Counter control/read frame | 하나의 counter를 제어하거나 읽기 위한 서로 다른 register view이다. frame이 여러 개라고 counter state도 여러 개인 것은 아니다. |

[Arm Generic Timer 설명서](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Learn%20the%20Architecture/Generic%20Timer.pdf?revision=c710e7a7-9f52-4901-8c9d-91b19f44f9c7)는
System Counter와 각 processing element의 timer comparator를 이와 같이
구분한다.

## 4. Zena CSS 하드웨어 기준 구조

### 4.1 전체 구조

하드웨어 사양을 기준으로 한 논리 구조는 다음과 같다.

```text
        125MHz REFCLK                RSE local counter clock input
              |                     (source/rate: local guide 미확정)
              |                                  |
    CSS REFCLK System Counter            RSE Local System Counter
    control/read/sync frames             control/read frames
              |                                  |
       +---------+-----------+               +--> RSE TIMER0
       |         |           |               +--> RSE TIMER1
       |         |           |               +--> RSE TIMER2
       |         |           |               +--> RSE TIMER3 (AoN)
       |         |           |
    AP cores   AP MMIO     Safety Island cores/frames
    per-core   S/NS frame  per-core comparator/PPI
    timer/PPI  SPI 48/49
```

이 그림에서 화살표 끝의 timer들은 각자 enable, mask, compare value 및 interrupt
상태를 갖는다. 공유되는 것은 시간 count source이며 comparator 상태가 아니다.

### 4.2 CSS REFCLK System Counter

SMD의 CSS control region에는 세 개의 64KB frame이 연속 배치된다.

| 물리 주소 | 이름 | 역할 |
| --- | --- | --- |
| `0x02_0000_D010_0000` | REFCLK Counter `CNTControlBase` | counter 제어 및 count 접근 |
| `0x02_0000_D011_0000` | REFCLK Counter `CNTRead` | read-only count view |
| `0x02_0000_D012_0000` | `SYSCNT0_MSTSYNC_CTRL` | primary-secondary chip 동기화 제어 |

근거는 Zena CSS guide
`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:293-295`이다.
동기화 block의 목적은 같은 문서 `:9295-9297`에 primary chip과 secondary chip
사이 request-acknowledge 동기화로 명시되어 있다.

### 4.3 Primary Compute의 timer

AP에는 두 종류의 Generic Timer view가 존재한다.

1. 각 Cortex-A720AE core의 architectural Generic Timer
2. AP peripheral block에 있는 REFCLK memory-mapped Generic Timer

MMIO frame은 다음과 같다.

| 주소 | Frame | Security | Interrupt |
| --- | --- | --- | --- |
| `0x1A81_0000` | `AP0_REFCLK_CNTCTL` | Non-secure control | - |
| `0x1A82_0000` | frame 1 | Secure | SPI 48 |
| `0x1A83_0000` | frame 0 | Non-secure | SPI 49 |

주소와 interrupt는 Zena CSS guide `:110-112`, `:1415-1416` 및 TF-A
`plat/arm/board/automotive_rd/platform/apollo_fvp/include/platform_def.h:41-45`에서
일치한다. Linux-visible DTS는 non-secure frame 0과 SPI 49를
`fdts/apollo_fvp.dtsi:689-705`에 기술한다.

CPU internal timer는 per-core PPI 장치이다. 각 core의 comparator/control과 PPI는
독립적이지만, `CNTPCT_EL0` 같은 physical count view는 공통 System Counter 시간
축을 읽는다. 따라서 AP CPU 수만큼 독립 free-running counter가 생기는 구조가
아니다.

AP hardware의 timer PPI matrix는 다음과 같다
(`09-programmers-model-for-zena-css.md:1331-1348`).

| PPI | Timer output | 의미 |
| ---: | --- | --- |
| 19 | `CNTHVS` | Secure EL2 virtual timer |
| 20 | `CNTHPS` | Secure EL2 physical timer |
| 26 | `CNTHPIRQn` | Non-secure EL2 physical timer |
| 27 | `CNTVIRQn` | virtual timer |
| 28 | `CNTHVIRQn` | EL2 virtual timer |
| 29 | `CNTPSIRQn` | secure physical timer |
| 30 | `CNTPNSIRQn` | non-secure physical timer |

이 표는 count source가 일곱 개라는 뜻이 아니다. comparator/control/interrupt
class가 분리되어 있고 모두 해당 PE가 보는 공통 physical counter 시간 축을
기준으로 deadline을 계산한다는 뜻이다. 실제 firmware/DT가 사용하는 subset과
PE가 구현한 extension은 별도로 확인해야 한다.

### 4.4 Safety Island의 timer

Safety Island CL0에는 다음 local programmer view가 있다.

| 주소 | 이름 | 역할 |
| --- | --- | --- |
| `0x2A6F_0000` | `SYSCLK_CNTCTLBase` | CL0 SYSCLK timer control view |
| `0x2A72_0000` | `SYSCLK_CNTBase_CL0` | CL0 timer frame/count view |
| `0x01_7072_0000` | `REFCLK_SSYSCLK_CNTBase0` | 외부 system view의 SSYSCLK frame |

근거는 Zena CSS guide `:1227-1230`, `:1304`이다. CFG2의 CL1은 FVP 전용 두 번째
Cortex-R82AE cluster이며, 현재 하드웨어 guide에는 CL1 register와 interrupt가
정의되어 있지 않다(`08-fixed-virtual-platform.md:21-32`).

SI0 hardware의 CPU timer PPI는 AP matrix와 같지 않다. table 9-38
(`09-programmers-model-for-zena-css.md:1644-1656`)에서 timer output은
`CNTHPSIRQ=PPI20`, `CNTVIRQ=PPI27`, `CNTPSIRQ=PPI29` 세 개이고 PPI 19, 26,
28, 30은 reserved이다. CFG2 SI1은 FVP extension이므로 SI0 표를 그대로 복사해서
하드웨어 사실로 취급할 수 없고 Iris target/GIC 상태로 별도 확인해야 한다.

SCP-firmware는 하나의 논리 `SI0_TIMER` element에 세 view를 묶는다.

- `hw_timer = SI0_TIMER_CNT_BASE_CL0`
- `hw_counter = SI0_TIMER_CNTCTL_BASE`
- `control = SI0_REFCLK_CNTCONTROL_BASE`

이는 `scp-firmware/product/automotive-rd/rdaspen/si0_ramfw/config_gtimer.c:63-73`에
정의되어 있다. 즉, local timer frame과 SMD로 번역되는 REFCLK counter control을
하나의 timer driver가 함께 사용한다.

### 4.5 RSE Local System Counter와 timer

하드웨어 사양에서 RSE는 CSS REFCLK counter와 구별되는 Local System Counter를
갖는다.

| 주소 | 이름 | 역할 |
| --- | --- | --- |
| `0x5015_8000` | `SOC_TIMER0` | Zena CSS System Timestamp-based Timer 0 |
| `0x5015_9000` | `SOC_TIMER1` | Zena CSS System Timestamp-based Timer 1 |
| `0x5015_A000` | `LSC_CB` | Local System Counter Control Base |
| `0x5015_B000` | `LSC_RB` | Local System Counter Read Base |
| `0x5800_0000`~`0x5800_3000` | `TIMER0`~`TIMER3` | RSE timestamp timer, IRQ 3/4/5/27 |

Zena CSS guide `:15014-15023`은 Local System Counter의 목적을 `TIMER0`~`TIMER3`에
`CNTVALUEB`를 공급하는 것으로 직접 정의한다. `TIMER0`~`TIMER3`과 Local System
Counter는 모두 PD_AON에 속한다. reset source는 `TIMER0`~`TIMER2`가
`nWARMRESETSYS_RSS`, `TIMER3`과 Local System Counter가 `nWARMRESETAON`으로
다르다(`:14940-14946`, `:15027-15043`). TF-M의 RSE common platform도 같은
control/read base와 timer base를 정의한다.

TF-M common device 설정은 `SYSTIMER0_ARMV8M_DEFAULT_FREQ_HZ`를 32MHz로
정의한다(`device/config/device_cfg.h:91-94`). 이는 현재 software가 RSE system
timer에 적용하는 frequency 계약이지만, 로컬 Zena CSS guide만으로 RSE Local
System Counter의 실제 입력 clock source와 rate를 증명하지는 못한다. 뒤에서
확인하듯 현재 FVP의 RSE timer count는 이 32MHz 설정과도 다르다.

`SOC_TIMER0/1`도 Zena CSS system timestamp timer로 정의되지만, 로컬 guide에는
이 두 timer의 `CNTVALUEB` source가 명시적으로 연결되어 있지 않다. 따라서 이
문서에서는 이 두 timer의 하드웨어 count source를 **미확정**으로 남긴다.

## 5. 현재 FVP가 구현한 구조

### 5.1 모델 parameter와 instance

현재 설치된 CFG2 FVP에서 다음 명령으로 parameter를 확인했다.

```bash
build/tmp_baremetal/sysroots-components/x86_64/fvp-rd-aspen-native/usr/lib/fvp/\
fvp-rd-aspen/bin/FVP_Zena_CSS_Cfg2 --list-params
```

관련 기본값은 다음과 같다.

```text
ros.ref_clk_frequency=125000000
css.smb.smd.ref_counter.has_counter_scaling=0
css.smb.smd.ref_counter.non_arch_start_at_default=0
```

`non_arch_start_at_default=0`은 정상 부팅에서 firmware가 counter를 enable해야 함을
뜻한다. `--list-instances`와 `--list-regs`에서는 다음 항목을 확인했다.

- `RD_ASD.css.smb.smd.ref_counter`: `CNTCR`, `CNTCV_LO/HI`, `CNTFID0`,
  `CNTINCR`
- `RD_ASD.css.ap_periph.gtimer`: AP MMIO Generic Timer
- `RD_ASD.css.smb.si.system_timer`: Safety Island system timer
- AP, SI0, SI1 CPU의 `CNTFRQ_EL0`, `CNTPCT_EL0` 등 architectural timer register
- RSE `timer0`~`timer3`

Yocto FVP 설정인
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:26-98`과
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc:14-20`에는
timer/reference-clock override가 없다. CFG2 추가는 실행 파일, SI CL1 UART 및
LLRAM 설정뿐이므로 이 분석에서는 모델 기본 clock parameter가 적용된다.

### 5.2 Iris 동적 측정

배포된 local-build image를 정상 실행한 뒤 Iris로 멈춰 같은 logical point에서
register와 simulation time delta를 수집했다. 정상 상태는 다음과 같다.

```text
physical REFCLK     = 125000000 Hz
SMD CNTCR           = 0x101
SMD CNTFID0         = 125000000
SMD CNTINCR         = 0
simulation elapsed  = 1030743023 ticks @ 1 THz
expected count      = floor(1030743023 * 125000000 / 1e12)
                    = 128842
observed count delta= 128842
```

즉 정상 배포 image의 executed contract는 `125MHz input`, `CNTINCR register=0`,
FVP default 실효 increment 1, visible count 125MHz이다. AP CPU 0~3은
`CNTFRQ_EL0=125MHz`이고 같은 SMD count를 읽었다. SI0은 `CNTFRQ_EL0=0`이지만
같은 count를 읽었고, SI1 CPU 0~3은 `CNTFRQ_EL0=100MHz`를 보고하면서도 같은
SMD count를 읽었다. reported frequency metadata와 physical count source가 서로
다를 수 있음을 구분해야 한다.

rate 제어 대조군으로 debugger가 `CNTINCR=8`을 강제한 경우에는
`232320000000`개의 1THz simulation tick 동안 count가 `232320000` 증가하여 정확히
1GHz가 됐다. 이 결과는 `CNTINCR=8`의 모델 의미를 확인하지만 정상 boot 상태를
나타내지 않는다.

두 번째 검증에서는 counter를 정지한 뒤 SMD `CNTCV`에 `0x912345678`을 기록했다.
그 즉시 AP CPU, SI0 CPU, SI1 CPU 및 RSE `TIMER0`~`TIMER3`의 count view가 모두
같은 값을 반환했다. 이는 단순히 같은 rate로 따로 증가하는 counter가 아니라,
현재 FVP 내에서 실제로 같은 counter state가 alias되어 있음을 보여준다.

정상 boot의 AP MMIO control base `0x1A810000`에서는 `CNTFRQ=125MHz`,
`CNTNSAR=1`, `CNTACR0=0x3f`, `CNTACR1=0`을 읽었다. 따라서 non-secure frame 0
`0x1A830000`은 SMD와 같은 count와 125MHz를 반환하지만 secure frame 1
`0x1A820000`의 count/frequency는 RAZ이다. debugger로 `CNTACR1=0x3f`를 쓰면
secure frame 1도 즉시 같은 SMD count와 125MHz를 반환했고, 0으로 복구하면 다시
RAZ가 됐다. 이는 frame 1의 map과 공통 count 연결이 존재하되 정상 firmware가
access를 disable한다는 증거다.

SI1 FVP-only CPU timer output은 comparator를 강제로 만료시켜 GIC pending bit를
측정했다. `CNTP=PPI29`, `CNTV=PPI27`, `CNTHPS=PPI20`이 확인됐고, 이 FVP의 SI1
CPU에는 `CNTHP`, `CNTHV`, `CNTHVS`, `CNTPS` comparator register가 노출되지
않았다. 이 matrix는 CFG2 FVP 동작이며 SI0 hardware table을 복사한 결과가 아니다.

반면 RSE CPU의 모든 Iris memory space에서 다음 주소는 unmapped access였다.

- `0x50158000`: Zena CSS System Timer 0
- `0x50159000`: Zena CSS System Timer 1
- `0x5015A000`: RSE Local System Counter control
- `0x5015B000`: RSE Local System Counter read

따라서 현재 FVP는 하드웨어가 정의한 RSE local counter path를 구현하지 않고,
RSE `TIMER0`~`TIMER3`을 CSS 공통 count에 연결한 것으로 결론 내릴 수 있다.

정상 boot 측정과 강제 쓰기 대조군의 원자료, 배포 artifact hash 및 판단은
`build/qbox-apollo-qvp/timer-validation/20260722-085755/fvp/` 아래에 보존했다.

최종 독립 재측정은 U-Boot `_start`와 `board_init_f`에서 수행했다. 두 지점 모두
SMD, AP CPU, AP MMIO NS/S, SI0 CPU/CNTBase와 SI1 CPU의 7개 CSS view가 정확히
같았고, secure frame의 원래 `CNTACR1=0`을 확인한 뒤 임시 32-bit enable write와
복구를 수행했다. 구조화 결과는
`build/qbox-apollo-qvp/timer-validation/final-differential/fvp/timer-snapshot-final.json`
이며 status는 `pass`다.

### 5.3 FVP 논리 topology

현재 FVP의 실측 topology는 다음과 같다.

```text
ros.ref_clk_frequency = 125MHz
                 |
          SMD ref_counter
          normal CNTINCR = 0
          default effective increment = 1
          effective count = 125MHz
                 |
       +---------+----------+------------+-------------+
       |         |          |            |             |
    AP CPU    AP MMIO*    SI0 CPU     SI1 CPU      RSE TIMER0..3
    timers    frames       timers      timers       FVP alias

RSE LSC control/read (0x5015A000/0x5015B000): not mapped in this FVP

* AP MMIO NS frame 0은 정상 enable되어 공통 count를 읽는다. secure frame 1은
  CNTACR1=0 때문에 RAZ이며, CNTACR1=0x3f 대조군에서 같은 count가 확인됐다.
```

## 6. 주파수 계약 문제

### 6.1 CSS REFCLK: 정상 실행 125MHz와 source/deploy 불일치

현재 source에는 물리 clock과 visible count frequency 사이의 계약이 일관되지
않는 지점이 있다.

1. FVP의 물리 REFCLK parameter와 정상 visible count delta는 125MHz이다.
2. SCP-firmware source는 `SYSCNT_INCR=8`을 "1GHz clock speed에 필요한 값"이라고
   설명하고 `CNTINCR`에 기록한다
   (`config_gtimer.c:32-39`, `:51-59`).
3. 그러나 배포된 `si0_ramfw.elf`의 `gtimer_control_init+0x34`는
   `str x5, [x3, x2]`로 32-bit impdef register에 64-bit store를 수행한다.
   `syscnt_impdef_cfg`의 배포 bytes는 `{0xc0:0, 0xd0:8}`이다. FVP는 이 malformed
   64-bit `CNTINCR` write를 WI로 처리하여 정상 boot에서 `CNTINCR=0`이 유지된다.
4. debugger로 유효한 `CNTINCR=8` 쓰기를 강제한 대조군에서만 visible count가
   정확히 1GHz가 됐다.
5. 같은 SCP configuration의 `.frequency`와 `CNTFID0` 설정값은
   125MHz이다(`config_gtimer.c:63-73`, `mod_gtimer.c:294-312`).
6. `mod_gtimer`는 이 `.frequency`를 framework에 반환하고 count-to-time 변환에도
   사용한다(`mod_gtimer.c:165-175`, `:393-396`).
7. TF-A의 `SYS_COUNTER_FREQ_IN_TICKS`와 `plat_get_syscnt_freq2()`도 125MHz를
   반환한다(`platform_def.h:315-316`, `apollo_fvp_plat.c:58-61`).

동일 SCP-firmware tree의 RD1AE 및 여러 Neoverse RD configuration은
`.frequency = CLOCK_RATE_REFCLK * SYSCNT_INCR`로 설정한다. 따라서 Zena/Apollo
현재 설정은 다음 둘 중 하나로 통일되어야 한다.

- 125MHz REFCLK에 `CNTINCR=8`을 적용하여 visible count를 1GHz로 만들고,
  `CNTFID0`, `CNTFRQ`, firmware time conversion도 1GHz로 맞춘다.
- visible count 자체를 125MHz로 유지하고 FVP의 `CNTINCR=0` default 실효
  increment 1 의미를 명시적으로 계약한다.

현재 정상 배포 FVP와 firmware reported-frequency의 실행 계약은 두 번째 방향,
즉 visible 125MHz이다. 다만 source 의도와 배포 실행이 다르므로 이 문서에서는
component source를 변경하지 않는다. production QBox는 측정된 125MHz를 기준으로
generic provider와 production wiring을 구현했다. 이는 사용자가 정상 배포 FVP의
executed 125MHz 계약을 우선하도록 결정한 결과이며, source의 malformed 64-bit
write는 별도 component debt로 남긴다.

### 6.2 RSE: TF-M 32MHz와 FVP 125MHz alias

TF-M common RSE device는 `TIMER0`의 기본 frequency를 32MHz로 설정하지만,
현재 FVP의 RSE `TIMER0`~`TIMER3` count view는 CSS SMD count와 동일한 125MHz
delta를 반환했다. 동시에 하드웨어 guide는 RSE Local System Counter의 입력
clock source/rate를 명시하지 않는다.

따라서 다음 세 값을 서로 다른 근거로 관리해야 한다.

| 값 | 의미 | 상태 |
| ---: | --- | --- |
| 32MHz | TF-M common RSE timer software 설정 | source로 확정 |
| 미확정 | Zena CSS RSE Local System Counter의 실제 hardware clock | 추가 TRM/integration 자료 필요 |
| 125MHz | 현재 FVP가 RSE TIMER0~3에 alias한 CSS count | 정상 boot Iris로 측정 |

QBox의 RSE Local System Counter를 구현할 때 125MHz나 1GHz를 임의로 적용하면
안 된다. Corstone Ma1 integration 자료와 정상 FVP/firmware 설정을 추가 확인해
RSE local-domain frequency를 별도로 결정해야 한다.

## 7. subsystem별 최종 판정

| Subsystem/view | Timer/comparator 상태 | Count source: 하드웨어 의도 | 현재 FVP | 판정 |
| --- | --- | --- | --- | --- |
| AP CPU core | core별, PPI별 독립 | CSS REFCLK System Counter | SMD `ref_counter` 공유 | 확정 |
| AP MMIO secure/non-secure frame | frame별 CVAL/control/SPI 독립 | CSS REFCLK System Counter | NS frame 0은 공통 count, S frame 1은 `CNTACR1=0`에서 RAZ이고 enable 대조군에서 공통 count | FVP 측정 |
| SI0 CPU 및 timer frame | core/frame별 독립 | CSS REFCLK System Counter | SMD `ref_counter` 공유 | 확정 |
| SI1 CPU | core별 독립 | CFG2 FVP 전용이라 하드웨어 guide 미정의 | SMD `ref_counter` 공유, `CNTP/V/CNTHPS=PPI29/27/20` | FVP 측정 |
| RSE TIMER0~3 | timer별 compare/IRQ 독립 | RSE Local System Counter, rate는 로컬 guide에서 미확정 | SMD `ref_counter` 125MHz 공유 | 하드웨어/FVP/TF-M 32MHz 계약 불일치 |
| RSE SOC_TIMER0/1 | timer별 독립 | 로컬 자료만으로 source 미확정 | address unmapped | FVP 미구현 |
| Cross-chip sync | 동기화 state machine | primary-secondary chip 동기화 | 별도 sync block | counter source가 아님 |

## 8. 분석에 사용한 주요 근거

### Repository source

- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
  - AP timer frames: `:110-112`
  - SMD counter 및 sync frames: `:293-295`
  - RSE timer/local counter map: `:674-677`, `:700-703`
  - Safety Island timer views: `:1227-1230`, `:1304`
  - AP timer SPI: `:1415-1416`
  - cross-chip synchronization: `:9295-9297`
  - RSE timer 및 Local System Counter: `:14940-14948`, `:15014-15043`
- `doc/arm_zena_css_dev_guide/08-fixed-virtual-platform.md:21-32`
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:26-98`
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc:14-20`
- `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/rdaspen/si0_ramfw/config_gtimer.c:21-83`
- `hsoc-stack/components/system_mgmt/scp-firmware/module/gtimer/src/mod_gtimer.c:59-77`,
  `:165-175`, `:294-312`, `:393-396`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/config/device_cfg.h:75-94`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/source/device_definition.c:222-300`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/partition/platform_base_address.h:65-68`,
  `:109-110`, `:131-134`
- `hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_fvp/include/platform_def.h:26-45`,
  `:315-316`
- `hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp.dtsi:689-705`,
  `:845-852`

### Arm 공식 자료

- [Learn the Architecture: Generic Timer](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Learn%20the%20Architecture/Generic%20Timer.pdf?revision=c710e7a7-9f52-4901-8c9d-91b19f44f9c7)
- [Arm Corstone Reference Systems Architecture Specification Ma1](https://developer.arm.com/documentation/102803/)

## 9. 분석 한계

- 설치된 FVP는 closed binary이므로 내부 signal netlist를 직접 검토할 수 없다.
  동일 counter 판정은 공개 parameter/register surface와 Iris read/write 실측을
  결합한 결과이다.
- RSE `SOC_TIMER0/1`의 하드웨어 count source는 현재 로컬 guide만으로 확정하지
  않았다.
- RSE Local System Counter 자체의 입력 clock source/rate도 로컬 guide만으로
  확정하지 않았다. TF-M의 32MHz 값은 software configuration 근거로만 사용했다.
- 정상 배포 image의 CSS executed contract와 AP MMIO access-control은 측정했다.
  SCP-firmware source가 의도한 `CNTINCR=8`과 배포 ELF의 malformed 64-bit write 중
  어느 쪽을 고칠지는 component owner 결정 사항으로 남는다.
- RSE Local System Counter의 실제 clock rate, secure/non-secure 노출 정책과
  integration reset signoff는 미확정이다. 모든 timer/LSC의 PD_AON 소속 및
  `TIMER0`~`TIMER2` 대비 `TIMER3`/LSC reset-source 차이는 문서상 확인했지만
  runtime reset evidence는 아직 없다.
