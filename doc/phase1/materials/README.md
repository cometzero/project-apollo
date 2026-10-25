# Apollo Project Seminar

> **Hardware block → 실행 Domain → boot/runtime service → source와 build → QBox 연결** 순서로 Apollo를 설명하는 한국어 세미나 자료입니다. Arm Zena CSS / RD-Aspen reference의 구성 원리를 먼저 읽고, 현재 Apollo 구현에 대응시킵니다.

**구성: 7개 장 안내 + 32개 상세 기술 문서.** 각 장은 개요와 읽기 순서를 제공하며, 상세 문서는 목적·구성·동작 순서·interface·source·실패 진단을 연결합니다.

기준일: **2026-10-25** · Root source: `c3f91677a416b2c52bb41cffcc7623fcb4435e44`

## 1. 전체 자료와 발표 순서

| 자료 | Diagram으로 설명하는 구성 | 본문에서 따라가는 기술적 흐름 |
|---|---|---|
| [01. Project Overview](01-project-overview.md) | Compute Complex, SMB, baremetal/Xen stack, address domain | AP·RSE·SI의 역할, ATU/shared memory, boot·service·fault lifecycle |
| [02. Project Source Architecture](02-project-source-architecture.md) | HW block과 source ownership, secure service, source provenance, HIPC | Framework/port 분리, Linux provider·config·DTB 선택, source→consumer 추적 |
| [03. Project Build Architecture](03-project-build-architecture.md) | Yocto layer, firmware/OS assembly, Flash layout, native provider | kas와 wrapper, toolchain/ABI, signing/FWU, verity→initramfs→UKI→WIC |
| [04. QBox 실행 구조와 Apollo Lua](04-qbox-runtime-and-lua.md) | Launcher, domain fabric, SoC/VP/Board, MMIO, time model | CCI 최종 binding, address translation 수치 예, DMI·IRQ, TCG/SystemC 시간과 reset |
| [05. FVP와 QBox 구성 비교](05-fvp-qbox-comparison.md) | Reference IP, SMB, GIC multiple views, power control, HIPC | CMN/NI/ATU/SMMU 대응, machine별 artifact, CPUFreq/Idle와 IPC 구현 범위 |
| [06. Component SW Architecture](06-component-software-architecture.md) | Multi-domain boot, AP/TF-M/SCP/Zephyr 내부 구조, secure service, FWU | EL/privilege, PSA IPC, module binding/event, init/thread, remoteproc attach |
| [07. System SW Core Architecture](07-system-software-core.md) | IRQ·MSI, mailbox, timer·WDT, power, PFDI, FMU/SSU, RAS, SBISTC/TFP, SMCF | Buffer ownership, deadline 계산, AP recovery, fault 수집·정책·report 경로 |

전체 **61종 diagram의 편집 원본과 77회 본문 사용 위치**는 [DIAGRAMS.md](DIAGRAMS.md)에 모았습니다. 각 그림 바로 아래의 **draw.io 편집 원본** 링크로 해당 `.drawio`를 열 수 있습니다.

장 안내와 핵심 사례는 **두 차례의 90분 세미나**로 나눌 수 있습니다. 32개 상세 문서 전체는 후속 주제별 세션과 source 읽기 자료입니다. 첫 회는 01→02→03→04로 구성과 구현 경로를 읽고, 둘째 회는 06→07→05로 Domain 내부 동작과 FVP 비교를 다룹니다. 장별 상세 표와 source 사례까지 설명하려면 별도의 토론 시간이 필요합니다.

45분 Overview에서는 01장의 hardware·software·address 그림, 03장의 assembly 그림, 04장의 domain fabric, 06장의 boot handoff, 07장의 mailbox·watchdog 예제를 선택합니다. 상세 문서의 수치 예제와 함수 추적은 주제별 세션에서 이어 다룹니다.

### 상세 문서 전체 목차

상위 장에서 개념을 잡은 뒤 아래 순서로 읽습니다. Core 기능만 살펴볼 때도 해당 문서의 Domain·주소 view·완료 조건을 먼저 확인합니다.

| 번호 | 상세 문서 |
|---|---|
| 01.1 | [Hardware 구성과 Domain ownership](01-overview/01-hardware-and-domains.md) |
| 01.2 | [Software stack과 실행 profile](01-overview/02-software-and-profiles.md) |
| 01.3 | [Address view와 System lifecycle](01-overview/03-address-and-lifecycle.md) |
| 02.1 | [Repository ownership과 domain dependency](02-source/01-ownership-and-dependencies.md) |
| 02.2 | [Source 선택·configuration·artifact contract](02-source/02-build-source-contracts.md) |
| 02.3 | [Change trace·HIPC 사례·실패 진단](02-source/03-change-tracing-and-diagnosis.md) |
| 03.1 | [Build entrypoint와 configuration 선택](03-build/01-configuration-and-entrypoints.md) |
| 03.2 | [Toolchain·task DAG·native provider](03-build/02-task-graph-and-native-provider.md) |
| 03.3 | [Firmware signing·FWU metadata·Flash assembly](03-build/03-firmware-signing-and-flash.md) |
| 03.4 | [Rootfs·dm-verity·initramfs·UKI·WIC](03-build/04-os-image-and-storage.md) |
| 03.5 | [Runtime artifact handoff와 실패 진단](03-build/05-runtime-artifacts-and-diagnosis.md) |
| 04.1 | [Launcher, artifact 선택과 runtime process](04-qbox/01-launcher-runtime.md) |
| 04.2 | [QemuInstance와 SystemC/QOM object 생성](04-qbox/02-qemu-instance-construction.md) |
| 04.3 | [SoC·VP·Board Lua composition과 boot/reset](04-qbox/03-lua-composition.md) |
| 04.4 | [Address view, MMIO·DMA·IRQ·DMI와 시간](04-qbox/04-address-time-transport.md) |
| 05.1 | [FVP/QBox 비교 baseline과 artifact 계약](05-comparison/01-comparison-baseline.md) |
| 05.2 | [Domain topology와 device mechanism 비교](05-comparison/02-topology-device-mechanisms.md) |
| 05.3 | [Evidence, FVP reference gate와 실패 진단](05-comparison/03-evidence-and-diagnosis.md) |
| 06.1 | [Boot와 firmware lifecycle](06-software/01-boot-and-lifecycle.md) |
| 06.2 | [AP boot·Linux·Secure Services](06-software/02-ap-and-secure-services.md) |
| 06.3 | [RSE TF-M과 PSA runtime](06-software/03-rse-and-psa-runtime.md) |
| 06.4 | [Secure FWU와 image encryption](06-software/04-secure-firmware-update.md) |
| 06.5 | [SI CL0 SCP system management](06-software/05-scp-system-management.md) |
| 06.6 | [SI CL1 Zephyr와 HIPC](06-software/06-zephyr-and-hipc.md) |
| 07.1 | [Interrupt와 GIC — source에서 ISR까지](07-system/01-interrupt-and-gic.md) |
| 07.2 | [Mailbox와 IPC — notification, payload, completion](07-system/02-mailbox-and-ipc.md) |
| 07.3 | [Timer와 deadline — count에서 callback까지](07-system/03-timer-and-deadlines.md) |
| 07.4 | [Watchdog과 AP recovery — WS1에서 service 복귀까지](07-system/04-watchdog-and-recovery.md) |
| 07.5 | [Power와 performance — PSCI, SCMI, PPU, DVFS](07-system/05-power-and-performance.md) |
| 07.6 | [PFDI와 core별 monitoring](07-system/06-pfdi-and-monitoring.md) |
| 07.7 | [FMU·SSU·RAS — fault identity에서 OS 기록까지](07-system/07-fmu-ssu-and-ras.md) |
| 07.8 | [SMCF — sampling control과 data delivery](07-system/08-smcf-sampling.md) |

**문서 간 연결 사례:** [Boot dependency](06-software/01-boot-and-lifecycle.md) → [Watchdog recovery](07-system/04-watchdog-and-recovery.md) → [PFDI generation](07-system/06-pfdi-and-monitoring.md), 또는 [Address alias](01-overview/03-address-and-lifecycle.md) → [Mailbox ownership](07-system/02-mailbox-and-ipc.md) → [Zephyr HIPC](06-software/06-zephyr-and-hipc.md).

## 2. 그림을 읽는 방법

**Reference 그림은 hardware/software 설계 원리**, **Apollo 도식은 현재 source의 연결**, **표는 두 구성의 대응과 차이**를 설명합니다. 그림마다 주변 본문에서 주요 block, request/data 경로, owner를 해설합니다.

| 그림 종류 | 표시와 원본 | 읽을 때 확인할 것 |
|---|---|---|
| Arm reference architecture — 24종 | `figures/reference/*.drawio`와 `.drawio.svg`, 최초 SVG/PNG·RST 출처 유지 | 22개 native graph 복원과 PNG 기반 재작성 2개의 구분, reference/Apollo 차이 |
| Apollo seminar diagram — 14종 | `diagrams/*.drawio`와 `.drawio.svg` | 그림 아래 설명과 본문의 실제 source link |
| 기존 Phase 1 상세 diagram — 23종 | `diagrams/phase1/*.drawio`와 `.drawio.svg`, 기존 source page 재사용 | 작성 시점 차이는 각 caption의 보정 설명 |

본문의 모든 표시 그림은 `.drawio.svg`이며 편집 원본은 `.drawio`입니다. Arm reference 중 **Compute Complex와 System Management Block은 PNG의 block·label·관계를 바탕으로 native object로 재작성**했습니다. 나머지 22개는 원본에 내장된 mxGraph를 복원했습니다. [Reference figure index와 출처](figures/reference/README.md)에서 편집 원본, 표시 SVG, 최초 Arm SVG/PNG와 license를 함께 확인할 수 있습니다.

Apollo seminar 14개는 기존 Diagram Design의 **밝은 배경·짙은 글자·주황 강조**, 1280×720 구성을 native draw.io로 옮겼습니다. 초기 HTML과 이전 SVG/PNG도 보존했으며 [전체 Diagram index](DIAGRAMS.md)에서 비교용 HTML을 열 수 있습니다. Font가 없는 환경에서는 fallback이 적용되므로 viewer별 글자 폭에는 차이가 있을 수 있습니다.

## 3. 네 가지 사례를 끝까지 연결하기

| 세미나 사례 | Source / build에서 볼 것 | Runtime에서 설명할 것 | 관련 장 |
|---|---|---|---|
| Linux CPUFreq request | SCMI driver, SCP performance module, 각 image recipe | Request buffer → MHU → IRQ → SCP event → clock/DVFS response | 02, 03, 05, 07 |
| SI CL1 boot와 통신 | Zephyr board/module, signed SI image, RSE/SCP firmware | RSE load → CL0 power/release → Zephyr init → remoteproc attach → RPMsg | 03, 06, 07 |
| AP secure service | TF-A, OP-TEE SPMC, SE-Proxy/SMM Gateway, TF-M partition | FF-A → AP Secure Partition → MHU/PSA → RSE service → reply | 01, 02, 06 |
| AP Watchdog recovery | WDT model/driver, SCP `si0_platform`, RSE reload path | WS0/WS1 → AP OFF → RSE authenticated reload → CPU0 ON | 04, 06, 07 |

각 사례에서 **어느 CPU가 실행하는가, 어느 address view인가, 누가 resource를 소유하는가, 어떤 artifact에 포함되는가**를 함께 확인합니다.

## 4. 현재 workspace의 기준 설정

| 항목 | Source/config에서 확인한 값 |
|---|---|
| Machine / variant | `MACHINE ??= "apollo-qvp"`, `RD_ASPEN_VARIANT="cfg2"` |
| AP population | `PC_CPUS_COUNT_DEFAULT ??= "4"`; 일반 Yocto/runner AP4, 별도 AP16 DTB 제공 |
| Distro / build output | `auto-ad-nexios`, `${TOPDIR}/tmp_baremetal` |
| Product / BSP target | `nexios-image` / `nexios-bsp-initramfs` |
| Full-system Lua | `apollo-qvp-saturn-v.lua` → `vp/profiles/full-system.lua` |
| Firmware domains | AP, RSE, SI CL0, SI CL1; QemuInstance는 RSE helper를 포함해 5개 |

근거: [local.conf](../../../build/conf/local.conf), [machine metadata](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf), [build wrapper](../../../yocto_build.sh), [SoC composition](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/apollo.lua).

이 값은 local file과 source를 읽은 결과이며 `bitbake -e`로 최종 datastore를 평가한 결과는 아닙니다. 명령행/환경 override와 `soc/config.lua` 단독 기본 AP16을 구분합니다. Source revision과 문서 검사는 [SOURCES.md](SOURCES.md)에 기록했습니다.

## 5. Reference와 상세 자료

| 읽을 목적 | 자료 |
|---|---|
| Diagram 편집·확대·사용 위치 | [전체 61종 Diagram index](DIAGRAMS.md), [Arm reference와 license](figures/reference/README.md) |
| Arm 원본 전체 구조 | [overview.rst](../../../arm-zena-css/documentation/overview.rst), [components.rst](../../../arm-zena-css/documentation/design/components.rst) |
| Boot와 trust boundary | [boot_process.rst](../../../arm-zena-css/documentation/design/boot_process.rst), [secure_services.rst](../../../arm-zena-css/documentation/design/secure_services.rst) |
| Runtime control과 IPC | [power_and_performance_control.rst](../../../arm-zena-css/documentation/design/power_and_performance_control.rst), [hipc.rst](../../../arm-zena-css/documentation/design/hipc.rst) |
| Reference build와 integration | [integration.rst](../../../arm-zena-css/documentation/design/integration.rst), [reproduce.rst](../../../arm-zena-css/documentation/user_guide/reproduce.rst) |
| Apollo 상세 설계 | [Build](../build/README.md), [QBox](../qbox/README.md), [Linux](../linux/README.md), [TF-M](../tfm/README.md), [SCP](../scp/README.md), [Zephyr](../zephyr/README.md) |
| System core 상세 | [Interrupt](../interrupt/README.md), [Mailbox](../mailbox/README.md), [Timer](../timer/README.md), [Watchdog](../watchdog/README.md) |
| Hardware와 구현 상태 | [Zena CSS guide](../../arm_zena_css_dev_guide/index.md), [QBox emulation project](../../qbox-fvp-emulation-project.md) |

원본 directory의 실제 이름은 `arm-zena-css/documentation/`입니다. Arm 문서의 EWAOL image, reference layer 이름, Flash/WIC layout, SSU 상태 전이는 현재 Apollo와 차이가 있어 해당 장에 구분해서 적었습니다.

## 6. 세미나 후 설명할 수 있어야 할 것

- AP·RSE·CL0·CL1의 실행 privilege, boot owner와 runtime service owner.
- CPU local address, system-global address, shared-memory backing의 관계.
- QEMU/libqemu, QBox, Apollo Lua/모델, Yocto native provider의 책임.
- Firmware signing과 Flash 조립, rootfs integrity와 UKI/WIC 조립의 차이.
- IRQ acknowledge와 device clear, MHU notification과 protocol completion의 차이.
- Timer deadline과 Watchdog recovery, PFDI test와 FMU/SSU fault policy의 연결.

문서 내 `source 확인`, `reference`, `UNVERIFIED`, `미구성` 표기는 구현·설계·검증 상태를 구분합니다. 과거 PASS는 그때의 profile과 artifact 범위로 읽습니다. 문서 검증의 이전 결과와 native draw.io 전환 검증 상태는 [SOURCES.md](SOURCES.md#deep-dive-validation)에 구분해서 기록합니다. Build, QBox/FVP boot, fault injection은 실행하지 않았습니다.
