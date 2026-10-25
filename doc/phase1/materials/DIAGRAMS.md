# Diagram 편집 원본과 본문 사용 목록

[세미나 목차](README.md) · [Arm reference index](figures/reference/README.md) · [Source와 검증 기록](SOURCES.md)

7개 장 안내와 32개 상세 문서의 그림은 `.drawio.svg`로 표시하고 바로 아래에 `.drawio` 편집 원본을 연결한다. **고유 diagram은 61종이고 본문 삽입은 77회**다. 같은 reference 그림을 여러 장에 사용한 경우 아래 목록에서는 한 행으로 묶고 사용하는 상세 문서까지 연결했다.

| 분류 | 고유 diagram | 확보 방식 | 위치 |
|---|---:|---|---|
| Apollo seminar | 14 | 기존 HTML/SVG 도식을 native object·connector로 변환 | `diagrams/` |
| Arm reference | 24 | embedded mxGraph 복원 22개, PNG 기준 native 재작성 2개 | `figures/reference/` |
| 기존 Phase 1 상세 자료 | 23 | 기존 multi-page draw.io의 해당 page를 보존하여 single-page로 재사용 | `diagrams/phase1/` |
| 합계 | 61 | `.drawio` 편집 원본과 `.drawio.svg` 표시본 | 본문 77회 삽입 |

편집할 때는 `.drawio`를 draw.io에서 연다. `.drawio.svg`는 Markdown 표시용이며 동일한 native graph가 내장되어 있어 draw.io에서 다시 열 수도 있다. 기존 14개 HTML과 이전 SVG/PNG는 비교용으로 보존했으며, 아래 HTML 링크는 초기 HTML 도식을 가리킨다. 원본을 변경한 뒤에는 SVG를 **Include a copy of my diagram** 옵션과 함께 다시 export하여 본문 표시와 편집 source를 맞춘다.

## 1. 문서별 삽입 명세

| 문서 | 삽입 횟수 |
|---|---:|
| [01.1 Hardware 구성과 Domain ownership](01-overview/01-hardware-and-domains.md) | 2 |
| [01.2 Software stack과 실행 profile](01-overview/02-software-and-profiles.md) | 2 |
| [01.3 Address view와 System lifecycle](01-overview/03-address-and-lifecycle.md) | 2 |
| [02. Project Source Architecture](02-project-source-architecture.md) | 1 |
| [02.1. Repository ownership과 domain dependency](02-source/01-ownership-and-dependencies.md) | 2 |
| [02.2. Source 선택·configuration·artifact contract](02-source/02-build-source-contracts.md) | 2 |
| [02.3. Change trace·HIPC 사례·실패 진단](02-source/03-change-tracing-and-diagnosis.md) | 1 |
| [03.1. Build entrypoint와 configuration 선택](03-build/01-configuration-and-entrypoints.md) | 2 |
| [03.2. Toolchain·task DAG·native provider](03-build/02-task-graph-and-native-provider.md) | 1 |
| [03.3. Firmware signing·FWU metadata·Flash assembly](03-build/03-firmware-signing-and-flash.md) | 2 |
| [03.4. Rootfs·dm-verity·initramfs·UKI·WIC](03-build/04-os-image-and-storage.md) | 1 |
| [03. Project Build Architecture](03-project-build-architecture.md) | 1 |
| [04.1 Launcher, artifact 선택과 runtime process](04-qbox/01-launcher-runtime.md) | 1 |
| [04.2 QemuInstance와 SystemC/QOM object 생성](04-qbox/02-qemu-instance-construction.md) | 1 |
| [04.3 SoC·VP·Board Lua composition과 boot/reset](04-qbox/03-lua-composition.md) | 2 |
| [04.4 Address view, MMIO·DMA·IRQ·DMI와 시간](04-qbox/04-address-time-transport.md) | 3 |
| [04. QBox 실행 구조와 Apollo QVP Lua](04-qbox-runtime-and-lua.md) | 1 |
| [05.1 FVP/QBox 비교 baseline과 artifact 계약](05-comparison/01-comparison-baseline.md) | 2 |
| [05.2 Domain topology와 device mechanism 비교](05-comparison/02-topology-device-mechanisms.md) | 4 |
| [05.3 Evidence, FVP reference gate와 실패 진단](05-comparison/03-evidence-and-diagnosis.md) | 1 |
| [05. FVP 대비 QBox 구성 비교](05-fvp-qbox-comparison.md) | 1 |
| [06. Project Component SW Architecture](06-component-software-architecture.md) | 1 |
| [06.1. Boot와 firmware lifecycle](06-software/01-boot-and-lifecycle.md) | 4 |
| [06.2. AP boot·Linux·Secure Services](06-software/02-ap-and-secure-services.md) | 3 |
| [06.3. RSE TF-M과 PSA runtime](06-software/03-rse-and-psa-runtime.md) | 3 |
| [06.4. Secure FWU와 image encryption](06-software/04-secure-firmware-update.md) | 2 |
| [06.5. SI CL0 SCP system management](06-software/05-scp-system-management.md) | 3 |
| [06.6. SI CL1 Zephyr와 HIPC](06-software/06-zephyr-and-hipc.md) | 4 |
| [07.1 Interrupt와 GIC — source에서 ISR까지](07-system/01-interrupt-and-gic.md) | 3 |
| [07.2 Mailbox와 IPC — notification, payload, completion](07-system/02-mailbox-and-ipc.md) | 3 |
| [07.3 Timer와 deadline — count에서 callback까지](07-system/03-timer-and-deadlines.md) | 3 |
| [07.4 Watchdog과 AP recovery — WS1에서 service 복귀까지](07-system/04-watchdog-and-recovery.md) | 2 |
| [07.5 Power와 performance — PSCI, SCMI, PPU, DVFS](07-system/05-power-and-performance.md) | 1 |
| [07.6 PFDI와 core별 monitoring](07-system/06-pfdi-and-monitoring.md) | 3 |
| [07.7 FMU·SSU·RAS — fault identity에서 OS 기록까지](07-system/07-fmu-ssu-and-ras.md) | 6 |
| [07.8 SMCF — sampling control과 data delivery](07-system/08-smcf-sampling.md) | 1 |
| 합계 | 77 |

표 중심 문서는 위 삽입 명세에서 제외한다. 전체 읽기 순서는 [README](README.md)의 상세 목차를 따른다.

## 2. Apollo seminar diagram — 14종

각 도식의 기술적 범위와 생략한 상세는 [SOURCES.md](SOURCES.md#5-diagram과-reference-figure의-표현-범위) 및 그림 옆 본문에서 설명한다.

| Diagram | 편집 원본 | 표시 SVG | 기존 HTML | 사용 문서 |
|---|---|---|---|---|
| `01-address-domains` | [draw.io](diagrams/01-address-domains.drawio) | [SVG](diagrams/01-address-domains.drawio.svg) | [HTML](diagrams/01-address-domains.html) | [01.3](01-overview/03-address-and-lifecycle.md) |
| `01-project-overview` | [draw.io](diagrams/01-project-overview.drawio) | [SVG](diagrams/01-project-overview.drawio.svg) | [HTML](diagrams/01-project-overview.html) | [01.3](01-overview/03-address-and-lifecycle.md) |
| `02-source-map` | [draw.io](diagrams/02-source-map.drawio) | [SVG](diagrams/02-source-map.drawio.svg) | [HTML](diagrams/02-source-map.html) | [02](02-project-source-architecture.md) |
| `03-build-pipeline` | [draw.io](diagrams/03-build-pipeline.drawio) | [SVG](diagrams/03-build-pipeline.drawio.svg) | [HTML](diagrams/03-build-pipeline.html) | [03](03-project-build-architecture.md) |
| `04-domain-fabric` | [draw.io](diagrams/04-domain-fabric.drawio) | [SVG](diagrams/04-domain-fabric.drawio.svg) | [HTML](diagrams/04-domain-fabric.html) | [04.4](04-qbox/04-address-time-transport.md) |
| `04-lua-composition` | [draw.io](diagrams/04-lua-composition.drawio) | [SVG](diagrams/04-lua-composition.drawio.svg) | [HTML](diagrams/04-lua-composition.html) | [04.3](04-qbox/03-lua-composition.md) |
| `04-qbox-runtime` | [draw.io](diagrams/04-qbox-runtime.drawio) | [SVG](diagrams/04-qbox-runtime.drawio.svg) | [HTML](diagrams/04-qbox-runtime.html) | [04.1](04-qbox/01-launcher-runtime.md) · [04.2](04-qbox/02-qemu-instance-construction.md) · [04](04-qbox-runtime-and-lua.md) |
| `05-fvp-qbox` | [draw.io](diagrams/05-fvp-qbox.drawio) | [SVG](diagrams/05-fvp-qbox.drawio.svg) | [HTML](diagrams/05-fvp-qbox.html) | [05.1](05-comparison/01-comparison-baseline.md) · [05.3](05-comparison/03-evidence-and-diagnosis.md) · [05](05-fvp-qbox-comparison.md) |
| `06-boot-handoff` | [draw.io](diagrams/06-boot-handoff.drawio) | [SVG](diagrams/06-boot-handoff.drawio.svg) | [HTML](diagrams/06-boot-handoff.html) | [06.1](06-software/01-boot-and-lifecycle.md) |
| `06-domain-software` | [draw.io](diagrams/06-domain-software.drawio) | [SVG](diagrams/06-domain-software.drawio.svg) | [HTML](diagrams/06-domain-software.html) | [06](06-component-software-architecture.md) |
| `07-interrupt-route` | [draw.io](diagrams/07-interrupt-route.drawio) | [SVG](diagrams/07-interrupt-route.drawio.svg) | [HTML](diagrams/07-interrupt-route.html) | [07.1](07-system/01-interrupt-and-gic.md) |
| `07-mailbox-flow` | [draw.io](diagrams/07-mailbox-flow.drawio) | [SVG](diagrams/07-mailbox-flow.drawio.svg) | [HTML](diagrams/07-mailbox-flow.html) | [07.2](07-system/02-mailbox-and-ipc.md) |
| `07-smcf-monitor` | [draw.io](diagrams/07-smcf-monitor.drawio) | [SVG](diagrams/07-smcf-monitor.drawio.svg) | [HTML](diagrams/07-smcf-monitor.html) | [07.8](07-system/08-smcf-sampling.md) |
| `07-timer-watchdog` | [draw.io](diagrams/07-timer-watchdog.drawio) | [SVG](diagrams/07-timer-watchdog.drawio.svg) | [HTML](diagrams/07-timer-watchdog.html) | [07.3](07-system/03-timer-and-deadlines.md) |

## 3. Arm reference — 24종

Compute Complex와 System Management Block은 PNG 기반 재작성이다. 나머지 22개는 원본에 내장된 native graph를 복원했다. [Reference index](figures/reference/README.md)에 최초 Arm SVG/PNG, RST 관련 caption과 MIT license 정보를 연결했다.

| Diagram | 편집 원본 | 표시 SVG | 방식 | 사용 문서 |
|---|---|---|---|---|
| Arm reference Xen virtualization architecture | [draw.io](figures/reference/aspen-virtualization-arch.drawio) | [SVG](figures/reference/aspen-virtualization-arch.drawio.svg) | embedded mxGraph 복원 | [01.2](01-overview/02-software-and-profiles.md) |
| Arm Zena CSS System Block Diagram | [draw.io](figures/reference/aspen_compute_complex.drawio) | [SVG](figures/reference/aspen_compute_complex.drawio.svg) | PNG 기준 native 재작성 | [01.1](01-overview/01-hardware-and-domains.md) · [02.1](02-source/01-ownership-and-dependencies.md) · [05.1](05-comparison/01-comparison-baseline.md) |
| Arm reference baremetal software architecture | [draw.io](figures/reference/aspen_high_level_arch.drawio) | [SVG](figures/reference/aspen_high_level_arch.drawio.svg) | embedded mxGraph 복원 | [01.2](01-overview/02-software-and-profiles.md) |
| Arm System Management Block | [draw.io](figures/reference/aspen_system_management_block.drawio) | [SVG](figures/reference/aspen_system_management_block.drawio.svg) | PNG 기준 native 재작성 | [01.1](01-overview/01-hardware-and-domains.md) · [02.1](02-source/01-ownership-and-dependencies.md) · [05.2](05-comparison/02-topology-device-mechanisms.md) · [06.1](06-software/01-boot-and-lifecycle.md) |
| Arm FMU and SSU integration | [draw.io](figures/reference/fmu_ssu_integration.drawio) | [SVG](figures/reference/fmu_ssu_integration.drawio.svg) | embedded mxGraph 복원 | [07.7](07-system/07-fmu-ssu-and-ras.md) |
| Arm RD-Aspen FMU tree | [draw.io](figures/reference/fmu_tree.drawio) | [SVG](figures/reference/fmu_tree.drawio.svg) | embedded mxGraph 복원 | [07.7](07-system/07-fmu-ssu-and-ras.md) |
| Arm HIPC Baremetal Architecture | [draw.io](figures/reference/hipc_baremetal_design.drawio) | [SVG](figures/reference/hipc_baremetal_design.drawio.svg) | embedded mxGraph 복원 | [02.3](02-source/03-change-tracing-and-diagnosis.md) · [05.2](05-comparison/02-topology-device-mechanisms.md) · [06.6](06-software/06-zephyr-and-hipc.md) |
| Arm reference RSE image encryption procedure | [draw.io](figures/reference/image-encryption-procedure.drawio) | [SVG](figures/reference/image-encryption-procedure.drawio.svg) | embedded mxGraph 복원 | [06.4](06-software/04-secure-firmware-update.md) |
| Arm reference의 ROM·Flash·WIC image layout | [draw.io](figures/reference/image-layouts.drawio) | [SVG](figures/reference/image-layouts.drawio.svg) | embedded mxGraph 복원 | [03.3](03-build/03-firmware-signing-and-flash.md) · [06.1](06-software/01-boot-and-lifecycle.md) |
| Arm Primary Compute domain reset | [draw.io](figures/reference/pc_domain_reset.drawio) | [SVG](figures/reference/pc_domain_reset.drawio.svg) | embedded mxGraph 복원 | [07.4](07-system/04-watchdog-and-recovery.md) |
| Arm AP PFDI architecture | [draw.io](figures/reference/platform_fault_detection_interface.drawio) | [SVG](figures/reference/platform_fault_detection_interface.drawio.svg) | embedded mxGraph 복원 | [07.6](07-system/06-pfdi-and-monitoring.md) |
| Arm PFDI monitoring architecture | [draw.io](figures/reference/platform_fault_detection_interface_monitoring.drawio) | [SVG](figures/reference/platform_fault_detection_interface_monitoring.drawio.svg) | embedded mxGraph 복원 | [07.6](07-system/06-pfdi-and-monitoring.md) |
| Arm Power and performance control | [draw.io](figures/reference/power_and_performance_control.drawio) | [SVG](figures/reference/power_and_performance_control.drawio.svg) | embedded mxGraph 복원 | [05.2](05-comparison/02-topology-device-mechanisms.md) · [07.5](07-system/05-power-and-performance.md) |
| Arm reference의 Primary Compute Secure Services | [draw.io](figures/reference/primary_compute_secure_services.drawio) | [SVG](figures/reference/primary_compute_secure_services.drawio.svg) | embedded mxGraph 복원 | [02.2](02-source/02-build-source-contracts.md) · [06.2](06-software/02-ap-and-secure-services.md) |
| Arm RAS error processing | [draw.io](figures/reference/ras_error_processing.drawio) | [SVG](figures/reference/ras_error_processing.drawio.svg) | embedded mxGraph 복원 | [07.7](07-system/07-fmu-ssu-and-ras.md) |
| Arm RSE-oriented boot flow | [draw.io](figures/reference/rse_oriented_boot_flow.drawio) | [SVG](figures/reference/rse_oriented_boot_flow.drawio.svg) | embedded mxGraph 복원 | [04.3](04-qbox/03-lua-composition.md) · [06.1](06-software/01-boot-and-lifecycle.md) |
| Arm SBISTC to FMU information flow | [draw.io](figures/reference/sbistc_info_flow.drawio) | [SVG](figures/reference/sbistc_info_flow.drawio.svg) | embedded mxGraph 복원 | [07.7](07-system/07-fmu-ssu-and-ras.md) |
| RSE, TF-A, SCP의 SCMI communication 관계 | [draw.io](figures/reference/scmi_comm_rse_tfa_scp.drawio) | [SVG](figures/reference/scmi_comm_rse_tfa_scp.drawio.svg) | embedded mxGraph 복원 | [07.2](07-system/02-mailbox-and-ipc.md) |
| Arm Secure Firmware Update architecture | [draw.io](figures/reference/secure_firmware_update.drawio) | [SVG](figures/reference/secure_firmware_update.drawio.svg) | embedded mxGraph 복원 | [06.4](06-software/04-secure-firmware-update.md) |
| Arm Safety Island GIC Multiple Views | [draw.io](figures/reference/si_gic_multiple_view.drawio) | [SVG](figures/reference/si_gic_multiple_view.drawio.svg) | embedded mxGraph 복원 | [05.2](05-comparison/02-topology-device-mechanisms.md) · [07.1](07-system/01-interrupt-and-gic.md) |
| Arm SI CL1 PFDI architecture | [draw.io](figures/reference/si_platform_fault_detection_interface.drawio) | [SVG](figures/reference/si_platform_fault_detection_interface.drawio.svg) | embedded mxGraph 복원 | [07.6](07-system/06-pfdi-and-monitoring.md) |
| Arm SSU reference state machine | [draw.io](figures/reference/ssu_fsm_state.drawio) | [SVG](figures/reference/ssu_fsm_state.drawio.svg) | embedded mxGraph 복원 | [07.7](07-system/07-fmu-ssu-and-ras.md) |
| Arm Transient Fault Protection mechanism | [draw.io](figures/reference/tfp_mechanism.drawio) | [SVG](figures/reference/tfp_mechanism.drawio.svg) | embedded mxGraph 복원 | [07.7](07-system/07-fmu-ssu-and-ras.md) |
| Arm reference의 Yocto layer dependency | [draw.io](figures/reference/yocto_layers_dependency_diagram.drawio) | [SVG](figures/reference/yocto_layers_dependency_diagram.drawio.svg) | embedded mxGraph 복원 | [03.1](03-build/01-configuration-and-entrypoints.md) |

## 4. 기존 Phase 1 상세 diagram — 23종

기존 8개 multi-page source에서 해당 page를 복사했다. Native cell·label·geometry·connector를 유지했고, 원래 source와 SVG는 변경하지 않았다. 원본 열의 page ID는 기존 multi-page 파일에서 같은 그림을 찾는 기준이다.

| Diagram | 편집 원본 | 표시 SVG | 기존 source / page ID | 사용 문서 |
|---|---|---|---|---|
| Yocto layer 관계 | [draw.io](diagrams/phase1/build-04-yocto-layers.drawio) | [SVG](diagrams/phase1/build-04-yocto-layers.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `04-yocto-layers` | [03.1](03-build/01-configuration-and-entrypoints.md) |
| Local source와 Yocto 통합 경계 | [draw.io](diagrams/phase1/build-05-source-provenance.drawio) | [SVG](diagrams/phase1/build-05-source-provenance.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `05-source-provenance` | [02.2](02-source/02-build-source-contracts.md) |
| Firmware 산출물 연결 | [draw.io](diagrams/phase1/build-07-firmware-assembly.drawio) | [SVG](diagrams/phase1/build-07-firmware-assembly.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `07-firmware-assembly` | [03.3](03-build/03-firmware-signing-and-flash.md) |
| Apollo rootfs·verity·initramfs·UKI·WIC 조립 | [draw.io](diagrams/phase1/build-08-os-assembly.drawio) | [SVG](diagrams/phase1/build-08-os-assembly.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `08-os-assembly` | [03.4](03-build/04-os-image-and-storage.md) |
| QBox native provider의 source·build·install 경로 | [draw.io](diagrams/phase1/build-09-native-provider.drawio) | [SVG](diagrams/phase1/build-09-native-provider.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `09-native-provider` | [03.2](03-build/02-task-graph-and-native-provider.md) |
| Linux driver와 domain 통신 구조 | [draw.io](diagrams/phase1/build-component-linux.drawio) | [SVG](diagrams/phase1/build-component-linux.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `component-linux` | [06.2](06-software/02-ap-and-secure-services.md) |
| SCP framework와 service module | [draw.io](diagrams/phase1/build-component-scp-firmware.drawio) | [SVG](diagrams/phase1/build-component-scp-firmware.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `component-scp-firmware` | [06.5](06-software/05-scp-system-management.md) |
| AP TF-A 내부 구조 | [draw.io](diagrams/phase1/build-component-tf-a.drawio) | [SVG](diagrams/phase1/build-component-tf-a.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `component-tf-a` | [06.2](06-software/02-ap-and-secure-services.md) |
| RSE TF-M component 구조 | [draw.io](diagrams/phase1/build-component-tf-m.drawio) | [SVG](diagrams/phase1/build-component-tf-m.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `component-tf-m` | [06.3](06-software/03-rse-and-psa-runtime.md) |
| CL1 Zephyr component 구조 | [draw.io](diagrams/phase1/build-component-zephyr.drawio) | [SVG](diagrams/phase1/build-component-zephyr.drawio.svg) | [source](../build/apollo-build-architecture.drawio) / `component-zephyr` | [06.6](06-software/06-zephyr-and-hipc.md) |
| Apollo PCIe MSI, ITS, LPI 경로 | [draw.io](diagrams/phase1/interrupt-12-its.drawio) | [SVG](diagrams/phase1/interrupt-12-its.drawio.svg) | [source](../interrupt/apollo-interrupt-architecture.drawio) / `12-its` | [07.1](07-system/01-interrupt-and-gic.md) |
| Hardware의 mailbox write와 QBox의 실제 객체 경로 | [draw.io](diagrams/phase1/qbox-04a-mmio-hardware-qbox.drawio) | [SVG](diagrams/phase1/qbox-04a-mmio-hardware-qbox.drawio.svg) | [source](../qbox/apollo-qvp-architecture.drawio) / `04a-mmio-hardware-qbox` | [04.4](04-qbox/04-address-time-transport.md) |
| Host wall time, QEMU virtual time, SystemC simulation time | [draw.io](diagrams/phase1/qbox-08-time-model.drawio) | [SVG](diagrams/phase1/qbox-08-time-model.drawio.svg) | [source](../qbox/apollo-qvp-architecture.drawio) / `08-time-model` | [04.4](04-qbox/04-address-time-transport.md) |
| SCP module API binding | [draw.io](diagrams/phase1/scp-08-binding.drawio) | [SVG](diagrams/phase1/scp-08-binding.drawio.svg) | [source](../scp/apollo-scp-architecture.drawio) / `08-binding` | [06.5](06-software/05-scp-system-management.md) |
| SCP SCMI service stack | [draw.io](diagrams/phase1/scp-15-scmi-stack.drawio) | [SVG](diagrams/phase1/scp-15-scmi-stack.drawio.svg) | [source](../scp/apollo-scp-architecture.drawio) / `15-scmi-stack` | [06.5](06-software/05-scp-system-management.md) |
| TF-M manifest와 partition 실행 구성 | [draw.io](diagrams/phase1/tfm-09-manifest.drawio) | [SVG](diagrams/phase1/tfm-09-manifest.drawio.svg) | [source](../tfm/apollo-tfm-architecture.drawio) / `09-manifest` | [06.3](06-software/03-rse-and-psa-runtime.md) |
| TF-M PSA IPC request 처리 | [draw.io](diagrams/phase1/tfm-10-ipc.drawio) | [SVG](diagrams/phase1/tfm-10-ipc.drawio.svg) | [source](../tfm/apollo-tfm-architecture.drawio) / `10-ipc` | [06.3](06-software/03-rse-and-psa-runtime.md) |
| Counter snapshot, QEMU timer와 SystemC timer의 시간 전달 | [draw.io](diagrams/phase1/timer-03a-counter-propagation.drawio) | [SVG](diagrams/phase1/timer-03a-counter-propagation.drawio.svg) | [source](../timer/apollo-timer-architecture.drawio) / `03a-counter-propagation` | [07.3](07-system/03-timer-and-deadlines.md) |
| SCP alarm queue와 하나의 MMIO comparator | [draw.io](diagrams/phase1/timer-08f-scp-software.drawio) | [SVG](diagrams/phase1/timer-08f-scp-software.drawio.svg) | [source](../timer/apollo-timer-architecture.drawio) / `08f-scp-software` | [07.3](07-system/03-timer-and-deadlines.md) |
| AP watchdog부터 SCP/RSE 협력 복구까지 | [draw.io](diagrams/phase1/watchdog-11-recovery-sequence.drawio) | [SVG](diagrams/phase1/watchdog-11-recovery-sequence.drawio.svg) | [source](../watchdog/apollo-watchdog-architecture.drawio) / `11-recovery-sequence` | [07.4](07-system/04-watchdog-and-recovery.md) |
| Zephyr init level과 driver/application 시작 | [draw.io](diagrams/phase1/zephyr-08-init-levels.drawio) | [SVG](diagrams/phase1/zephyr-08-init-levels.drawio.svg) | [source](../zephyr/apollo-zephyr-architecture.drawio) / `08-init-levels` | [06.6](06-software/06-zephyr-and-hipc.md) |
| Zephyr runtime thread 구성 | [draw.io](diagrams/phase1/zephyr-10-runtime-threads.drawio) | [SVG](diagrams/phase1/zephyr-10-runtime-threads.drawio.svg) | [source](../zephyr/apollo-zephyr-architecture.drawio) / `10-runtime-threads` | [06.6](06-software/06-zephyr-and-hipc.md) |
| CL1 HIPC attach와 resource negotiation | [draw.io](diagrams/phase1/zephyr-17-attach-sequence.drawio) | [SVG](diagrams/phase1/zephyr-17-attach-sequence.drawio.svg) | [source](../zephyr/apollo-zephyr-architecture.drawio) / `17-attach-sequence` | [07.2](07-system/02-mailbox-and-ipc.md) |

## 5. 검증 기록

기존 61개 native graph의 QA와 문서 분리 후 image 연결 검사는 [SOURCES.md](SOURCES.md#deep-dive-validation)에 기록한다. `.drawio` 존재 여부와 graph 구조 확인은 문서 편집성에 대한 검사이며 QBox/FVP runtime 검증을 뜻하지 않는다.
