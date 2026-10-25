# 05.1 FVP/QBox 비교 baseline과 artifact 계약

> **학습 목표:** 공통 guest contract와 machine별 model·firmware·DTB·evidence 조건을 구분한다.
> Source 기준: 2026-10-25 checkout. 이 장의 작성·분할 검증에서는 build와 runtime을 실행하지 않았다.

[상위 장](../05-fvp-qbox-comparison.md) · [전체 목차](../README.md) · [이전: 05 개요](../05-fvp-qbox-comparison.md) · [다음: Topology와 device mechanism](02-topology-device-mechanisms.md)

## Arm 원본 block diagram에서 비교 단위를 찾기

![Arm reference Compute Complex — native draw.io 재작성](../figures/reference/aspen_compute_complex.drawio.svg)

[draw.io 편집 원본](../figures/reference/aspen_compute_complex.drawio)

Native draw.io 재작성 기준: Arm [Components — System Block Diagram](../../../../arm-zena-css/documentation/design/components.rst),
[`aspen_compute_complex.png`](../../../../arm-zena-css/documentation/images/aspen_compute_complex.png).
**Apollo delta:** 이 그림의 물리적 block 관계를 출발점으로 삼되,
QVP는 programmable register·memory view·IRQ·reset 계약을 QEMU와 SystemC 모델에 나누어 구현한다.

그림은 왼쪽 AP cluster, 중앙 GIC/I/O, 오른쪽 RSE/Safety Island,
아래 CMN과 expansion interface의 순서로 읽는다.
SW가 어느 core에서 실행되는지만 보면 놓치는 것이 **domain을 건너는 접근의 소유자**다.
AP의 PCIe DMA, RSE의 AP image 적재, SCP의 AP PPU 제어는 서로 다른 initiator다.

| 원본 그림의 위치 | SW 관점의 질문 | QVP에서 이어서 볼 객체 |
|---|---|---|
| AP cluster / DSU | CPU가 어떤 DRAM·peripheral view를 보는가? | `ap_cpu_N`, `ap_router` |
| CMN / NCI | 주소 decode, 보호·설정, coherent traffic 중 무엇을 모델링하는가? | router, ATU, `host_cmn_cyprus`, `host_ni710ae_nci` |
| I/O TCU / TBU / ITS | DMA 주소 변환과 MSI interrupt는 어디서 처리하는가? | `ap_smmu_0`, `ap_smmu_lti00`, `ap_gic_multiview.its` |
| RSE / Safety Island | 누가 image를 준비하고 power/reset을 해제하는가? | TF-M, SCP, loader, `host_ppu` |
| Peripheral / Board | MMIO target과 외부 부품 연결은 어디에 있는가? | `soc/hw-block/ros`, `board/saturn-v.lua` |

Arm [Overview — Architectures](../../../../arm-zena-css/documentation/overview.rst)는
baremetal PREEMPT_RT Linux와 Xen virtualization 구성을 모두 설명한다.
현재 local build의 baremetal 구성에서 그려진 Linux 하나를 전체 reference의 유일한 배치로 일반화하지 않는다.
이 장은 local cfg2 full-system을 중심으로 **IP 대응 → programming view → 실제 protocol 사례**를 비교한다.

## 비교의 중심은 guest가 보는 계약

![공통 SW 계약을 구현하는 FVP와 Apollo QVP](../diagrams/05-fvp-qbox.drawio.svg)

[draw.io 편집 원본](../diagrams/05-fvp-qbox.drawio)

[기존 HTML 보기](../diagrams/05-fvp-qbox.html)

**FVP와 QBox를 비교할 때는 동일한 기능 요구를 각각의 model과 image 조합에서 확인한다.**
CPU 실행 엔진이나 host elapsed time이 같아야 하는 것은 아니다.

| 비교 층 | FVP | Apollo QVP | 비교할 항목 |
|---|---|---|---|
| 실행 엔진 | Arm Fast Models 기반 FVP executable | QEMU/libqemu TCG + SystemC/TLM | ISA·exception·register 의미 |
| 조합 방식 | 제공된 topology + FVP parameter | SoC/VP/Board Lua + CCI + C++ model | CPU 수, address view, IRQ, reset |
| Guest SW | RD-Aspen reference stack 및 project 통합 | project의 QVP 통합 firmware·OS | boot, PSCI/SCMI, FF-A, IPC, driver |
| 관찰 도구 | UART, Iris/Cornea, model trace | UART, GDB, QMP, monitor, TLM/model trace | 동일한 성공·실패 조건 |
| 시간 | 각 FVP model의 시간 의미 | QEMU virtual clock + SystemC 시간 정책 | 기능 deadline과 순서; silicon 성능은 별도 |

FVP도 SW 개발용 기능 platform이다. FVP라는 이름만으로 cycle-accurate 또는 physical timing 모델이라고 설명하지 않는다.
Arm [User Guide — Reproduce / FVP](../../../../arm-zena-css/documentation/user_guide/reproduce.rst)도
FVP의 목적을 기능 확인으로 설명하고 performance 분석과 구분한다.

근거: [Zena FVP 설명](../../../arm_zena_css_dev_guide/08-fixed-virtual-platform.md),
[QBox 실행 구조](../04-qbox-runtime-and-lua.md),
[Arm reference component 설명](../../../../arm-zena-css/documentation/design/components.rst).

## 먼저 맞춰야 할 configuration

| 항목 | 참조·선택지 | 현재 local source/config에서 확인한 값 |
|---|---|---|
| Machine | Arm reference `fvp-rd-aspen`; project `apollo-fvp` / `apollo-qvp` | `build/conf/local.conf`: `apollo-qvp` |
| FVP variant | Cfg1: SI 단일 cluster / Cfg2: SI 두 cluster | `RD_ASPEN_VARIANT = "cfg2"` |
| FVP executable | variant include가 결정 | cfg2 include: `FVP_Zena_CSS_Cfg2` |
| AP population | reference topology 최대 4 cluster × 4 PE | `PC_CPUS_COUNT_DEFAULT = "4"` |
| QVP DTB | 4 PE / 16 PE 명시 선택 | `APOLLO_QVP_DTB`가 `PC_CPUS_COUNT`로 선택 |
| SI CL0 | system management cluster | QVP functional PE 1개 |
| SI CL1 | Cfg2의 4-core SMP cluster | QVP PE 4개 |

`??=`/`?=` 값은 metadata default이며 환경·override·다른 include로 바뀔 수 있다.
위 표는 현재 파일을 읽은 snapshot이고 새 `bitbake -e` 결과는 아니다.
실제 비교에서는 `.fvpconf`/`.qboxconf`, DTB, firmware와 실행 manifest의 최종값을 함께 확인한다.

근거: [local.conf](../../../../build/conf/local.conf),
[FVP machine](../../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf),
[Cfg2 include](../../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc),
[QVP machine](../../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf).

`run_fvp.sh`는 기본 `apollo-fvp`를 선택하고 `--machine apollo-qvp`도 지원한다.
후자는 matching QVP machine artifact를 FVP에서 비교할 수 있는 project 경로다.
이 경우도 model이 자동으로 QBox topology로 바뀌는 것은 아니며,
FVP parameter와 해당 artifact의 compatible device/firmware 계약이 비교의 전제다.

근거: [Apollo FVP machine](../../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-fvp.conf),
[project FVP launcher](../../../../run_fvp.sh),
[Arm Integration — meta-zena-css-bsp](../../../../arm-zena-css/documentation/design/integration.rst).

## Firmware는 공통 역할을 유지하고 artifact는 machine별로 선택한다

| 역할 | 공통 SW 구성 | FVP 입력 | QVP 입력 |
|---|---|---|---|
| Root of Trust | TF-M RSE boot/runtime | FVP ROM/flash/NVM parameter | runner의 RSE ROM/flash/OTP 입력 |
| System management | SI CL0 SCP | firmware package와 SI load contract | `si0_ramfw.bin`, MHU/PPU/reset wiring |
| Real-time service | SI CL1 Zephyr | Cfg2 SI image | CL1 binary/ELF, shared-memory·MHU topology |
| Secure monitor / Trusted OS | TF-A, OP-TEE, Trusted Services | FVP용 AP firmware package | QVP용 AP firmware package |
| Bootloader / Linux | U-Boot, kernel, rootfs | FVP DTB, `.wic`, `.fvpconf` | QVP DTB, `.wic`, `.qboxconf` |

QVP machine은 `fvp-rd-aspen` metadata를 상속하면서 firmware provider, kernel machine,
QVP DTB, QBox timing 설정을 바꾼다. 따라서 source 공통성이 크지만 배포 산출물을 무조건 교환할 수는 없다.
예를 들어 AP CPU 수는 firmware의 PSCI/SCMI topology, DTB의 CPU node,
QBox CPU/GIC population이 함께 맞아야 한다.

**공통 boot 의존성:** RSE의 image 검증·적재 → SI CL0 준비와 전원 제어 → AP boot chain,
그리고 Cfg2의 SI CL1 실행. 세부 handoff는 [Domain SW Architecture](../06-component-software-architecture.md)를 참고한다.

근거: [FVP artifact parameter](../../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc),
[QVP machine override](../../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf),
[QVP launcher image 선택](../../../../run_qbox_yocto.sh),
[reference boot process](../../../../arm-zena-css/documentation/design/boot_process.rst).

Reference `fvp.inc`는 ROM, RSE flash, OTP/NVM, AP flash, WIC를 각각 model parameter에 연결한다.
QVP는 같은 역할의 입력을 `.qboxconf`와 runner 인자로 전달하고 loader/backend가 소비한다.
Arm의 [Boot process — Image layouts](../../../../arm-zena-css/documentation/design/boot_process.rst)에 나오는
signed firmware package와 disk image를 구분해야 한다.
RSE flash의 image slot을 바꾼 것과 WIC의 Linux rootfs를 바꾼 것은 영향을 주는 boot 단계가 다르다.

| 비교 준비 | FVP에서 남길 값 | QVP에서 남길 값 |
|---|---|---|
| 실행기 | executable/version, variant | native provider executable/library hash |
| Config | generated `.fvpconf`, model parameter | `.qboxconf`, 실제 installed Lua, CCI/env override |
| Boot input | ROM/flash/OTP/WIC hash | 같은 역할의 input 및 실행 중 writable-state hash |
| SW topology | firmware/DTB의 CPU·GIC·memory 설정 | AP PE 수, GIC geometry, DTB와 loader entry |

비교는 양쪽이 동일 byte image를 반드시 쓰는 방법과,
동일 source/config 의도를 machine별 artifact로 조립하는 방법을 구분해서 기록한다.
QVP board peripheral 추가나 timing integration이 포함되면 후자의 비교가 필요하다.

## 비교 baseline은 한 파일이 아니라 일치시킬 계약이다

같은 Linux banner가 출력되어도 CPU population, secure firmware, board device가 다를 수 있다.
비교를 시작할 때는 **어떤 guest 동작을 같은 조건에서 확인할 것인지**를 먼저 정한다.
그 동작을 만드는 firmware·DTB·model parameter를 한 묶음으로 남겨야 결과를 다시 해석할 수 있다.

| 계약 | 예시 | 일치하지 않을 때 생기는 결과 |
|---|---|---|
| CPU / interrupt topology | AP4, SI CL1 4 PE, MPIDR, redistributor | secondary CPU boot 또는 IRQ 대상 불일치 |
| Memory / device view | AP SRAM, MHU address, SMMU register | abort, 잘못된 target, shared-memory 오해 |
| Firmware ABI | PSCI, SCMI, FF-A, mailbox channel | Linux는 부팅하나 service 요청 실패 |
| Boot / persistent state | RSE ROM·flash·OTP, AP flash, writable storage | 인증·provisioning 단계에서 결과 차이 |
| OS packaging | WIC의 kernel/DTB/UKI/rootfs | 같은 source라고 생각한 run의 실제 driver 차이 |
| Test semantics | profile selector, assertion ID, traffic 조건 | 같은 PASS 표시가 서로 다른 기능을 의미 |

“동일 byte image 비교”는 input 자체를 맞추는 방법이다.
“동일 guest contract 비교”는 machine별 image가 달라도 공통 protocol과 assertion을 맞추는 방법이다.
이 둘을 비교 보고서에서 구분하면 QVP용 DTB나 board integration의 차이를 설명할 수 있다.
Named validation gate는 후자의 semantic 계약과 각 실행 input의 무결성을 별도 항목으로 검사한다.

### 설정 변경은 어디까지 전파되는가: AP4 → AP16 사고 실험

AP vCPU 12개를 더 생성하는 것만으로 완성되지 않는다.
CPU interface, firmware topology, Linux CPU node가 서로 같은 population을 가리켜야 한다.

| 계층 | 확인할 사항 | 관련 source |
|---|---|---|
| Model | AP CPU descriptor 수, GIC redistributor, MPIDR | `soc/hw-block/ap_compute/cpu.lua`, `system.lua` |
| Firmware | PSCI core/cluster topology, SCMI performance domain | machine CPU count와 TF-A/SCP 구성 |
| OS | 4/16 variant DTB, CPU·GIC nodes | `APOLLO_QVP_DTB`, Linux DTS |
| Runner / test | expected CPU count와 profile 요구 | `expected_ap_cpus()`, validation matrix |

현재 문서의 local snapshot은 AP4다.
AP16 source·static evidence가 있다는 사실은 AP16 full-system runtime을 이 문서에서 수행했다는 뜻이 아니다.
CPU 수가 달라지면 SMP나 timer 시험의 expected assertion 조건도 함께 검토한다.

근거: [QVP machine/DTB 선택](../../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf),
[AP CPU topology](../../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua),
[full runner](../../../../scripts/run/run_qbox_apollo_fvp_full.py),
[profile provenance의 CPU 검사](../../../../scripts/validation/apollo_validation/provenance.py).

## Launcher의 유연성과 비교 gate의 허용 범위는 다르다

`run_fvp.sh --machine apollo-qvp`는 matching QVP artifact를 FVP에서 살펴볼 수 있는 launcher 경로다.
반면 현재 named validation의 `validate_fvp_reference()`가 수락하는 reference summary는
`backend=fvp`, `machine=apollo-fvp`여야 한다.
Launcher가 어떤 조합을 실행할 수 있다는 것과 그 결과를 named 비교의 reference로 수락하는 것은 별개다.

| 실행 / 결과 경로 | 의미 | 적합한 활용 |
|---|---|---|
| FVP + `apollo-fvp` named profile | gate의 정규 reference 후보 | 동일 profile의 QVP 비교 |
| FVP + `apollo-qvp` artifact 조사 | launcher가 지원하는 별도 조합 | machine artifact 호환성 조사 |
| QVP standalone named profile | 허용 policy에서 QVP 독립 검증 | FVP 비교 전 또는 독립 기능 증거 |
| QVP + accepted FVP reference | provenance와 assertion gate 통과 | 해당 profile 범위의 비교 |

`summary.json`에 PASS라는 문자열이 있다는 이유만으로 두 번째 결과를 첫 번째로 바꾸어 읽지 않는다.
Machine, profile, CPU count와 shared input 조건을 모두 확인하는 과정은
[05.3 evidence와 진단](../05-comparison/03-evidence-and-diagnosis.md)에서 자세히 다룬다.

근거: [FVP launcher](../../../../run_fvp.sh),
[reference 수락 조건](../../../../scripts/validation/apollo_validation/fvp_reference.py),
[standalone policy](../../../../scripts/validation/apollo_validation/reference_policy.py).

---

[상위 장](../05-fvp-qbox-comparison.md) · [전체 목차](../README.md) · [이전: 05 개요](../05-fvp-qbox-comparison.md) · [다음: Topology와 device mechanism](02-topology-device-mechanisms.md)
