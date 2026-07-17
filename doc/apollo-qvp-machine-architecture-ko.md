# Apollo QVP Machine Architecture 비교 및 개선안

작성일: 2026-07-15, 최종 갱신 2026-07-17

상태: QBox / system hardware / system software / QEMU 및 Arm Zena CSS
하드웨어 블록 다이어그램 리뷰 반영, A0–A4 구조 전환과 I0–I7 4 CPU fidelity
구현·리뷰·local/Yocto 검증 완료

대상: active `apollo-qvp` / RD-Aspen CFG2 / current Zena CSS architecture와
FVP CFG2 extension

연계 계획: [Apollo QVP Machine Architecture 개선 계획](apollo-qvp-machine-improvement-plan-ko.md)

잔여 부채 설계와 리뷰:

- [잔여 아키텍처 부채 설계](apollo-qvp-remaining-architecture-debt-design-ko.md)
- [2026-07-15 아키텍처 리뷰](apollo-qvp-remaining-architecture-review-2026-07-15.md)
- [아키텍처 부채 구현·검증 계획](apollo-qvp-architecture-debt-implementation-plan-ko.md)
- [2026-07-16 구현·검증 보고서](apollo-qvp-architecture-debt-validation-2026-07-16.md)

4 CPU 우선 fidelity 후속 단계:

- [Fidelity 부채 아키텍처 설계](apollo-qvp-fidelity-debt-architecture-design-ko.md)
- [Fidelity 부채 구현 계획](apollo-qvp-fidelity-debt-implementation-plan-ko.md)
- [Fidelity 부채 검증 계획](apollo-qvp-fidelity-debt-validation-plan-ko.md)
- [I7 local/Yocto 완료 보고서](apollo-qvp-fidelity-stages/i7-integration-validation-completion-2026-07-17-ko.md)

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
- QBox/SystemC TLM transaction, QEMU lifecycle와 memory ownership
- firmware, DT와 OS가 공유하는 boot/control 및 software ABI

이 문서의 결론은 단순히 누락된 레지스터 블록을 나열하는 데 있지 않다.
현재 부팅 중심의 평탄한 QBox machine을 Zena CSS의 도메인 경계와 접근 정책이
보이는 virtual platform으로 전환하기 위한 목표 구조를 정의한다.

## 2. 결론 요약

현재 QVP는 RSE, live SI CL0/CL1과 AP를 한 프로세스에서 함께 실행하고 주요
firmware handoff를 재현한다. 52-bit `system_router` 아래에 AP/SMD/RSE/SI의
address view를 분리했으며, `ap_router`, `smd_router`, `rse_router`,
`si_cl0_router`, `si_cl1_router`가 실제 runtime graph에 존재한다. AP/SI의
broad 1:1 system bridge 세 개는 제거됐고 contract phase는
`A4_policy_routing`, `compatibility_debt`는 빈 목록이다.

system address의 `0x2` high-nibble만 `system_to_smd_nci`를 통해 SMD로 decode한다.
AP/SI/SMDEXP `rse_atu` translation socket은 RSE가 programming하는 실제 data
path에 있고, AP shared SRAM, HIPC SRAM, GIC, CSS timer와 SMCF SRAM은 canonical
target 하나를 다른 view가 좁은 static window 또는 ATU를 통해 공유한다.
SystemC SMMU backend의 GPEX DMA는 MMU-720AE LTI00 TBU를 통과한다.

단일 Lua source로 topology, address, transaction, signal, boot/control과 software
ABI contract를 선언하고 9개 JSON evidence를 생성한다. validator는 address width,
overlap, backing, cross-domain reference, route, signal, boot/ABI와 broad bridge
부재를 검사한다. ATU reset 상태의 normal/debug/DMI default-deny도 component
test로 고정했다.

반복 부팅에서 reset-held AP CPU의 timehandler가 SystemC global suspend owner가
되어 simulated time이 멈추는 QEMU/SystemC lifecycle 결함을 추가로 발견했다.
reset-held CPU는 quantum keeper에 참여하지 않고 target-vCPU의 tracked reset
release 완료 뒤에만 time sync와 wake 상태로 복귀하도록 수정했다. 대상 회귀
50회, local source image 5회와 Yocto `nexios-image` 3회, 총 8회의 full-system
boot와 각 49항목 coverage audit가 모두 통과했다.

구현 후 재리뷰에서는 두 경계 오류를 추가로 닫았다. local full-system bootargs의
`maxcpus`를 resolved AP CPU 수와 정렬해 기본 4 CPU만 online하게 했고, SI0가
AP reset 전에 초기화하는 non-secure MHU shared SRAM의 owner를 SMD로 명시해
AP reset fan-out에서 보존했다. 후자는 수정 전 Linux secondary SCMI warning과
timeout을 제거했고 기존 FVP와 같은 SCMI v2.0 firmware marker를 재현했다.
또한 SI CL1 PFDI request가 SI0 transport init보다 먼저 도착할 때 공통 secure
init이 BUSY/payload를 지우던 startup race를 닫았다. 유효한 pending mailbox는
SI0가 소비할 때까지 보존하며, trace/quantum 변경 없이 local/Yocto를 각각 3회
반복해 PFDI ready, 4 CPU, SCMI v2.0과 Linux login을 확인했다.

2026-07-17 비-AP FVP/QBox 로그 비교에서는 별도 QEMU instance인 SI1 requester가
SI0 응답보다 virtual deadline을 먼저 진행해 PFDI timeout이 발생하는 두 번째
경계를 확인했다. SI1 PFDI PBX가 TLM `requester_id`로 실제 발행 vCPU와 quantum
keeper만 정지하고, 실제 SI0 firmware가 shared-memory channel을 `FREE`로 만든
뒤 재개하도록 보강했다. channel 2~5의 초기 setup을 모두 CPU0가 발행하므로
channel 번호는 CPU identity로 사용하지 않는다. local 반복 및 Yocto provider/image
부팅에서 PFDI timeout 4종이 사라졌고, RSE CC3XX `PIDR0`도 FVP와 같은 `0xc1`로
보존됐다.

### 2.1 완료한 A4 구조 전환

1. `smd_router`와 `system_to_smd_nci`를 runtime에 생성했다.
2. AP/SI CL0/SI CL1 broad 1:1 bridge를 삭제했다.
3. SI/AP/SMDEXP ATU를 firmware-controlled data path에 연결했다.
4. 공유 SRAM/GIC/timer/FMU target을 canonical owner 하나로 정리했다.
5. GPEX DMA를 선택한 SMMU backend의 올바른 경로로 연결했다.
6. CL1 HIPC를 문서상 512 KiB static allow-list로 고정했다.
7. reset-held CPU의 QK 참여와 reset release ordering을 architecture invariant로
   추가했다.
8. SMD-owned AP/SI SCMI SRAM을 AP reset에서 보존하는 owner/reset contract를
   추가했다.
9. full-system rootfs의 `maxcpus`를 resolved AP CPU topology와 일치시켰다.
10. AP/CL1 PFDI를 포함한 secure completer transport init이 먼저 게시된 유효한
    mailbox를 보존하도록 startup ownership contract를 추가했다.
11. QBox가 소유하는 SCMI/PFDI completer에 message length 경계,
    `SCMI_PROTOCOL_ERROR`, channel FREE와 다음 정상 요청 recovery를 추가했다.
12. HIPC/RPMsg host service의 invalid descriptor poll을 bounded하게 유지하고,
    다음 doorbell의 정상 descriptor를 소비하는 recovery를 검증했다.

### 2.2 구조 폐쇄 뒤 남은 기능 충실도 부채

1. NI-710AE APU의 완전한 register/permission 및 initiator별 deny matrix.
2. MMU-720AE page-table walk, GPEX requester/StreamID 전 access-kind와
   MSI→ITS→LPI.
3. debug/direct/reentrant trusted capability와 대표 allow/deny. 전체 negative 및
   DMI matrix는 extended validation.
4. FMU/SSU/RAS/DCLS fault injection, power/reset recovery와 timing.
5. PSCI/FF-A firmware-owned 오류, SCMI/PFDI peer-offline/reset-time 오류와
   HIPC duplicate notification. I6의 model-owned malformed/recovery slice는
   완료했고 전체 조합은 extended validation이다.
6. 4 CPU focused FVP/QVP functional comparison. 동일 artifact 전체 differential은
   후속이며 emulator 성능 budget은 두지 않는다.

따라서 A4의 구조적 address-policy 부채는 폐쇄됐지만 Arm Zena CSS/FVP 전체
functional 또는 safety equivalence를 완료로 판정하지 않는다. Apollo 전용
map/policy는 `qbox-platform`, 범용 CPU/QEMU/SystemC lifecycle은 QBox/QEMU가
소유하는 경계를 유지한다.

## 3. 분석 기준과 판정 원칙

### 3.1 분석한 소스 revision

| 저장소 | revision |
| --- | --- |
| 최상위 `arm-auto-solutions` | `a049040e56b7` |
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

full-system QBox Lua와 runner의 AP CPU 기본값은 active Yocto 설정과 같은 4다.
직접 부팅 전용 `apollo-pc.lua`는 16-core 실험 기본값을 유지하므로 full-system
evidence와 혼동하지 않고 resolved CPU 수를 `result.json`에 기록한다.

### 3.3 기준 자료의 우선순위

1. `doc/arm_zena_css_dev_guide/02-block-diagram-for-zena-css.md`
2. `doc/arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md`
3. `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
4. `arm-zena-css/documentation/design/components.rst`와 safety/software design 문서
5. `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`
6. `doc/arm_zena_css_dev_guide/08-fixed-virtual-platform.md`
7. `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/` 아래 FVP 설정
8. 현재 `qbox-platform/platforms/apollo/` Lua와 QBox/SystemC/QEMU 소스

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

RD-Aspen CFG2 reference platform의 주요 도메인은 다음과 같다. 단, current
Zena CSS architecture와 FVP-only 확장을 같은 범위로 취급하지 않는다.

| 도메인 | 주요 구성 | 기준 동작 | scope |
| --- | --- | --- | --- |
| AP / Primary Compute | 4 cluster × 4 Cortex-A720AE, DSU-120AE, GIC-720AE, MMU-720AE, CMN/NI | Linux와 rich OS 실행, coherent memory와 I/O 접근 | Zena CSS architecture |
| SMD | shared SRAM, system PPU, reset/clock/power control, ATU, MHU, system counter, expansion | 도메인 연결과 공용 자원 제공 | Zena CSS architecture |
| RSE | Cortex-M55, secure boot, DMA/crypto/KMU/LCM/SAM, ATU/APU 정책 | Root of Trust, 모든 ATU 설정 소유 | Zena CSS architecture |
| SI CL0 | dual lock-step 성격의 Cortex-R82AE safety cluster | bootstrap, safety control, runtime safety service | Zena CSS architecture |
| SI CL1 | 4-way SMP Cortex-R82AE cluster | Zephyr와 safety workload 실행 | `FVP_Zena_CSS_Cfg2` extension; current Zena CSS configuration에는 없음 |

Safety Island GIC는 bootstrap/configuration용 view 0, CL0 OS용 view 1, CL1
OS용 view 2를 제공한다. 이는 단순히 같은 GIC MMIO를 여러 주소에 alias하는
문제가 아니라 각 initiator가 보아야 하는 제어 면과 interrupt 소유권의
문제다.

`FVP_Zena_CSS_Cfg2`의 두 번째 Safety Island cluster는 추가 real-time processing을
위한 reference-platform 확장이다. 따라서 QVP full-system 호환에는 CL1이
필요하지만, architecture manifest에서는 `fvp_cfg2_extension` scope로 표시하고
current Zena CSS hardware 필수 블록으로 판정하지 않는다.

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

### 4.4 하드웨어 블록 연결 구조

Zena CSS high-level 및 RD-Aspen System Management Block 그림은 AP, RSE,
Safety Island와 Debug/System Control이 하나의 평면 bus에 연결된 구조가 아님을
보여준다.

| 계층 | 하드웨어 경계 | QVP에서 보존할 contract |
| --- | --- | --- |
| AP compute | processor cluster/DSU, GIC-720AE, CMN coherent mesh | CPU-local timer PPI, coherent DRAM visibility, GIC/ITS와 AP physical view |
| AP I/O | PCIe/GPEX, I/O TBU/TCU, ITS와 NI | DMA requester/StreamID, SMMU translation/fault, MSI→ITS→LPI route |
| system fabric | CMN/NI와 52-bit domain region decode | address width, initiator domain, security, translation과 error response |
| SMD | SMD NCI, shared SRAM, system PPU/peripheral, RGM | 공용 backing, reset/clock/power owner와 AP/SI/RSE bridge |
| RSE | RSE local interconnect/NCI, ATU, secure memory/peripheral | Root of Trust view, image/APU/ATU authority와 default-deny policy |
| Safety Island | SI NCI, CL0, GIC multiple view, ATU, MHU, local SRAM | 40-bit local view, CL0 safety owner, FVP CFG2 CL1 extension 분리 |
| sideband | Debug, System Control expansion, FMU/SSU/ESM | trusted debug capability와 별도 reset/fault signal graph |

QVP가 CMN/CHI packet이나 NCI arbitration을 cycle-accurate하게 모델링할 필요는
없다. 그러나 각 경계에서 주소 폭, initiator identity, security, translation,
interrupt 및 fault ownership이 사라져서는 안 된다.

### 4.5 Boot 및 control ownership

Arm boot sequence는 RSE가 모든 system management를 단독 수행하는 구조가 아니라
RSE와 SI CL0가 책임을 나누는 구조다.

| 단계/owner | 필수 동작 | 실패 시 contract |
| --- | --- | --- |
| RSE BL2 | SI CL0 image 인증·적재, SI reset release, AP BL2와 RSE runtime 적재, NI-710AE APU 설정 | 인증/설정 실패 시 다음 domain을 release하지 않음 |
| RSE-owned firmware | 모든 ATU configuration과 lock 관리 | owner가 아닌 write는 실패하고 설정값을 read-back 가능해야 함 |
| SI CL0 | Primary Compute self-test, CMN/GIC/peripheral 설정 | 완료 전 AP CPU가 실행되지 않음 |
| SI CL0 safety verification | RSE ATU access와 SCR expected value 검증 | mismatch 시 boot를 halt하고 AP reset을 유지함 |
| SI CL0 final handoff | primary AP reset release와 runtime safety service 시작 | release 원인과 순서를 trace에 남김 |
| TF-A/Linux/SCP | PSCI와 SCMI를 통한 secondary CPU, system power/reset, performance control | timeout/error가 caller까지 전달되고 무한 대기하지 않음 |

RGM은 RSE, Safety Island, Primary Compute가 공유하는 block이므로 reset은 단순
CPU input wire가 아니다. cold/warm, CPU/cluster/domain, watchdog 및 safety
escalation별로 보존·초기화되는 memory, IRQ와 device state를 별도 정의해야 한다.

### 4.6 System software가 관찰하는 하드웨어 계약

주소와 IRQ가 같아도 producer와 consumer가 공유하는 ABI가 다르면 FVP 호환으로
판정할 수 없다.

| 계약 | producer / consumer | architecture 요구사항 |
| --- | --- | --- |
| Device Tree | TF-A가 생성·FIP에 포함, U-Boot/Linux가 소비 | CPU/memory/GIC/SMMU/MHU/shared-memory가 동일 artifact와 일치하고 SystemReady DT 요구를 검사 |
| SCMI/PSCI | RSE, SCP-firmware, TF-A/Linux | boot confirmation, AP primary/secondary power, system power/reset와 notification channel의 ID·owner·error 정의 |
| PFDI | AP/SI CL1 agent ↔ SI CL0 monitor | agent별 전용 MHU/shared memory, per-CPU watchdog, vendor protocol `0x90`, FDTI와 timeout 정의; 별도 QEMU instance 사이에서는 실제 requester의 virtual deadline을 SI0 channel FREE까지 보존 |
| HIPC/RPMsg | AP Linux ↔ SI CL1 Zephyr | MHUv3와 512 KiB 단일 SRAM backing; resource table 128 KiB, vring 2개 각 128 KiB, buffer 128 KiB |
| remoteproc | AP Linux ↔ independently booted SI CL1 | AP가 CL1을 부팅하지 않으며 초기 상태는 `RPROC_DETACHED` |
| FF-A | TF-A/OP-TEE/Linux endpoints | endpoint, shared-memory descriptor, interrupt와 denied/invalid response 정의 |
| RAS | AP TF-A/Linux FFH, SI firmware | AP corrected/deferred software notification SPI 89와 SI uncorrected ERI 경로를 분리 |

이 계약은 register coverage가 아니라 message, shared-memory layout, state
transition, interrupt/reset side effect와 error termination으로 검증한다.

## 5. 현재 Apollo QVP machine 구조

### 5.1 조립 흐름

`platforms/apollo/apollo-qvp.lua`는 먼저 `machine_contract.lua`로 여섯 contract를
적재·검증한 뒤 `fabric.create()`에서 `system_router`와 `smd_router`를 생성한다.
AP router는 SI mode와 무관하게 구성되고, live SI CL0/CL1을 사용할 때 각각의
local router와 명시적 ATU/static window가 추가된다. 조립 도중 기존 target의
우선순위를 일괄 낮추던
`prepare_live_cl0_integration()` 경로는 제거됐다.

```text
 AP CPUs / GPEX / loaders --> ap_router --+--> AP local targets
                                          +--> AP HIPC alias
                                          +--> AP ATU --> smd_router/system
 GPEX DMA --> MMU-720AE LTI00 ------------+

 RSE CPU --> rse_router --> RSE ATU -----------------------> system_router

 SI CL0 CPU/loaders --> si_cl0_router --+--> CL0 local targets
                                        +--> SI/SMDEXP ATU --> system/SMD
                                        +--> AP shared/GIC narrow windows
                                        +--> SI CL1 SCMI bridge

 SI CL1 CPUs/loaders --> si_cl1_router --+--> CL1 local targets
                                         +--> AP HIPC bridge

 system_router --[0x2 high-nibble NCI decode]--> smd_router --> SMD targets
```

각 router에서 미매핑된 접근은 다른 domain으로 자동 전달되지 않고 address
error로 종료된다. cross-domain transaction은 contract에 선언된 ATU 또는 좁은
static window만 통과한다. decode priority는 같은 view의 의도적인 control-plane
overlay에만 사용한다.

### 5.2 현재 구성의 장점

- 단일 TLM fabric 덕분에 firmware가 요구하는 주소를 빠르게 연결할 수 있다.
- `router`의 overlap priority, alias, DMI와 `addrtr`의 주소 변환을 재사용한다.
- RSE local map과 RSE/SMD/AP/SI 사이의 boot-critical ATU/MHU 경로가 존재한다.
- AP는 QEMU Cortex-A720AE CPU, GICv3/ITS, PCIe, VirtIO, PL031, UART를 사용한다.
- SI CL0은 Cortex-R82, GIC, `gicx00_multiview`, `zena_ssu`, `zena_fmu`,
  `host_gtimer`, CMN/NI discovery 모델을 결합한다.
- FVP CFG2 SI CL1은 4-core SMP, GIC, UART, MHU, SRAM/SCMI 경로를 제공한다.
- AP MMIO generic timer는 125 MHz REFCLK와 secure SPI 48, non-secure SPI 49를
  사용하고, CPU generic timer PPI는 CPU 내부 경로에 남겨 둔다.

### 5.3 현재 하드웨어 블록 비교

| 영역 | 현재 QVP | 판정 및 개선점 |
| --- | --- | --- |
| AP CPU topology | `cpu_arm_cortexA720AE`, 1–16 core 지원, full-system 기본 4 | active Yocto 기본과 local `maxcpus=4`가 정렬됨; 이번 fidelity gate는 CPU0–CPU3만 대상으로 하고 16-core enablement/lifecycle은 후속 범위 |
| AP GIC/ITS | SystemC `gicx00_multiview` view 0 overlay와 QEMU `arm_gicv3` canonical backend, ITS, LPI/DirectLPI, RGIC message model | 표준 GIC access의 단일 functional owner는 QEMU이고 multiview 확장만 SystemC가 소유함; MSI→ITS→LPI와 GIC-720AE safety/fault 의미의 end-to-end 증거는 부족 |
| AP MMU-720AE | 기본 `systemc-mmu720ae`, 선택 `qemu-arm-smmuv3` | boot/I/O functional subset, 두 backend의 requester/StreamID·fault 동등성 기준 필요 |
| AP PCIe/GPEX DMA | GPEX bus master, MMU-720AE LTI00 TBU와 legacy SPI 300–303 | SystemC backend routing은 완료; explicit requester/StreamID와 MSI/LPI end-to-end 증거는 부족 |
| CMN/NI-710AE | `host_cmn_cyprus`, `host_ni710ae_nci` | discovery/register 호환 모델이며 CHI coherency·실제 NoC arbitration 모델은 아님 |
| AP timer/UART/RoS | MMIO timer, PL011, VirtIO, PL031 | 주요 software contract 제공 |
| AP secure watchdog | `gs_memory` control/refresh | 주소만 유지하는 placeholder, timeout/reset/IRQ 효과 필요 |
| SMD | runtime `smd_router`, PPU/SCR, ATU, MHU, shared SRAM, system counters | high-nibble NCI와 canonical owner 구현; 완전한 RGM/APU 및 power/reset graph는 A6 이후 |
| RSE | M55 wrapper, TCM/VM/flash, DMA350, crypto/KMU/LCM/SAM, protection, ATU, MHU | 폭넓은 기능 모델 보유 |
| RSE OTP/control/integration | 일부 `gs_memory` | OTP, identity, power/security control과 DCLS 의미 보강 필요 |
| SI CL0 | R82, GIC/multiview, FMU/SSU, MHU, timer/PPU/PLL, CMN/NI view, 40-bit local router와 ATU | broad bridge 없이 정상 boot; DCLS/fault propagation 보강 필요 |
| SI CL1 | 4×R82 SMP, GIC, MHU, UART, SRAM, 40-bit local router | FVP CFG2 extension scope, static SCMI/HIPC allow-list와 local view, requester-aware PFDI scheduler hold가 명시됨 |
| QEMU/TLM bridge | `QemuMemTxAttrsTlmExtension`, `RequestContextTlmExtension`과 MemTx/TLM 오류 변환 | domain/requester/substream/access path 기반은 구현됐으며 미지원 initiator 조합과 전체 debug/DMI policy matrix는 후속 |
| QEMU CPU lifecycle | managed target-vCPU reset, BQL/DMI reset, async job tracking, reset-held QK 격리, MTTCG quantum/WFI wake | 50회 reset 회귀, 기준 full boot 8회, post-review acceptance 2회와 최종 trace-off 6회 통과; 신규 fault는 대표 smoke만 필수이며 stress/KVM/16 CPU는 후속 |
| RoS | VirtIO block/net/rng, PL031 | system register, p9, VSI, RoS UART 항목은 부재 또는 범위 밖 |

### 5.4 Memory map 차이

| 항목 | Zena CSS/FVP 기준 | 현재 QVP | 의미 |
| --- | --- | --- | --- |
| system fabric | 상위 nibble로 AP/SMD/RSE/SI 분리 | `system_router`와 AP/SMD/RSE/SI local router, `0x2` SMD NCI decode, broad bridge 없음 | A4 policy-routing 구조 완료 |
| AP shared SRAM | 128 MiB aperture | `0x0000_0000`의 1 MiB backing과 별도 boot용 SRAM | boot에는 충분할 수 있으나 aperture와 보호 의미가 축소됨 |
| AP/SI SCMI/PFDI SRAM | SMD/SCP가 AP release 전에 초기화하거나 requester가 SI0 init 전에 게시하는 MHU transport backing | canonical `host_ap_mhu_ns_shared_sram`, SI ATU region 14 view, `preserve_on_ap_reset`, secure pending-mailbox preserve | 주소 view·reset owner·message owner를 분리해 AP reset 및 startup race 뒤 channel state/payload 보존 |
| AP low DRAM | 2 GiB aperture | `0x8000_0000`, `0x7f00_0000` + SPMC/통신 buffer 분할 | 배치 의도는 있으나 선언적 bank 검증이 없음 |
| AP high DRAM | single/multichip 규칙에 따라 배치 | `0x200_0000_0000`, 2 GiB | 현재 DT/deploy 산출물과의 자동 일치 확인 필요 |
| RSE local map | 독립 32-bit 공간 | 독립 `rse_router` | 목표 구조에 가장 가까움 |
| SI local map | 독립 40-bit 공간과 ATU | CL0/CL1 각각 40-bit router, SI/SMDEXP ATU와 HIPC/SCMI static window | 구조적 allow-list와 SI ATU region 14 SCMI backing 확인, 완전한 APU 권한표는 후속 |
| SMD | 독립 52-bit system management map | runtime `smd_router`, NCI prefix decode와 canonical SMD target | 영역·소유권 hierarchy 완료, cycle/APU fidelity는 후속 |

#### AP GIC view 소유권 불변조건

AP GIC의 RD-Aspen software view와 QEMU functional view는 서로 다른 GIC
인스턴스가 아니다. 다음과 같이 하나의 기능 상태에 도달하는 두 programming
view로 모델링한다.

| view | software-visible 주소/간격 | QVP 소유권과 routing |
| --- | --- | --- |
| RD-Aspen secure/legacy view 0 | GICD `0x2000_0000`, GICR scan 시작 `0x200c_0000`, 128 KiB 간격 | `gicx00_multiview`가 `GICD_CFGID`, `GICD_IVIEWR`, `GICR_PWRR/VIEWR/FLUSHR`만 처리하고 표준 GICD/GICR access는 canonical backend로 변환 |
| canonical functional view 1 | GICD `0x2080_0000`, GICR `0x2088_0000`, CPU당 256 KiB 간격 | QEMU `arm_gicv3`가 distributor, CPU0–CPU3 redistributor와 interrupt 상태를 단일 소유 |

view 0의 256 KiB frame 안에는 128 KiB redistributor 두 개가 연속 배치되므로
QVP는 OP-TEE가 사용하는 128 KiB scan을 CPU0–CPU3 canonical redistributor로
변환한다. OP-TEE의 RD-Aspen `GICD_BASE`, `GICR_BASE`, `GICR_SIZE`를 view 1 주소에
맞춰 변경해서는 안 된다. 그런 변경은 software ABI를 QBox 내부 구현에 종속시키고
FVP와의 주소 계약을 깨뜨린다. 표준 register 상태를 SystemC 배열과 QEMU 양쪽에
복제하는 것도 금지하며, 기능 상태의 유일한 owner는 QEMU로 유지한다.

full-map validator와 topology validator가 주소 상수, 실제 binding, view width,
overlap, backing 및 route reference를 확인한다. 이는 접근 주체별 negative access,
보안 속성 또는 실제 side effect까지 동일함을 뜻하지 않으며 해당 항목은 G1/G2
후속 시험 대상이다.

### 5.5 Bus 및 routing 차이

Zena CSS에서 CMN/NI/AXI/AHB/APB 경계는 단순 성능 topology만이 아니다. address
width, 보안 속성, access control, error response와 관리 소유권을 규정한다.
현재 QVP는 A4에서 local/system view와 ATU를 통과하지 않은 cross-domain 접근의
금지를 runtime router로 복원했다. unmapped는 address error로 종료하고 GIC/timer
allocated frame의 reserved tail은 RAZ/WI로 구분한다. 공통 request context를
추가했지만 다음 조합의 전체 coverage와 fault attribution은 여전히 불완전하다.

- 미지원 initiator의 세부 requester identity와 privilege
- NI-710AE APU의 RSE-only register/lock/permission 전체 의미
- GPEX 외 DMA의 StreamID와 SMMU/APU fault syndrome end-to-end 보존
- debug/direct/reentrant access capability의 전체 조합
- bridge/alias별 DMI invalidate 전파의 전체 matrix

현재 QBox–QEMU 경계가 완전히 비어 있는 것은 아니다.

- `QemuInitiatorSocket::qemu_io_access()`는 QEMU `MemTxAttrs`와 공통
  `RequestContextTlmExtension`을 붙이고 TLM response를 `MemTxOK`,
  `MemTxDecodeError`, `MemTxError`로 되돌린다.
- CPU, loader와 GPEX는 origin/domain/requester/substream, capability 및 access
  path를 context에 기록한다. SI1 PFDI trace는 같은 channel에서도 실제 발행
  vCPU가 requester로 보존됨을 확인했다.
- router의 `b_transport`는 initiator ID를 stamp하고 unmapped access에
  `TLM_ADDRESS_ERROR_RESPONSE`를 반환한다. 반면 `transport_dbg`는 같은
  initiator stamping path 없이 decode/forward한다.
- `addrtr`는 동일 payload를 주소 변환해 전달하고 DMI range를 역변환하며
  invalidate를 전달한다. 그러나 이것만으로 APU deny 또는 trusted debug policy가
  보장되지는 않는다.
- GPEX DMA는 explicit PCI requester와 SID를 붙여 MMU-720AE LTI00를 통과한다.
  지원하지 않은 DMA initiator와 모든 fault attribution 조합은 후속이다.

따라서 새 오류 adapter를 중복 구현할 필요는 없다. 기존 MemTx/TLM 변환과 공통
request context를 유지하고, 누락된 initiator/path 조합만 같은 extension으로
확장해야 한다.

낮은 숫자가 높은 decode priority인 QBox router 규칙은 한 address view 안의
의도적인 subwindow overlay에는 적합하다. 그러나 다른 도메인의 동일 숫자
주소를 구분하는 수단으로 사용하면 platform 조립 순서에 따라 잘못된 target이
선택될 수 있다.

### 5.6 QEMU instance, memory ownership 및 lifecycle 차이

Apollo full-system은 AP, RSE, SI에 서로 다른 QEMU/SystemC 실행 경계를 사용한다.
각 instance의 architecture, CPU model, TCG mode, sync policy, RAM/AddressSpace
owner를 한 manifest에서 확인할 수 있어야 하지만 현재는 Lua, CCI, runner와
wrapper에 분산되어 있다.

- AP, RSE, SI CL0와 FVP CFG2 SI CL1은 multi-thread TCG를 사용한다. AP/SI는
  `multithread-quantum`, RSE는 `multithread-freerunning` 정책을 사용한다.
- managed CPU는 reset 중 quantum keeper에 참여하지 않고 release completion 뒤
  시작한다. release 뒤에는 WFI 동안 time sync/wake 계약을 유지해 QEMU deadline
  timer가 CPU를 깨울 수 있게 한다.
- QEMU CPU wrapper에는 `start_reset → hold_reset → finish_reset` state,
  SystemC-thread reset callback, BQL 구간의 DMI flush, async job tracking과 QEMU
  kick이 이미 존재한다.
- exclusive와 reentrant QEMU I/O는 direct, debug request는 debug, 나머지는
  regular TLM access로 갈라진다. 이 경로들이 일반 functional policy를
  우회하는지 명시돼 있지 않다.
- QEMU `MemoryRegion`/`AddressSpace`, QBox `gs_memory`와 file-backed IPC 중 어느
  객체가 각 RAM의 canonical backing owner인지 생성된 evidence에서 바로 알 수
  없다.

목표 구조는 이 lifecycle을 새로 복제하지 않고 Apollo reset/power graph와
연결한다. reset, BQL, async completion, quantum/WFI 및 DMI invalidation의 순서를
architecture acceptance로 승격하고, 하나의 backing은 정확히 한 component가
소유하도록 한다.

### 5.7 Interrupt, reset, clock, power routing 차이

현재 interrupt는 QEMU GIC/NVIC와 Lua signal binding으로 기능한다. FMU critical
및 non-critical 경로, MHU receiver IRQ, AP timer SPI와 CPU PPI도 상당 부분
연결되어 있고 `signal_routes.lua`가 machine-readable source/sink/INTID contract를
제공한다. 다만 다음 질문은 runtime injection과 state-transition evidence가
아직 부족하다.

- 각 interrupt source의 유일한 sink와 ID는 무엇인가?
- GIC view마다 어떤 register와 interrupt가 보여야 하는가?
- reset 시 어떤 IRQ와 pending state가 함께 초기화되는가?
- FMU→SSU→GIC 또는 reset escalation의 실제 전파 순서는 무엇인가?

reset/power는 MHU service와 `host_ppu` 신호를 통해 boot에 필요한 효과를
제공하지만, RGM부터 power domain, CPU reset, clock enable로 이어지는 독립된
signal topology로 표현되지 않는다.

AP GIC는 ITS, LPI와 GICv4.1 DirectLPI 기능을 노출하고 GPEX legacy interrupt는
SPI 300–303에 연결된다. 그러나 PCIe MSI→ITS→LPI, SMMU event/fault, AP RAS
software notification SPI 89와 SI ERI까지를 하나의 source-to-vCPU route로
검증하는 manifest는 없다. FMU도 register/IRQ 존재보다 threshold,
critical/non-critical output, SCP serialization queue, SSU FSM과 ESM status의
event 순서가 핵심이다.

### 5.8 Evidence root 명명 차이

프로젝트 contract, full-system runner, coverage audit와 신규 QVP evidence의
표준 root는 `build/qbox-apollo-qvp/`로 이전됐다. topology bundle, local source
runtime과 Yocto image runtime도 이 경로 아래 서로 다른 run directory를 사용한다.
직접 부팅용 legacy runner의 `build/qbox-apollo-fvp/` 기본값은 아직 호환 부채로
남아 있으므로 full-system/FVP reference와 혼동하지 않게 실제 path, command와
revision을 result에 보존한다.

## 6. 구조적 위험과 우선순위

| 우선순위 | 구조적 gap | 실패 양상 |
| --- | --- | --- |
| 완료 | AP/SMD/RSE/SI runtime view와 broad bridge 제거 | A4 contract/source/unit/runtime으로 구조 폐쇄 |
| 완료 | 공통 request identity와 SI CL0 primary NI-710AE APU 정책 | reset/program/lock, normal/debug와 policy-aware DMI 및 protected-path boot로 폐쇄 |
| P1 | debug/direct/reentrant/DMI 대표 정책은 구현됐으나 전체 조합은 미검증 | 지원하지 않은 initiator/path 조합의 exhaustive negative matrix 필요 |
| P1 | RSE 설정, SI 검증과 AP release 정상 ownership은 연결됨 | 실패 주입별 release 차단 matrix는 후속 |
| P1 | full-system CPU 기본 4는 정렬됐으나 CPU/DRAM artifact 자동 동기화는 부분적 | DT와 machine 간 CPU/메모리 불일치 가능 |
| 완료 | GPEX requester/StreamID, LTI00 SMMUv3와 MSI/ITS route | mapped/fault DMA 및 동일 endpoint MSI-X/LPI와 INTx 증거 완료 |
| 완료 | IRQ/reset/power route manifest | topology validator와 machine contract에서 정적 검사 |
| P1 | shared backing과 address view 구분이 불명확 | 동일 메모리 복제, DMI alias incoherency 가능 |
| P1 | reset-held QK 교착은 수정됐으나 QEMU RAM owner와 4 CPU fault/reset lifecycle matrix가 부분적; KVM/16 CPU는 후속 | double mapping, backend별 reset/WFI 차이 가능 |
| P1 | SCMI/PFDI/HIPC 대표 오류/recovery는 검증됐으나 PSCI/FF-A matrix는 미검증 | peer-offline/reset-time 또는 추가 descriptor 조합의 timeout 가능 |
| 완화 | full-system QVP evidence root를 `qbox-apollo-qvp`로 이전 | direct-boot legacy 경로는 별도 정리 필요 |
| P2 | SMMU→FMU→SSU 대표 fault는 완료됐으나 watchdog/DCLS/APU source 전체 수직 경로는 부분적 | 미구현 source의 fault/reset 검증 불가 |
| P2 | FVP CFG2 CL1 scope가 hardware contract와 섞임 | reference 확장을 current silicon 필수 기능으로 오판 |
| P3 | CHI/NoC timing·contention 미모델링 | 성능·타이밍 분석에는 사용할 수 없음 |

## 7. 목표 QBox machine architecture

### 7.1 목표 topology

```text
 AP CPU(QEMU) ------ QEMU/TLM bridge --------+
 PCIe/GPEX DMA -- requester/StreamID -- SMMU +--> ap_router
 loader/debug ------- trusted capability ----+      |
                                                    +--> AP local targets
                                                    |
                                              AP->SMD ATU/APU
                                                    |
 +--------------------------------------------------v-----------+
 | system_router (52-bit system physical address only)          |
 | region 0: AP   region 1: AP/TCU   region 2: SMD              |
 | region 3: RSE  region 4: SI       others: DECERR             |
 +-----------+----------------+------------------+---------------+
             |                |                  |
       +-----v----+      +----v-----+      +-----v-------------+
       |smd_router|      |rse bridge|      |SI system bridge/APU|
       +-----+----+      +----+-----+      +-----+-------------+
             |                |                  |
       SMD NCI/devices   +----v-----+      +-----v------+ +----------+
       SRAM/RGM/PPU      |rse_router|      |si_cl0_router| |si_cl1_router|
                         +----------+      +------------+ +----------+
                                                          FVP CFG2 scope

 병렬 contract:
   signal: IRQ/MSI/LPI/fault -> GIC/NVIC/SSU/RGM/reset sink
   control: RSE configure -> SI verify/init -> AP release
   software: DT/SCMI/PSCI/PFDI/HIPC/FF-A/RAS producer <-> consumer
   evidence: source revision + artifact hash + CCI/backend + route/result
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
5. **boot ownership 강제**: reset 상태의 configuration authority는 RSE에 두고,
   RSE의 APU/ATU 설정과 SI CL0의 ATU/SCR read-back 및 CMN/GIC/peripheral
   초기화가 끝난 뒤에만 AP를 release한다.
6. **backing과 view 분리**: 하나의 SRAM/DRAM/flash backing을 여러 address view가
   공유하며, alias별 복제 메모리를 만들지 않는다.
7. **오류 응답 보존**: unmapped는 `DECERR`, reserved register는 요구에 따라
   RAZ/WI 또는 `SLVERR`로 구분하고 TLM response, QEMU `MemTxResult`와 guest
   syndrome까지 대응시킨다.
8. **설정 단일화**: CPU 수, memory bank와 enabled device는 active build
   manifest 또는 명시적 runner option에서 한 번 결정하고 result에 남긴다.
9. **QBox core 경계 보존**: 범용 router/translation 기능만 QBox core에 두고,
   Zena CSS map/policy는 `qbox-platform`에 둔다.
10. **부팅과 fidelity를 분리 판정**: Linux/Zephyr boot 성공만으로 접근 제어,
    fault, reset 또는 safety parity를 완료로 판정하지 않는다.
11. **기존 QEMU/TLM bridge 우선**: `QemuMemTxAttrsTlmExtension`, router initiator
    stamping과 MemTx/TLM error 변환을 재사용하고 중복 adapter를 만들지 않는다.
12. **request context 보존**: secure/debug, domain, initiator/requester, StreamID,
    privilege와 access kind를 CPU/DMA부터 target과 fault sink까지 전달한다.
13. **trusted access 명시**: loader/debug/direct/reentrant access는 일반 functional
    access와 구분하고 capability가 없는 `transport_dbg` policy bypass를 금지한다.
14. **QEMU/SystemC owner 단일화**: QEMU `MemoryRegion`/`AddressSpace`, `gs_memory`,
    file-backed memory 중 하나만 canonical backing을 소유한다.
15. **lifecycle을 architecture로 취급**: qdev/CPU reset, BQL, async completion,
    DMI flush, MTTCG quantum와 WFI wake ordering을 signal/reset contract에 포함한다.
16. **software ABI 동등성**: DT, SCMI/PSCI/MHU/PFDI/HIPC/FF-A/RAS의 producer와
    consumer 값, state transition 및 error termination을 검증한다.
17. **scope와 provenance 명시**: current Zena CSS, RD-Aspen variant, FVP-only
    extension과 QVP abstraction을 구분하고 모든 결과에 source/artifact hash를
    연결한다.

### 7.3 선언적 machine contract 집합

Lua 블록이 전역 table을 조립 순서대로 변경하거나 사람이 Lua와 JSON 사본을
각각 유지하지 않는다. 하나의 source model에서 runtime binding과 정렬된 JSON을
생성하거나, 기존 Lua를 source로 유지할 경우 동일 Lua를 읽는 extractor로 다음
resolved contract를 만든다.

| contract | 핵심 내용 | 대표 evidence |
| --- | --- | --- |
| topology/address | domain/view, local/system range, target/backing, bridge, width, overlap | `topology.json`, `address-routes.json` |
| transaction | initiator, secure/debug/domain, requester/StreamID, access kind, SMMU/APU와 response | `transaction-routes.json` |
| signal | PPI/SPI/MSI/LPI, reset, clock, power, FMU/SSU/RAS source/sink | `irq-routes.json`, `reset-routes.json` |
| boot/control | RSE/SI/AP owner, configure/verify/lock/release 순서 | `boot-routes.json` |
| software ABI | DT와 firmware 상수, SCMI/PSCI/PFDI/HIPC/FF-A/RAS endpoint와 shared memory | `software-routes.json` |
| artifact/runtime | source revision, artifact hash, QEMU backend/CPU/TCG, CCI, memory owner와 command | `artifacts.json`, `result.json` |

모든 block/range/route는 최소한 다음 공통 metadata를 가진다.

| 필드 | 내용 |
| --- | --- |
| `scope` | current Zena CSS, RD-Aspen variant, FVP-only extension, QVP abstraction |
| `domain` / `view` | AP, SMD, RSE, SI_CL0, SI_CL1, SYSTEM |
| `initiator` / `owner` | CPU, DMA, PCIe, loader/debug 및 boot/runtime programming owner |
| `local_base`, `system_base`, `size`, `width` | initiator view와 system-wide address constraint |
| `target` / `backing` | 실제 SystemC/QEMU target과 유일한 canonical memory owner |
| `bridge` / `access` | ATU/TCU/SMMU/APU, secure/privilege/read/write/debug policy |
| `requester` / `stream_id` | DMA/IOMMU 및 fault attribution identity |
| `response` | RAZ/WI, `DECERR`, `SLVERR`, TLM status, `MemTxResult`, guest syndrome |
| `irq`, `reset`, `clock`, `power`, `fault` | signal route와 reset-state policy |
| `dmi` / `debug` | DMI grant/clip/invalidate 및 trusted access capability |
| `fidelity` / `source` | 구현 등급과 Zena CSS 문서/FVP/source 근거 |

machine 조립은 `구성 해석 → instance 생성 → route binding → socket/signal
cardinality와 policy 검증 → topology freeze` 순서로 고정한다. SystemC elaboration
종료 시 unbound/multiply-bound socket을 실패시키고, 조립 뒤 다른 block이 기존
target priority나 stable CCI path를 변경하지 못하게 한다.

### 7.4 QBox–QEMU transaction boundary

QEMU CPU/device access는 기존 `QemuInitiatorSocket`과
`QemuMemTxAttrsTlmExtension`을 통해 TLM으로 변환한다. 목표 boundary는 다음과
같다.

1. CPU hint, secure/debug와 새 request context의 lifetime을 payload 전송 동안
   보존하고 completion 후 안전하게 정리한다.
   platform이 `secure_valid=true`로 고정한 CPU context는 QEMU attribute가 해당
   의미를 제공하지 않는 경로에서 우선하며, validity가 없을 때만
   `MemTxAttrs.secure`로 정규화한다.
2. router와 `addrtr`는 `b_transport`, `transport_dbg`, DMI에서 extension과
   original address를 보존한다. functional/debug policy 차이는 명시적
   capability로만 발생한다.
3. byte enable, streaming width, unaligned/exclusive access와 endian semantics를
   bridge가 조용히 축소하지 않는다.
4. `TLM_OK_RESPONSE`, `TLM_ADDRESS_ERROR_RESPONSE`와 기타 error를 기존
   `MemTxOK`, `MemTxDecodeError`, `MemTxError` 및 guest abort로 일관되게 전달한다.
5. GPEX/DMA는 requester/StreamID를 붙여 SMMU translation과 APU policy를 통과하고
   fault/interrupt trace에도 같은 identity가 남는다.
6. direct/reentrant/debug path는 side effect와 blocking 제한을 문서화하고 일반
   CPU/DMA가 접근 제어 우회 수단으로 사용할 수 없게 한다.

### 7.5 도메인별 목표

#### AP

- `ap_router`를 AP CPU 유무와 무관한 AP physical view의 정식 root로 만든다.
- CPU, GIC, SMMU, PCIe, DRAM, flash, AP peripheral과 RoS를 AP view에 등록한다.
- GPEX DMA는 requester/StreamID를 갖고 normative SMMU backend를 통과하며,
  alternate backend는 compatibility matrix로 검증한다.
- GPEX legacy SPI 300–303과 MSI→ITS→LPI route를 별도로 검증한다.
- AP→SMD `0x4000_0000` window는 ATU가 열린 범위만 전달한다.
- `ap_view_passthrough`의 broad 1:1 mapping을 제거한다.
- CPU 수 4와 memory bank를 deploy DTB/manifest와 대조하고 CPU4–CPU15가
  enable되지 않았음을 검사한다.
- CPU 내부 generic timer PPI와 AP REFCLK 125 MHz MMIO frame의 secure SPI 48,
  non-secure SPI 49 소유권을 중복 없이 유지한다.

#### SMD / system fabric

- `system_router`는 52-bit region decode와 width check만 담당한다.
- `smd_router`는 shared SRAM, RGM, PPU, ATU, system counter와 공용 peripheral을
  소유한다.
- NI-710AE APU의 initiator별 default-deny와 RSE override를 기능 모델로 둔다.
- SMD의 shared SRAM은 하나의 backing을 AP/RSE/SI view로 노출한다.
- SMD NCI와 SI/RSE system bridge를 manifest hierarchy에 남기고 한 router로
  flatten하지 않는다.

#### RSE

- 기존 `rse_router`를 유지하고 system bridge의 width와 access policy를 명시한다.
- RSE BL2의 image 인증·적재와 NI-710AE APU 설정, RSE-owned firmware의 모든
  ATU configuration을 서로 구분해 reset state와 연결한다.
- OTP, identity, integration, power/security control의 placeholder를 firmware가
  관찰하는 순서대로 기능 모델로 승격한다.

#### Safety Island

- CL0와 CL1에 독립 local router를 두고 각 CPU/DMA/GIC view를 분리한다.
- SI system bridge는 40-bit 범위와 ATU window만 허용한다.
- GIC view 0/1/2의 register visibility와 interrupt owner를 명시적으로 검증한다.
- FMU→SSU→GIC/reset escalation, CL0 DCLS와 CL1 SMP 차이를 signal graph에 담는다.
- SI CL0가 ATU/SCR을 read-back하고 CMN/GIC/peripheral 초기화 후 AP reset을
  release하는 control state를 모델링한다.
- FVP CFG2 CL1의 AP↔SI HIPC SRAM은 512 KiB 단일 backing과 고정
  resource-table/vring/buffer layout을 가지며 Linux는 CL1을
  `RPROC_DETACHED`로 관찰한다.
- CL1 block과 route는 `fvp_cfg2_extension` scope로 표시하고 architecture-only
  configuration에서도 validator가 동작하게 한다.
- `temporary merged bus`와 이를 위한 `lower_decode_priority()` 호출을 제거한다.

### 7.6 Memory, DMA/IOMMU와 DMI 원칙

- architectural aperture와 실제 allocated backing 크기를 별도 필드로 기록한다.
- QEMU `MemoryRegion`/`AddressSpace`, `gs_memory`, file-backed memory 중 canonical
  owner를 하나만 지정하고 같은 shared SRAM을 view별로 복제하지 않는다.
- CPU/DMA가 같은 DRAM/SRAM write를 관찰하는 순서와 barrier semantics를 1차
  functional coherency contract로 정의한다.
- GPEX requester/StreamID, IOVA translation/permission과 SMMU fault attribution을
  같은 transaction ID로 연결한다.
- `systemc-mmu720ae` 또는 `qemu-arm-smmuv3` 중 normative backend를 지정하고
  alternate backend의 호환 범위를 manifest에 기록한다.
- ATU/alias를 통과한 DMI는 반환 범위를 local window로 clip하고 주소를 역변환한다.
- backing write, APU/ATU reprogram, reset 또는 remap 시 모든 관련 alias에 DMI
  invalidation을 전파하고 deny 영역에는 DMI를 발급하지 않는다.
- NI-710AE protected DMI는 하나의 허용 region이 downstream range 전체와 모든
  요청 permission을 포함할 때만 발급하고, APU enable/live reprogram은 현재
  MMIO transaction 뒤 다음 SystemC delta에 invalidation을 병합한다.
- `b_transport`와 DMI의 data/side effect는 같아야 하며 `transport_dbg` 차이는
  명시된 debug semantics로만 허용한다.
- DRAM controller timing/ECC를 구현하지 않은 경우에도 이를 `backing`과 구분해
  fidelity ledger에 남긴다.
- single-chip과 multichip DRAM map은 하나의 고정 상수가 아니라 topology
  configuration에서 선택한다.

### 7.7 IRQ, lifecycle 및 safety topology 원칙

주소 map과 별도로 다음 route manifest를 생성한다.

- `source → sink controller → interrupt ID → security/group → owner`
- AP generic timer PPI와 AP REFCLK SPI를 별도 계층으로 유지
- GPEX INTx SPI 300–303, MSI→ITS→LPI와 SMMU event/fault route
- MHU sender/receiver와 receiver IRQ의 peer 관계
- SI GIC view별 visible frame과 CL0/CL1 interrupt 소유권
- AP corrected/deferred RAS의 TF-A/Linux FFH SPI 89와 SI uncorrected ERI 경로
- FMU input/threshold, critical/non-critical output, SCP queue, SSU FSM/ESM과
  escalation output
- RGM/PPU의 reset request/output, clock/power dependency와 cold/warm/CPU/cluster/
  domain/watchdog/fault reset state
- QEMU CPU reset state, BQL/DMI flush, async completion, quantum/WFI wake와
  simulated-time ordering

정적 검증은 중복 ID, dangling source/sink, 잘못된 controller view와 reset 후
초기 상태를 검사한다. Runtime trace는 transaction/event ID, source/sink,
simulated timestamp와 wall timestamp를 bounded form으로 기록한다.

### 7.8 System software contract

hardware contract는 firmware와 OS repository의 상수를 수동으로 복제하지 않고
producer와 consumer를 함께 검사한다.

- TF-M, SCP-firmware, TF-A, OP-TEE, U-Boot, Linux, Zephyr와 deploy DTB의 주소,
  IRQ, endpoint/channel 및 shared-memory layout을 resolved contract와 대조한다.
- RSE↔SCP boot confirmation/AP primary power, TF-A↔SCP secondary CPU/system
  power/reset, SCP→RSE notification을 SCMI owner와 channel별로 구분한다.
- Linux cpuidle/cpufreq→TF-A PSCI→SCP SCMI→PPU/clock/power의 request, ack,
  timeout과 error 전파를 유지한다.
- PFDI의 agent별 MHU/shared memory, watchdog와 FDTI, HIPC의 MHUv3/vring/RPMsg,
  FF-A endpoint/descriptor 및 RAS FFH/ERI를 success와 failure 양쪽에서 시험한다.
- secure boot image provenance, 인증/measurement와 AP/SI release condition을
  artifact hash 및 event log에 연결한다.
- DT는 TF-A가 FIP에 포함한 동일 artifact를 U-Boot/Linux가 소비해야 하며 주요
  driver probe와 SystemReady DT v3.1/ACS 결과를 보존한다.

malformed descriptor, duplicate notification, peer-offline, timeout, power/reset
중 request도 architecture test vector다. 실패는 guest/firmware가 관찰 가능한
error로 종료되어야 하며 무한 대기로 남아서는 안 된다.

### 7.9 관측성 및 evidence architecture

신규 QVP evidence의 표준 root는 `build/qbox-apollo-qvp/`로 한다.

| evidence | 필수 내용 |
| --- | --- |
| topology bundle | address/transaction/IRQ/reset/boot/software route와 source scope |
| artifact manifest | source/submodule revision, firmware/DTB/kernel/rootfs SHA-256와 provenance |
| runtime manifest | QEMU instance/backend/CPU/TCG/quantum, CCI, memory owner, command와 environment |
| bounded trace | router hit/miss/deny/error, DMI grant/invalidate, boot/control 및 fault event |
| optional telemetry | simulated/wall time은 hang 진단용이며 성능 acceptance에 사용하지 않음 |
| focused comparison | artifact hash 차이와 FVP/QVP boot 및 변경 marker의 scope-aware verdict |

full-system runner/README/audit 기본값은 `build/qbox-apollo-qvp/`로 이전했다.
기존 결과를 rename해 현재 증거처럼 만들지 않으며, 모든 bundle은 실제 root,
schema version, 생성 command와 timestamp를 기록한다.

## 8. 목표 fidelity와 비목표

### 8.1 1차 목표

- software-visible memory map 및 domain별 address view 일치
- CPU/GPEX DMA의 transaction identity, SMMU/ATU/APU 허용·차단과 guest 오류 응답
- interrupt/MSI/LPI, reset, power, MHU, RAS와 safety fault의 관찰 가능한 side effect
- RSE configure→SI verify/init→AP release ownership과 QEMU lifecycle ordering
- FVP와 같은 firmware/OS boot handoff, software ABI와 driver probe
- artifact provenance, topology/route/result와 UART log 증거

### 8.2 명시적 비목표

- CMN/NI의 cycle-accurate arbitration, CHI packet timing과 contention
- 실제 DRAM PHY, analog PLL 또는 PMIC의 전기적 동작
- FVP 자체가 모델링하지 않는 모든 CoreSight/trace block
- silicon 성능 수치의 예측
- ISO 26262 safety certification 또는 실제 fault coverage 수치의 대체

이 비목표는 주소를 broad memory로 채워도 된다는 뜻이 아니다. software가
접근하는 register와 fault/interrupt effect는 별도의 fidelity 상태로 관리한다.

## 9. Architecture 완료 조건

MVP 완료에는 G0–G6을 요구한다. G7은 수행하거나 `deferred` 사유를 기록한다.
각 gate의 실행 순서와 세부 task는 연계 plan을 따른다.

| Gate | Architecture 완료 조건 |
| --- | --- |
| G0 contract/static | single-source contract가 address/transaction/signal/boot/software/artifact JSON을 생성하고 overlap, scope, socket/signal, ABI drift와 core boundary 검사가 통과 |
| G1 QBox/TLM | payload extension과 response mapping, `b_transport`/`transport_dbg`/DMI policy, stable CCI 및 bounded trace가 단위 검증됨 |
| G2 domain/boot | AP/SMD/RSE/SI view가 분리되고 reset default-deny, RSE APU/ATU 설정, SI read-back/init와 AP release 순서가 positive/negative test로 증명됨 |
| G3 memory/DMA/IOMMU/QEMU | canonical backing owner, DMI invalidation, GPEX requester/StreamID, SMMU translation/fault와 guest syndrome이 일치 |
| G4 signal/lifecycle/safety | PPI/SPI/MSI/LPI, qdev reset/BQL/async/quantum, power, FMU/SSU/RAS 상태 전이와 reset-state 검증이 통과 |
| G5 system software/ABI | DT, SCMI/PSCI/MHU/PFDI/HIPC/FF-A/RAS의 producer-consumer 및 success/error path가 일치 |
| G6 QBox full-system smoke | RSE, SI, AP boot, 4 CPU correctness와 coverage audit가 local/Yocto에서 각각 한 번 통과 |
| G7 focused FVP comparison | boot milestone과 변경한 대표 marker를 비교하거나 실행 제약과 `deferred` 사유를 기록 |

2026-07-17 현재 판정은 G0/G1/G2/G3/G6 `pass`, G4/G5 `partial`, G7
`pass(non-AP focused scope)`다. G4는 선택한 SMMU→FMU→SSU와 PCIe interrupt
slice를 통과했지만 watchdog/DCLS/APU fault source 전체가 아니며, G5는
SCMI/PFDI/HIPC 대표 recovery를 통과했지만 PSCI/FF-A 전체 error matrix가 아니다.
G7은 기록된 RSE/SI0/SI1 로그와 변경 marker 비교를 완료했지만 AP는 요청 범위에서
제외했고 자동 same-artifact whole-system differential은 extended gate다. 따라서
이번 4 CPU MVP는 완료했으나 Apollo FVP 전체 safety/software equivalence를
주장하지 않는다.

추가로 다음 조건은 gate 결과와 무관하게 필수다.

- broad AP passthrough, `temporary merged bus`와 도메인 충돌 해소용 runtime
  priority 변경이 소스에 남아 있지 않다.
- placeholder와 미구현 블록이 이름, 주소, software 영향, scope와 대체 계획을
  fidelity ledger에 가진다.
- 신규 QVP evidence는 `build/qbox-apollo-qvp/`에 있고 기존
  `build/qbox-apollo-fvp/` 결과와 provenance로 구분된다.
- source revision, command, artifact hash, resolved CCI/backend, logs와 verdict가
  하나의 evidence bundle에 연결된다.

## 10. 근거 파일

### 10.1 Arm Zena CSS block/boot/software architecture

| 근거 | 이 문서에서 사용한 항목 |
| --- | --- |
| [`02-block-diagram-for-zena-css.md`](arm_zena_css_dev_guide/02-block-diagram-for-zena-css.md), [`figure-2-1`](arm_zena_css_dev_guide/assets/figure-2-1-zena-css-high-level-block-diagram.png) | AP/RSE/SI/Debug와 CMN/NCI/NI 및 외부 memory/I/O 경계 |
| [`aspen_high_level_arch.png`](../arm-zena-css/documentation/images/aspen_high_level_arch.png), [`aspen_system_management_block.png`](../arm-zena-css/documentation/images/aspen_system_management_block.png), [`aspen_compute_complex.png`](../arm-zena-css/documentation/images/aspen_compute_complex.png) | SMD/SI NCI, GIC/ATU, I/O TCU/TBU/ITS 및 계층형 fabric |
| [`components.rst`](../arm-zena-css/documentation/design/components.rst), [`09-programmers-model-for-zena-css.md`](arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) | system-wide map, domain address width, RSE ATU ownership과 register contract |
| [`06-boot-flow-of-zena-css.md`](arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md), [`rse_oriented_boot_flow.png`](../arm-zena-css/documentation/images/rse_oriented_boot_flow.png), [`safety_boot.rst`](../arm-zena-css/documentation/design/safety_boot.rst), [`boot_process.rst`](../arm-zena-css/documentation/design/boot_process.rst) | RSE image/APU/ATU, SI verify/init와 AP reset release ownership |
| [`scmi_comm_rse_tfa_scp.png`](../arm-zena-css/documentation/images/scmi_comm_rse_tfa_scp.png), [`power_and_performance_control.rst`](../arm-zena-css/documentation/design/power_and_performance_control.rst) | SCMI/PSCI power/reset/performance control 경로 |
| [`si_gic_multiple_view.png`](../arm-zena-css/documentation/images/si_gic_multiple_view.png), [`pc_domain_reset.png`](../arm-zena-css/documentation/images/pc_domain_reset.png) | SI GIC view와 AP reset state graph |
| [`fmu.rst`](../arm-zena-css/documentation/design/fmu.rst), [`ssu.rst`](../arm-zena-css/documentation/design/ssu.rst), [`ras.rst`](../arm-zena-css/documentation/design/ras.rst), [`fmu_ssu_integration.png`](../arm-zena-css/documentation/images/fmu_ssu_integration.png) | FMU threshold/queue, SSU FSM/ESM, AP FFH SPI 89와 SI ERI |
| [`platform_fault_detection_interface.rst`](../arm-zena-css/documentation/design/platform_fault_detection_interface.rst), [`platform_fault_detection_interface.png`](../arm-zena-css/documentation/images/platform_fault_detection_interface.png) | PFDI MHU/shared memory, watchdog, SCMI `0x90`와 FDTI |
| [`hipc.rst`](../arm-zena-css/documentation/design/hipc.rst), [`systemready_devicetree.rst`](../arm-zena-css/documentation/design/systemready_devicetree.rst) | HIPC 512 KiB ABI, detached remoteproc와 DT/SystemReady 계약 |
| [`08-fixed-virtual-platform.md`](arm_zena_css_dev_guide/08-fixed-virtual-platform.md) | FVP CFG2 SI CL1 extension scope |

FVP 구성 근거는
[`fvp-rd-aspen.conf`](../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf)와
[`fvp.inc`](../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc)을
함께 사용한다.

### 10.2 활성 build 설정

- [`build/conf/local.conf`](../build/conf/local.conf)
- [`build/conf/bblayers.conf`](../build/conf/bblayers.conf)
- [`build/conf/templateconf.cfg`](../build/conf/templateconf.cfg)

### 10.3 현재 QVP platform

- [`apollo-qvp.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua)
- [`fabric.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/fabric.lua)
- [`ap_compute.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua)
- [`system_mgmt.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua)
- [`si_cl0.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua)와
  [`si_cl1.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua)
- [`config.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua)
- [`machine_contract.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/machine_contract.lua),
  [`topology.lua`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/topology.lua)와
  address/transaction/signal/boot/software contract
- [Apollo platform README](../hsoc-stack/tools/qbox-platform/platforms/apollo/README.md)
- [`run_qbox_apollo_fvp_full.py`](../scripts/run/run_qbox_apollo_fvp_full.py)와
  [`audit_qbox_apollo_fvp_full_coverage.py`](../scripts/test/audit_qbox_apollo_fvp_full_coverage.py)
- [`validate_qbox_apollo_topology.py`](../scripts/test/validate_qbox_apollo_topology.py)

### 10.4 QBox/SystemC/QEMU boundary

- QBox [`router.h`](../hsoc-stack/tools/qbox/systemc-components/router/include/router.h)와
  [`addrtr.h`](../hsoc-stack/tools/qbox/systemc-components/addrtr/include/addrtr.h)
- [`qemu-memtx-attrs.h`](../hsoc-stack/tools/qbox/qemu-components/common/include/tlm-extensions/qemu-memtx-attrs.h)
- QEMU initiator [`initiator.h`](../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h)와
  [`libqemu-cxx.h`](../hsoc-stack/tools/qbox/qemu-components/common/include/libqemu-cxx/libqemu-cxx.h)
- CPU [`cpu.h`](../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h)와
  QEMU instance [`qemu-instance.h`](../hsoc-stack/tools/qbox/qemu-components/common/include/qemu-instance.h)
- GPEX [`qemu_gpex.h`](../hsoc-stack/tools/qbox/qemu-components/pci/qemu_gpex/include/qemu_gpex.h)

기존 [Apollo FVP-QVP Hardware Comparison KR](apollo-fvp-qvp-hardware-comparison-ko.md)와
[Apollo QBox Hardware KR](apollo-qbox-hardware-ko.md)은 subsystem별 상세 목록을
제공한다. 다만 현재 source revision과 다른 설명이 있을 수 있으므로 구현 상태는
위 revision의 Lua/SystemC/QEMU 소스를 최종 기준으로 삼는다.

## 11. Improvement plan 정합 및 검증 상태

Architecture 문서는 목표 구조와 불변 contract를 정의하고, 연계 plan은 이를
구현하는 순서, task와 gate를 정의한다.

### 11.1 A0–A8 traceability

| plan phase | architecture 근거 |
| --- | --- |
| A0 기준선 | 3장 revision/build 기준, 5.8 evidence root, 7.9 artifact/runtime provenance |
| A1 contract/QBox-TLM | 7.3 contract 집합, 7.4 transaction boundary와 elaboration/topology freeze |
| A2 AP view | 7.1 AP/QEMU/GPEX 경로와 7.5 AP 목표 |
| A3 SI view | 4.1 CFG2 scope, 7.5 Safety Island local view/HIPC/GIC 목표 |
| A4 system/SMD/APU/ATU | 4.4 fabric, 4.5 boot ownership, 7.5 SMD/RSE/SI 목표 |
| A5 memory/DMA/IOMMU/QEMU | 5.6 current lifecycle gap과 7.6 owner/SMMU/DMI 원칙 |
| A6 IRQ/reset/timing/safety | 5.7 current route gap과 7.7 signal/lifecycle/safety topology |
| A7 model/software ABI | 4.6 software-visible contract, 7.8 protocol/error contract와 8장 fidelity |
| A8 differential/완료 | 7.9 evidence, 8장 scope, 9장 G0–G7 완료 조건 |

Architecture 또는 plan 중 하나를 변경하면 이 traceability, G0–G7 이름, evidence
root와 scope classification을 함께 검사한다.

### 11.2 2026-07-16 A4 구현 및 검증

```text
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
  -> passed: true

python3 scripts/test/validate_qbox_apollo_topology.py
  -> status: pass; 9 JSON evidence files generated

python3 scripts/test/audit_qbox_core_boundary.py
  -> QBox core boundary audit passed

ctest --test-dir build/qbox-core-tests \
  -R '^aarch64-start-in-reset-release-test$' --repeat until-fail:50
  -> 50/50 passed

./local_build.sh qbox --qbox-unit-tests
  -> QBox/QBox-platform build passed; SystemC component tests 33/33 passed

make -f Makefile.cmake mod_test BUILD_PATH=<repo>/build/tests/scp-firmware-unit
  -> SCP module tests 77/77 passed; transport 24 tests passed

local full-system runtime x5
  -> 5/5 passed; coverage audit 5/5 passed
  -> RSE/SI CL0/SI CL1/AP/Linux login observed

post-review local acceptance x2
  -> resolved `maxcpus=4`; Linux 4 CPUs online, 49/49 coverage
  -> SMD-owned SCMI SRAM survived AP reset; QVP/FVP SCMI v2.0 marker matched,
     49/49 coverage

./yocto_build.sh
  -> 7,290 tasks attempted, 7,259 did not rerun, all succeeded

Yocto provider/firmware/nexios-image WIC full-system runtime x3
  -> 3/3 passed; coverage audit 3/3 passed

secure pending-mailbox fix trace-off local runtime x3
  -> 3/3 passed; PFDI ready (4 CPUs); coverage audit 3/3, each 49/49

secure pending-mailbox fix trace-off Yocto runtime x3
  -> 3/3 passed; PFDI/4 CPU/SCMI v2.0/login; each 49/49 coverage
```

상세 command, artifact와 판정은
[2026-07-16 아키텍처 부채 구현·검증 보고서](apollo-qvp-architecture-debt-validation-2026-07-16.md)에
기록한다. 이 결과는 A4 broad bridge 제거, SMD runtime router, 실제 ATU/TBU
route, reset-held CPU lifecycle과 두 image 계열의 정상 boot를 증명한다. 당시
미완료였던 APU/request context, 대표 software ABI error와 safety fault slice는
아래 I0~I7 단계에서 보강했다. 동일 artifact 전체 FVP differential G7은 여전히
완료로 판정하지 않는다. secondary SCMI protocol은 기존 FVP log와 focused
differential을 완료했다.

### 11.3 2026-07-17 I0~I7 구현 및 검증

I0~I6은 다음 최소 수직 slice를 닫았다.

| 단계 | 구현 결과 | 검증 결과 |
| --- | --- | --- |
| I0 | CFG2 4 CPU와 artifact provenance contract | CPU0~CPU3, CPU4 이상 비활성 validator pass |
| I1 | 공통 TLM request context와 QEMU/loader/router 전달 | request-context CTest pass |
| I2 | primary NI-710AE reset/program/lock/permission과 DMI | component CTest 및 protected-path full boot pass |
| I3 | MMU-720AE LTI00를 공용 SMMUv3 owner와 결합 | mapped DMA, EVTQ/IRQ와 TLBI pass |
| I4 | endpoint requester `0x0008`, SID `0x40`, ITS/LPI와 INTx | 같은 endpoint의 MSI-X와 `pci=nomsi` runtime pass |
| I5 | opt-in SMMU event fanout, FMU record/IRQ와 SSU sink | clear/recovery JSON 및 component test pass |
| I6 | malformed SCMI/PFDI와 invalid HIPC descriptor | channel FREE/bounded poll 뒤 정상 재시도 pass |

통합 gate는 다음 두 artifact family를 독립적으로 실행했다.

```text
./local_build.sh qbox --qbox-unit-tests --no-package --jobs 8
  -> QBox-platform SystemC component tests 33/33 passed

scripts/run/run_qbox_apollo_fidelity.py --artifacts local --cpus 4
  -> build/qbox-apollo-qvp/fidelity-4cpu-local-20260717
  -> runtime/coverage/contract pass, Linux CPU IDs [0,1,2,3]

./yocto_build.sh
  -> 7,293 tasks attempted, all succeeded

scripts/run/run_qbox_apollo_fidelity.py --artifacts yocto --cpus 4
  -> build/qbox-apollo-qvp/fidelity-4cpu-yocto-20260717
  -> runtime/coverage/contract pass, Linux CPU IDs [0,1,2,3]
```

두 manifest의 `artifact_family_errors`는 빈 배열이다. 이 I0~I7 acceptance
시점에는 계획한 comparison script와 실행 binary가 없어 focused FVP 비교를
`deferred`로 기록했다. 이후 확보한 기록 로그로 수행한 비-AP differential과
PFDI 수정 결과는 11.4에서 별도로 판정한다. 상세 근거는
[I7 완료 보고서](apollo-qvp-fidelity-stages/i7-integration-validation-completion-2026-07-17-ko.md)에
기록한다.

### 11.4 2026-07-17 비-AP FVP/QBox differential과 PFDI timing closure

사용자가 지정한 FVP
`build/fvp-tmux/apollo-qvp-20260717-091507/uarts/`와 수정 전 QBox
`build/qbox-apollo-qvp/yocto-apollo-qvp-20260717-091350/`의 RSE, SI0,
SI1 로그를 비교했다. AP 오류는 이 판정에서 제외했다.

| domain | FVP | 수정 전 QBox | 수정 후 QBox |
| --- | --- | --- | --- |
| RSE | CC3XX `PIDR0=0xc1` 유지 | BL2 이후 `PIDR0=0x0` | read-only ID write 보호 뒤 `0xc1` 유지 |
| SI0 | PFDI monitor가 SI1 core 0~3 감시 | 같은 monitor/service 동작 | 같은 동작 유지 |
| SI1 | OoR 0~3, PFDI ready 4 CPUs, network ready, 오류 없음 | core 1/3 status timeout과 `ret=-116` | 같은 정상 marker, timeout 4종 없음 |

원인은 PFDI register나 SI0 service 누락이 아니라 별도 SI0/SI1 QEMU instance의
virtual-time 진행 차이였다. SI1이 PBX doorbell을 게시한 뒤 SI0 firmware response가
shared memory에 반영되기 전에 requester의 guest timeout deadline이 진행했다.
계측 결과 초기 protocol setup의 channel 2~5는 모두 CPU0가 발행하고, 이후
steady-state status만 channel 2/3/4/5와 CPU 0/1/2/3이 대응했다.

수정된 timing boundary는 다음과 같다.

```text
SI1 vCPU --RequestContext(requester_id)--> PFDI PBX
        --doorbell/shared memory---------> SI0 SCP-firmware
        --sync_hold(requester)----------> 요청 vCPU/QK 정지

SI0 response: channel FREE
        --requester release-------------> 같은 SI1 vCPU/QK 재개
```

`sync_hold`는 architectural halt/reset/power 신호가 아니며 guest-visible state를
변경하지 않는다. MHU model도 response를 합성하지 않고 실제 SI0 firmware가
channel을 `FREE`로 전이할 때만 requester를 해제한다. 이 설계는 service ownership,
doorbell, IRQ와 firmware ABI를 보존하면서 cross-instance deadline만 정렬한다.

검증 결과는 다음과 같다.

```text
./local_build.sh qbox --qbox-unit-tests --no-package --jobs 16
  -> QBox-platform component tests 33/33 passed

local full-system trace-off runtime r2/r3
  -> 2/2 passed; SI1 PFDI error gates all false
  -> r3 full coverage audit passed

bitbake qbox-apollo-qvp-native
  -> 1,056 tasks attempted; all succeeded; do_check passed

run_qbox_yocto.sh ... pfdi-requester-context-yocto-20260717-r1
  -> provider executable/Lua + nexios-image WIC boot passed
  -> SI1 PFDI error gates all false; coverage passed
```

SI0 CMN discovery는 FVP의 RN-SAM/HN-S/RN-D/RN-F/RN-I `21/8/3/8/8`과
CCG RA/HA/LA `2/2/2` 대신 QBox에서 `1/8/0/1/0`, `0/0/0`을 보고한다.
이는 이번 PFDI timeout의 원인은 아니지만 CMN topology/revision fidelity 부채로
남긴다. 상세 로그, 구현 파일과 명령은
[비-AP 로그 비교 및 PFDI 수정 보고서](apollo-qvp-fvp-qbox-non-ap-pfdi-analysis-2026-07-17-ko.md)에
기록한다.

## 12. 4 CPU Fidelity 단계와 후속 범위

구조적 A4 전환 뒤 기능 부채는 다음 세 문서를 단일 실행 계약으로 사용했으며,
I0~I7 최소 범위는 완료했다.

1. [Fidelity 부채 아키텍처 설계](apollo-qvp-fidelity-debt-architecture-design-ko.md)는
   request identity, NI-710AE APU, MMU-720AE/SMMUv3, MSI/ITS/LPI, fault plane과
   software ABI의 목표 구조와 불변 조건을 정의한다.
2. [Fidelity 부채 구현 계획](apollo-qvp-fidelity-debt-implementation-plan-ko.md)은
   I0–I8 수직 slice, owning repository, atomic commit과 중단 기준을 정의한다.
3. [Fidelity 부채 검증 계획](apollo-qvp-fidelity-debt-validation-plan-ko.md)은
   V0–V9 최소 smoke gate, 대표 오류/recovery와 단일 실행 evidence를 정의한다.

이번 후속 단계의 AP acceptance는 active Yocto와 같은 CPU0–CPU3, 총 4 CPU다.
CPU4–CPU15 online, 16 CPU lifecycle과 KVM은 완료 조건에 포함하지 않는다. 4 CPU의
대표 보안·DMA·interrupt·fault·ABI 경로와 local/Yocto smoke는 완료했다. 전체
matrix, watchdog/DCLS/APU fault source 확대, PSCI/FF-A negative matrix와 FVP
differential은 extended validation으로 관리한다.
