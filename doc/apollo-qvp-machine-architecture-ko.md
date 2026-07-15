# Apollo QVP Machine Architecture 비교 및 개선안

작성일: 2026-07-15

상태: 설계 기준안

대상: `apollo-qvp` / RD-Aspen CFG2

연계 계획: [Apollo QVP Machine Architecture 개선 계획](apollo-qvp-machine-improvement-plan-ko.md)

## 1. 목적

이 문서는 현재 QBox `apollo-qvp` machine 구현을 Arm Zena CSS RD-Aspen
CFG2의 문서상 하드웨어 아키텍처와 Arm FVP `FVP_Zena_CSS_Cfg2`가 노출하는
동작에 대조한다. 비교 범위는 다음과 같다.

- 시스템 및 도메인별 memory map
- Primary Compute(AP), System Management Domain(SMD), RSE, Safety Island(SI)
  하드웨어 블록
- interconnect, bus, ATU/APU와 주소 routing
- SRAM, DRAM, flash와 공유 메모리 view
- interrupt, reset, clock, power 및 안전 신호 routing

이 문서의 결론은 단순히 누락된 레지스터 블록을 나열하는 데 있지 않다.
현재 부팅 중심의 평탄한 QBox machine을 Zena CSS의 도메인 경계와 접근 정책이
보이는 virtual platform으로 전환하기 위한 목표 구조를 정의한다.

## 2. 결론 요약

현재 QVP는 RSE, SI CL0/CL1, AP를 한 프로세스에서 함께 실행하고 주요 firmware
handoff를 재현할 수 있는 기능적 기반을 갖추었다. 특히 AP CPU/GIC, RSE 로컬
주소 공간, MHU, ATU, Safety Island GIC view, FMU/SSU, REFCLK timer와 주요
메모리 backing은 단순 register-only skeleton보다 진전된 상태다.

그러나 machine의 중심 interconnect는 아직 Zena CSS 구조와 다르다.

1. `host_router` 하나가 52-bit 시스템 주소 공간, AP 로컬 주소, SI 로컬 주소를
   함께 수용한다.
2. AP와 SI의 겹치는 로컬 주소는 별도 address view가 아니라 decode priority와
   alias로 구분한다.
3. AP view router는 독립된 AP bus의 기본 구조가 아니라 live CL0 통합 시점에
   사후 삽입된다.
4. SMD의 NI-710AE APU가 규정하는 default-deny 접근 정책과 RSE 소유권이
   routing 구조 자체로 강제되지 않는다.
5. 메모리 크기와 CPU topology 일부가 active Yocto/FVP 설정과 독립적으로
   Lua 기본값에 고정되어 있다.

따라서 최우선 개선은 주변장치를 더 추가하는 것이 아니라 address view를
`AP`, `SMD/system`, `RSE`, `SI CL0`, `SI CL1`로 분리하고, 도메인 사이를
명시적인 ATU/APU bridge로만 연결하는 것이다. QBox core의 기존 `router`와
`addrtr`로 이를 구현할 수 있으므로, Apollo 전용 동작은 계속
`qbox-platform` 소유로 유지한다.

## 3. 분석 기준과 판정 원칙

### 3.1 분석한 소스 revision

| 저장소 | revision |
| --- | --- |
| 최상위 `arm-auto-solutions` | `8ed21e4fdf2b` |
| `hsoc-stack/tools/qbox-platform` | `2bcd02c4e192` |
| `hsoc-stack/tools/qbox` | `5b44f50ff3d8` |
| `hsoc-stack/tools/qemu` | `ca30c1782ea0` |
| `arm-zena-css` | `bf34d9e71f67` |

revision이 바뀌면 주소, module type, 기본값과 fidelity 판정도 다시 확인해야
한다.

### 3.2 활성 build configuration

분석 시점의 active build는 FVP가 아니라 QVP를 대상으로 한다.

| 항목 | 값 |
| --- | --- |
| template | `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/` |
| `MACHINE` | `apollo-qvp` |
| image target | `nexios-image` |
| `TMPDIR` | `build/tmp_baremetal` |
| `RD_ASPEN_VARIANT` | `cfg2` |
| `PC_CPUS_COUNT_DEFAULT` | `4` |
| FVP 역할 | architecture/FVP 비교 및 source-level debug 기준 |

현재 QBox Lua의 AP CPU 기본값은 16이므로 build 설정과 source 기본값이 다르다.
실행 도구가 이를 명시적으로 resolve하고 증거에 기록해야 한다.

### 3.3 기준 자료의 우선순위

1. `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
2. `arm-zena-css/documentation/design/components.rst`
3. `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`
4. `doc/arm_zena_css_dev_guide/08-fixed-virtual-platform.md`
5. `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/` 아래 FVP 설정
6. 현재 `qbox-platform/platforms/apollo/` Lua와 QBox/SystemC/QEMU 소스

문서상 architecture contract와 FVP 구현은 동일한 개념이 아니다. FVP도
CoreSight 등 일부 실제 하드웨어를 생략하는 functional model이다. 따라서 본
문서에서 "FVP와 일치"는 silicon cycle accuracy가 아니라 관찰 가능한 software
contract가 일치한다는 뜻으로만 사용한다.

### 3.4 Fidelity 분류

| 등급 | 의미 |
| --- | --- |
| 기능 모델 | register state와 외부 효과, interrupt 또는 transaction 동작이 구현됨 |
| 호환 모델 | 부팅에 필요한 관찰 동작은 제공하지만 원 IP의 전체 기능은 아님 |
| backing/view | RAM·ROM·flash 저장공간 또는 동일 backing을 보는 주소 view |
| placeholder | 주소를 점유하거나 RAZ/WI에 가까운 최소 동작만 제공 |
| 미구현 | 주소 decode, 상태 또는 외부 효과가 없음 |

`gs_memory`는 모두 부채가 아니다. 실제 SRAM, TCM, DRAM, ROM backing에는
적절하지만 watchdog, power integration, identity/control register를 대신할 때는
placeholder다.

## 4. Arm Zena CSS / Apollo FVP 기준 아키텍처

### 4.1 시스템 도메인

RD-Aspen CFG2의 주요 도메인은 다음과 같다.

| 도메인 | 주요 구성 | 기준 동작 |
| --- | --- | --- |
| AP / Primary Compute | 4 cluster × 4 Cortex-A720AE, DSU-120AE, GIC-720AE, MMU-720AE, CMN/NI | Linux와 rich OS 실행, coherent memory와 I/O 접근 |
| SMD | shared SRAM, system PPU, reset/clock/power control, ATU, MHU, system counter, expansion | 도메인 연결과 공용 자원 제공 |
| RSE | Cortex-M55, secure boot, DMA/crypto/KMU/LCM/SAM, ATU/APU 정책 | Root of Trust, 모든 ATU 설정 소유 |
| SI CL0 | dual lock-step 성격의 Cortex-R82AE safety cluster | bootstrap, safety control, CL1 관리 |
| SI CL1 | 4-way SMP Cortex-R82AE cluster | Zephyr와 safety workload 실행 |

Safety Island GIC는 bootstrap/configuration용 view 0, CL0 OS용 view 1, CL1
OS용 view 2를 제공한다. 이는 단순히 같은 GIC MMIO를 여러 주소에 alias하는
문제가 아니라 각 initiator가 보아야 하는 제어 면과 interrupt 소유권의
문제다.

### 4.2 계층적 주소 공간

각 도메인의 로컬 주소 폭은 최대 48-bit이고, 시스템 interconnect는 52-bit
주소의 상위 4-bit로 영역을 구분한다.

| system-wide 영역 | 의미 | 경계 |
| --- | --- | --- |
| `0x0_0000_0000_0000`–`0x0_FFFF_FFFF_FFFF` | AP physical address space | AP local map에 진입 |
| `0x1_0000_0000_0000`–`0x1_FFFF_FFFF_FFFF` | AP access through TCU | AP가 관리하는 translation 경로 |
| `0x2_0000_0000_0000`–`0x2_0000_FFFF_FFFF` 중심 | SMD | shared/system control 자원 |
| `0x3_0000_0000_0000`–`0x3_0000_FFFF_FFFF` | RSE | 32-bit RSE 공간 외 접근 차단 |
| `0x4_0000_0000_0000`–`0x4_00FF_FFFF_FFFF` | Safety Island | 40-bit SI 공간 외 접근 차단 |

RSE, SI와 SMD의 ATU는 52-bit system address를 해당 도메인의 작은 logical
window에 투영한다. NI-710AE APU는 subsystem 진입을 필터링하며 boot 시 RSE를
제외한 접근은 기본 차단된다. 모든 ATU 구성의 최종 소유자는 RSE다.

### 4.3 AP memory map의 핵심 구간

| 주소 | 기준 블록 | QVP 관점에서 중요한 contract |
| --- | --- | --- |
| `0x0000_0000`–`0x07ff_ffff` | 128 MiB shared SRAM aperture | AP/RSE/SI 공유와 보안 partition |
| `0x1000_0000`–`0x13ff_ffff` | System NoC GPV | NI-710AE programmer view |
| `0x1a40_0000`–`0x1a83_ffff` | UART, watchdog, SID, AP REFCLK | secure/non-secure view와 IRQ |
| `0x1d00_0000`–`0x1def_ffff` | AP FMU region | cluster/system fault reporting |
| `0x2000_0000`–`0x27ff_ffff` | GIC | distributor/redistributor/ITS view |
| `0x4000_0000`–`0x4fff_ffff` | AP→SMD ATU window | 기본 closed, ATU 정책으로 개방 |
| `0x5fff_0000`–`0x5fff_ffff` | RGIC2LGIC message register | remote/local GIC 전달 |
| `0x8000_0000`–`0xffff_ffff` | low DRAM aperture | 2 GiB 범위 |
| `0x1_0000_0000` 이후 | CMN, cluster utility, memory controller, SMMU/NI/PCIe | control/GPV 공간 |
| `0x08_8000_0000`–`0x0d_ffff_ffff` | single-chip high DRAM | DT와 실제 배치의 일치 필요 |
| `0x200_0000_0000` 이후 | multichip DRAM | chip ID/주소 크기 정책 필요 |

SMD는 별도의 52-bit map 안에 `0x2_0000_6000_0000` shared SRAM,
`0x2_0000_d000_0000` CSS control, Reset Generation Manager, ATU, REFCLK,
SYSTOP/DBGTOP power integration, UART/GPIO/SID와 FMU 구간을 가진다.

## 5. 현재 Apollo QVP machine 구조

### 5.1 조립 흐름

`platforms/apollo/apollo-qvp.lua`는 `fabric.create()`로 root container와
`host_router`를 만든 뒤 RoS, system management, RSE, AP, SI 블록을 순서대로
정의한다. live CL0 모드에서 `prepare_live_cl0_integration()`을 호출한 뒤 CL0를
활성화하며, live CL1은 다시 같은 root 구조에 추가된다.

```text
                         +------------------------------+
 AP CPUs / GPEX / DMA -->| ap_view_router               |
   (live CL0일 때 삽입)   |  + AP passthrough            |
                         +---------------+--------------+
                                         |
                                  host_ap_atu / 1:1
                                         |
 RSE CPU --> rse_router --> RSE ATU ------+
 SI CL0 CPU/DMA --------------------------+--> host_router --> 모든 target
 SI CL1 CPU/DMA --------------------------+       ^
 loaders/debug initiators ------------------------+

 중첩 주소 해소: target priority 변경 + alias
```

RSE만 `rse_router`를 통해 명확한 local map을 갖는다. AP는 live CL0 통합 시
`ap_view_router`가 뒤늦게 삽입되며, SI CL0/CL1은 별도 local router 없이
`host_router`에 직접 연결된다. `si_cl1.lua`도 이를 "temporary merged bus"로
명시한다.

### 5.2 현재 구성의 장점

- 단일 TLM fabric 덕분에 firmware가 요구하는 주소를 빠르게 연결할 수 있다.
- `router`의 overlap priority, alias, DMI와 `addrtr`의 주소 변환을 재사용한다.
- RSE local map과 RSE/SMD/AP/SI 사이의 boot-critical ATU/MHU 경로가 존재한다.
- AP는 QEMU Cortex-A720AE CPU, GICv3/ITS, PCIe, VirtIO, PL031, UART를 사용한다.
- SI CL0은 Cortex-R82, GIC, `gicx00_multiview`, `zena_ssu`, `zena_fmu`,
  `host_gtimer`, CMN/NI discovery 모델을 결합한다.
- SI CL1은 4-core SMP, GIC, UART, MHU, SRAM/SCMI 경로를 제공한다.
- AP MMIO generic timer는 125 MHz REFCLK와 secure SPI 48, non-secure SPI 49를
  사용하고, CPU generic timer PPI는 CPU 내부 경로에 남겨 둔다.

### 5.3 현재 하드웨어 블록 비교

| 영역 | 현재 QVP | 판정 및 개선점 |
| --- | --- | --- |
| AP CPU topology | `cpu_arm_cortexA720AE`, 1–16 core | 최대 topology는 맞지만 Lua 기본 16과 active Yocto 기본 4가 불일치 |
| AP GIC/ITS | QEMU `arm_gicv3`, ITS, RGIC message model | 기능 기반 양호, GIC-720AE safety/fault/multiview 의미는 부분적 |
| AP MMU-720AE | `mmu720ae` 또는 SMMUv3 fallback | boot/I/O functional subset, TBU/RAS/safety 동작은 별도 추적 필요 |
| CMN/NI-710AE | `host_cmn_cyprus`, `host_ni710ae_nci` | discovery/register 호환 모델이며 CHI coherency·실제 NoC arbitration 모델은 아님 |
| AP timer/UART/RoS | MMIO timer, PL011, VirtIO, PL031 | 주요 software contract 제공 |
| AP secure watchdog | `gs_memory` control/refresh | 주소만 유지하는 placeholder, timeout/reset/IRQ 효과 필요 |
| SMD | PPU/SCR, ATU, MHU, shared SRAM, system counters | 주요 boot service 존재, RGM/APU/default-deny 및 power/reset graph가 불완전 |
| RSE | M55 wrapper, TCM/VM/flash, DMA350, crypto/KMU/LCM/SAM, protection, ATU, MHU | 폭넓은 기능 모델 보유 |
| RSE OTP/control/integration | 일부 `gs_memory` | OTP, identity, power/security control과 DCLS 의미 보강 필요 |
| SI CL0 | R82, GIC/multiview, FMU/SSU, MHU, timer/PPU/PLL, CMN/NI view | boot/safety path는 기능적, local bus 분리와 DCLS/fault propagation 보강 필요 |
| SI CL1 | 4×R82 SMP, GIC, MHU, UART, SRAM | 기능 path 존재, 독립 local address view가 없음 |
| RoS | VirtIO block/net/rng, PL031 | system register, p9, VSI, RoS UART 항목은 부재 또는 범위 밖 |

### 5.4 Memory map 차이

| 항목 | Zena CSS/FVP 기준 | 현재 QVP | 의미 |
| --- | --- | --- | --- |
| system fabric | 상위 nibble로 AP/SMD/RSE/SI 분리 | 하나의 `host_router`에 system/local map 혼재 | 가장 큰 구조 차이 |
| AP shared SRAM | 128 MiB aperture | `0x0000_0000`의 1 MiB backing과 별도 boot용 SRAM | boot에는 충분할 수 있으나 aperture와 보호 의미가 축소됨 |
| AP low DRAM | 2 GiB aperture | `0x8000_0000`, `0x7f00_0000` + SPMC/통신 buffer 분할 | 배치 의도는 있으나 선언적 bank 검증이 없음 |
| AP high DRAM | single/multichip 규칙에 따라 배치 | `0x200_0000_0000`, 2 GiB | 현재 DT/deploy 산출물과의 자동 일치 확인 필요 |
| RSE local map | 독립 32-bit 공간 | 독립 `rse_router` | 목표 구조에 가장 가까움 |
| SI local map | 독립 40-bit 공간과 ATU | root router에 직접 등록 | 같은 숫자 주소의 AP target과 충돌 가능 |
| SMD | 독립 52-bit system management map | root target들의 집합 | 영역·APU·소유권이 명시적 hierarchy가 아님 |

현재 map validator가 많은 주소 상수와 binding 존재를 확인하지만, 이는 접근
주체별 view와 negative access, 보안 속성, 실제 side effect가 동일함을 뜻하지
않는다.

### 5.5 Bus 및 routing 차이

Zena CSS에서 CMN/NI/AXI/AHB/APB 경계는 단순 성능 topology만이 아니다. address
width, 보안 속성, access control, error response와 관리 소유권을 규정한다.
현재 QVP는 TLM generic payload routing으로 software-visible 효과를 빠르게
재현하지만 다음 정보가 구조에서 사라진다.

- transaction의 출발 도메인과 initiator identity
- AP local address인지 system-wide address인지에 대한 view 구분
- ATU를 통과하지 않은 cross-domain 접근의 금지
- NI-710AE APU의 RSE-only boot policy
- unmapped 접근의 `DECERR`, reserved register의 RAZ/WI 구분
- bridge별 DMI 허용 범위와 invalidate 전파

낮은 숫자가 높은 decode priority인 QBox router 규칙은 한 address view 안의
의도적인 subwindow overlay에는 적합하다. 그러나 다른 도메인의 동일 숫자
주소를 구분하는 수단으로 사용하면 platform 조립 순서에 따라 잘못된 target이
선택될 수 있다.

### 5.6 Interrupt, reset, clock, power routing 차이

현재 interrupt는 QEMU GIC/NVIC와 Lua signal binding으로 기능한다. FMU critical
및 non-critical 경로, MHU receiver IRQ, AP timer SPI와 CPU PPI도 상당 부분
연결되어 있다. 다만 route가 여러 Lua 파일에 분산되어 있어 다음 질문에 대한
단일 검증 자료가 없다.

- 각 interrupt source의 유일한 sink와 ID는 무엇인가?
- GIC view마다 어떤 register와 interrupt가 보여야 하는가?
- reset 시 어떤 IRQ와 pending state가 함께 초기화되는가?
- FMU→SSU→GIC 또는 reset escalation의 실제 전파 순서는 무엇인가?

reset/power는 MHU service와 `host_ppu` 신호를 통해 boot에 필요한 효과를
제공하지만, RGM부터 power domain, CPU reset, clock enable로 이어지는 독립된
signal topology로 표현되지 않는다.

## 6. 구조적 위험과 우선순위

| 우선순위 | 구조적 gap | 실패 양상 |
| --- | --- | --- |
| P0 | AP/SMD/RSE/SI address view가 분리되지 않음 | 잘못된 target 선택, 불가능해야 할 cross-domain 접근 허용 |
| P0 | decode priority가 도메인 구분을 대신함 | 새 MMIO 추가 시 기존 boot path가 순서 의존적으로 회귀 |
| P0 | ATU/APU 정책과 initiator identity가 routing에 강제되지 않음 | 보안/안전 negative test가 거짓 통과 |
| P1 | CPU/DRAM topology가 build artifact와 자동 동기화되지 않음 | DT와 machine 간 CPU/메모리 불일치 |
| P1 | IRQ/reset/power route manifest 부재 | 연결 누락과 잘못된 ID를 정적 검증하기 어려움 |
| P1 | shared backing과 address view 구분이 불명확 | 동일 메모리 복제, DMI alias incoherency 가능 |
| P2 | 일부 control/fault 블록이 placeholder | 정상 boot는 통과해도 fault/reset 검증 불가 |
| P3 | CHI/NoC timing·contention 미모델링 | 성능·타이밍 분석에는 사용할 수 없음 |

## 7. 목표 QBox machine architecture

### 7.1 목표 topology

```text
 AP CPU / AP DMA / PCIe
          |
     +----v-----+       AP->SMD ATU/APU
     | ap_router|--------------+
     +----+-----+              |
          | region 0 bridge    |
          v                    v
 +--------+--------------------+-------------------------------+
 | system_router (52-bit, system physical address only)        |
 | region 0: AP    region 1: AP/TCU    region 2: SMD           |
 | region 3: RSE   region 4: SI        others: DECERR          |
 +---+----------------+-------------------+---------------------+
     |                |                   |
 +---v------+    +----v-----+       +-----v----------------+
 |smd_router|    |rse bridge|       | SI system bridge/APU |
 +---+------+    +----+-----+       +-----+----------------+
     |                |                   |
 SMD devices      +---v------+      +-----v------+  +----------+
 shared SRAM      |rse_router|      |si_cl0_router| |si_cl1_router|
 RGM/PPU/ATU      +----------+      +------------+ +------------+

 별도 signal fabric:
   IRQ source -> domain GIC/NVIC view
   RGM/PPU/FMU/SSU -> reset, clock, power, safety escalation
```

### 7.2 핵심 설계 원칙

1. **주소 view 우선**: CPU, DMA, loader, debug initiator는 자신의 domain router에만
   bind한다.
2. **명시적 cross-domain path**: 다른 도메인 접근은 ATU/TCU bridge와 APU를
   반드시 통과한다.
3. **system router는 system address만 decode**: SI와 AP의 같은 local 숫자
   주소를 한 table에 넣지 않는다.
4. **priority의 제한적 사용**: 같은 view 안의 명시적 subwindow에만 허용하고,
   모든 overlap은 manifest에 이유와 소유자를 기록한다.
5. **RSE 소유권 강제**: boot reset 상태에서 cross-domain access는 RSE만
   허용하며, ATU/APU programming 후에만 다른 initiator를 연다.
6. **backing과 view 분리**: 하나의 SRAM/DRAM/flash backing을 여러 address view가
   공유하며, alias별 복제 메모리를 만들지 않는다.
7. **오류 응답 보존**: unmapped는 `DECERR`, reserved register는 요구에 따라
   RAZ/WI 또는 `SLVERR`로 구분한다.
8. **설정 단일화**: CPU 수, memory bank와 enabled device는 active build
   manifest 또는 명시적 runner option에서 한 번 결정하고 result에 남긴다.
9. **QBox core 경계 보존**: 범용 router/translation 기능만 QBox core에 두고,
   Zena CSS map/policy는 `qbox-platform`에 둔다.
10. **부팅과 fidelity를 분리 판정**: Linux/Zephyr boot 성공만으로 접근 제어,
    fault, reset 또는 safety parity를 완료로 판정하지 않는다.

### 7.3 선언적 topology contract

Lua 블록이 전역 table을 조립 순서대로 직접 변경하는 방식 대신 다음 정보를
하나의 machine-readable contract로 만든다.

| 필드 | 내용 |
| --- | --- |
| `domain` / `view` | AP, SMD, RSE, SI_CL0, SI_CL1, SYSTEM |
| `initiators` | CPU, DMA, PCIe, loader, debug 등 허용 출발점 |
| `local_base`, `size` | initiator가 보는 주소 |
| `system_base` | system-wide 주소, 로컬 전용이면 없음 |
| `target` / `backing` | 실제 SystemC/QEMU target과 저장공간 |
| `bridge` | 통과해야 하는 ATU/TCU/alias 경로 |
| `access` | secure/non-secure, read/write, APU policy |
| `owner` | reset 시 정책과 runtime programming 소유자 |
| `irq`, `reset`, `clock`, `power` | 관련 signal route ID |
| `dmi` | 허용 여부, translated range와 invalidate 정책 |
| `fidelity` | 기능 모델, 호환 모델, backing, placeholder, 미구현 |
| `source` | Zena CSS 문서 table/section 또는 FVP 설정 근거 |

machine 조립은 `구성 해석 → instance 생성 → route binding → overlap/policy 검증
→ topology freeze` 순서로 고정한다. 조립이 끝난 뒤 다른 블록이 기존 target의
priority를 변경하지 못하게 한다.

### 7.4 도메인별 목표

#### AP

- `ap_router`를 AP CPU 유무와 무관한 AP physical view의 정식 root로 만든다.
- CPU, GIC, SMMU, PCIe, DRAM, flash, AP peripheral과 RoS를 AP view에 등록한다.
- AP→SMD `0x4000_0000` window는 ATU가 열린 범위만 전달한다.
- `ap_view_passthrough`의 broad 1:1 mapping을 제거한다.
- CPU 수 4/16과 memory bank를 deploy DTB/manifest와 대조한다.

#### SMD / system fabric

- `system_router`는 52-bit region decode와 width check만 담당한다.
- `smd_router`는 shared SRAM, RGM, PPU, ATU, system counter와 공용 peripheral을
  소유한다.
- NI-710AE APU의 initiator별 default-deny와 RSE override를 기능 모델로 둔다.
- SMD의 shared SRAM은 하나의 backing을 AP/RSE/SI view로 노출한다.

#### RSE

- 기존 `rse_router`를 유지하고 system bridge의 width와 access policy를 명시한다.
- 모든 ATU/APU programming authority를 RSE reset state와 연결한다.
- OTP, identity, integration, power/security control의 placeholder를 firmware가
  관찰하는 순서대로 기능 모델로 승격한다.

#### Safety Island

- CL0와 CL1에 독립 local router를 두고 각 CPU/DMA/GIC view를 분리한다.
- SI system bridge는 40-bit 범위와 ATU window만 허용한다.
- GIC view 0/1/2의 register visibility와 interrupt owner를 명시적으로 검증한다.
- FMU→SSU→GIC/reset escalation, CL0 DCLS와 CL1 SMP 차이를 signal graph에 담는다.
- `temporary merged bus`와 이를 위한 `lower_decode_priority()` 호출을 제거한다.

### 7.5 Memory와 DMI 원칙

- architectural aperture와 실제 allocated backing 크기를 별도 필드로 기록한다.
- 같은 shared SRAM을 view별 `gs_memory`로 복제하지 않는다.
- ATU/alias를 통과한 DMI는 반환 범위를 local window로 clip하고 주소를 역변환한다.
- backing write 또는 remap 시 모든 관련 alias에 DMI invalidation을 전파한다.
- DRAM controller timing/ECC를 구현하지 않은 경우에도 이를 `backing`과 구분해
  fidelity ledger에 남긴다.
- single-chip과 multichip DRAM map은 하나의 고정 상수가 아니라 topology
  configuration에서 선택한다.

### 7.6 IRQ 및 sideband topology 원칙

주소 map과 별도로 다음 route manifest를 생성한다.

- `source → sink controller → interrupt ID → security/group → owner`
- AP generic timer PPI와 AP REFCLK SPI를 별도 계층으로 유지
- MHU sender/receiver와 receiver IRQ의 peer 관계
- SI GIC view별 visible frame과 CL0/CL1 interrupt 소유권
- FMU critical/non-critical output, SSU input과 escalation output
- RGM/PPU의 reset request, reset output, clock/power dependency

정적 검증은 중복 ID, dangling source/sink, 잘못된 controller view와 reset 후
초기 상태를 검사한다.

## 8. 목표 fidelity와 비목표

### 8.1 1차 목표

- software-visible memory map 및 domain별 address view 일치
- ATU/APU access 허용·차단과 오류 응답
- interrupt, reset, power, MHU와 safety fault의 관찰 가능한 side effect
- FVP와 같은 firmware/OS boot handoff 및 driver probe
- 재현 가능한 topology/route/result JSON 증거

### 8.2 명시적 비목표

- CMN/NI의 cycle-accurate arbitration, CHI packet timing과 contention
- 실제 DRAM PHY, analog PLL 또는 PMIC의 전기적 동작
- FVP 자체가 모델링하지 않는 모든 CoreSight/trace block
- silicon 성능 수치의 예측

이 비목표는 주소를 broad memory로 채워도 된다는 뜻이 아니다. software가
접근하는 register와 fault/interrupt effect는 별도의 fidelity 상태로 관리한다.

## 9. Architecture 완료 조건

다음 조건을 모두 만족해야 목표 machine architecture 전환이 완료된 것으로
판정한다.

- AP, SMD, RSE, SI CL0, SI CL1 initiator가 독립 address view를 가진다.
- 도메인 간 접근은 manifest에 등록된 ATU/APU bridge로만 성공한다.
- 문서화되지 않은 overlap과 broad pass-through가 정적 검사에서 실패한다.
- reset 직후 RSE 외 cross-domain 접근이 차단되고, programming 후 선택적으로
  허용되는 negative/positive test가 있다.
- CPU 수와 DRAM bank가 active build artifact와 일치하며 result JSON에 기록된다.
- IRQ/reset/power route에 dangling 또는 중복 binding이 없다.
- full-system QBox boot와 FVP boot를 동일한 관찰 항목으로 비교한다.
- placeholder와 미구현 블록이 이름, 주소, 영향, 대체 계획과 함께 ledger에 남는다.

## 10. 근거 파일

### Arm Zena CSS / FVP

- `arm-zena-css/documentation/design/components.rst:96-160,196-210,363-397`
- `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`
- `doc/arm_zena_css_dev_guide/08-fixed-virtual-platform.md`
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:75-154`
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:247-335`
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:22-23`
- `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc:49`

### 활성 build 설정

- `build/conf/local.conf`
- `build/conf/bblayers.conf`
- `build/conf/templateconf.cfg`

### 현재 QVP

- `hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua:42-56`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/fabric.lua:3-19`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua:555-655`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua:506-521`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua:96-107`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua:423-460`
- `hsoc-stack/tools/qbox/systemc-components/router/`
- `hsoc-stack/tools/qbox/systemc-components/addrtr/`

기존 [Apollo FVP-QVP Hardware Comparison KR](apollo-fvp-qvp-hardware-comparison-ko.md)와
[Apollo QBox Hardware KR](apollo-qbox-hardware-ko.md)은 subsystem별 상세 목록을
제공한다. 다만 현재 source revision과 다른 설명이 있을 수 있으므로 구현 상태는
위 revision의 Lua/SystemC/QEMU 소스를 최종 기준으로 삼는다.
