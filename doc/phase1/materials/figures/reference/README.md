# Arm reference draw.io index

[세미나 목차](../../README.md) · [전체 Diagram index](../../DIAGRAMS.md) · [Source와 검증 기록](../../SOURCES.md)

이 directory의 편집 원본은 24개 `.drawio`이며, 본문은 같은 이름의 `.drawio.svg`를 표시한다. **22개는 Arm 원본에 내장된 mxGraph를 복원했고, Compute Complex와 System Management Block 두 개는 PNG의 block·label·관계를 기준으로 native draw.io object로 재작성했다.** 두 재작성 그림은 원본 PNG의 pixel 복사본이 아니며 caption에도 재작성 사실을 표시한다.

Arm 원본은 `arm-zena-css/documentation/images/`에 보존했다. 아래 표의 Arm 원본 링크는 최초 SVG/PNG로, 편집 원본 링크는 이 자료에 포함한 native graph로 연결된다. 이전 단계의 white-background PNG도 같은 directory에 보존했으며, 현재 본문 표시 파일은 `.drawio.svg`다.

SSU는 최초 표시 PNG와 같은 이름의 [원본 SVG](../../../../../arm-zena-css/documentation/images/ssu_fsm_state.svg)에 포함된 mxGraph를 복원했다.

각 caption의 RST 출처와 Apollo delta를 함께 읽는다. Reference의 physical block이나 기능 설명을 QVP 전체 구현·검증 완료로 해석하지 않는다.

Repository의 [documentation/REUSE.toml](../../../../../arm-zena-css/documentation/REUSE.toml)과 각 SVG의 SPDX header를 기준으로 출처·license를 유지한다.

**Copyright 2025–2026 Arm Limited and/or its affiliates &lt;open-source-office@arm.com&gt;.**
**SPDX-License-Identifier: MIT.** [MIT license 전문](LICENSE-MIT.txt). 원본 각 파일의 저작권·license 고지를 따른다. 복원·재작성 결과도 Arm reference에 기반한 자료임을 표시한다.

| 그림 | 편집 원본 | 표시 SVG | Arm 원본 | 확보 방식 | 사용 문서 |
|---|---|---|---|---|---|
| Arm reference Xen virtualization architecture | [draw.io](aspen-virtualization-arch.drawio) | [SVG](aspen-virtualization-arch.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/aspen-virtualization-arch.svg) | embedded mxGraph 복원 | [01.2](../../01-overview/02-software-and-profiles.md) |
| Arm Zena CSS System Block Diagram | [draw.io](aspen_compute_complex.drawio) | [SVG](aspen_compute_complex.drawio.svg) | [PNG](../../../../../arm-zena-css/documentation/images/aspen_compute_complex.png) | PNG 기준 native 재작성 | [01.1](../../01-overview/01-hardware-and-domains.md) · [02.1](../../02-source/01-ownership-and-dependencies.md) · [05.1](../../05-comparison/01-comparison-baseline.md) |
| Arm reference baremetal software architecture | [draw.io](aspen_high_level_arch.drawio) | [SVG](aspen_high_level_arch.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/aspen_high_level_arch.svg) | embedded mxGraph 복원 | [01.2](../../01-overview/02-software-and-profiles.md) |
| Arm System Management Block | [draw.io](aspen_system_management_block.drawio) | [SVG](aspen_system_management_block.drawio.svg) | [PNG](../../../../../arm-zena-css/documentation/images/aspen_system_management_block.png) | PNG 기준 native 재작성 | [01.1](../../01-overview/01-hardware-and-domains.md) · [02.1](../../02-source/01-ownership-and-dependencies.md) · [05.2](../../05-comparison/02-topology-device-mechanisms.md) · [06.1](../../06-software/01-boot-and-lifecycle.md) |
| Arm FMU and SSU integration | [draw.io](fmu_ssu_integration.drawio) | [SVG](fmu_ssu_integration.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/fmu_ssu_integration.svg) | embedded mxGraph 복원 | [07.7](../../07-system/07-fmu-ssu-and-ras.md) |
| Arm RD-Aspen FMU tree | [draw.io](fmu_tree.drawio) | [SVG](fmu_tree.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/fmu_tree.svg) | embedded mxGraph 복원 | [07.7](../../07-system/07-fmu-ssu-and-ras.md) |
| Arm HIPC Baremetal Architecture | [draw.io](hipc_baremetal_design.drawio) | [SVG](hipc_baremetal_design.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/hipc_baremetal_design.svg) | embedded mxGraph 복원 | [02.3](../../02-source/03-change-tracing-and-diagnosis.md) · [05.2](../../05-comparison/02-topology-device-mechanisms.md) · [06.6](../../06-software/06-zephyr-and-hipc.md) |
| Arm reference의 ROM·Flash·WIC image layout | [draw.io](image-layouts.drawio) | [SVG](image-layouts.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/image-layouts.svg) | embedded mxGraph 복원 | [03.3](../../03-build/03-firmware-signing-and-flash.md) · [06.1](../../06-software/01-boot-and-lifecycle.md) |
| Arm Primary Compute domain reset | [draw.io](pc_domain_reset.drawio) | [SVG](pc_domain_reset.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/pc_domain_reset.svg) | embedded mxGraph 복원 | [07.4](../../07-system/04-watchdog-and-recovery.md) |
| Arm AP PFDI architecture | [draw.io](platform_fault_detection_interface.drawio) | [SVG](platform_fault_detection_interface.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/platform_fault_detection_interface.svg) | embedded mxGraph 복원 | [07.6](../../07-system/06-pfdi-and-monitoring.md) |
| Arm PFDI monitoring architecture | [draw.io](platform_fault_detection_interface_monitoring.drawio) | [SVG](platform_fault_detection_interface_monitoring.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/platform_fault_detection_interface_monitoring.svg) | embedded mxGraph 복원 | [07.6](../../07-system/06-pfdi-and-monitoring.md) |
| Arm Power and performance control | [draw.io](power_and_performance_control.drawio) | [SVG](power_and_performance_control.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/power_and_performance_control.svg) | embedded mxGraph 복원 | [05.2](../../05-comparison/02-topology-device-mechanisms.md) · [07.5](../../07-system/05-power-and-performance.md) |
| Arm reference의 Primary Compute Secure Services | [draw.io](primary_compute_secure_services.drawio) | [SVG](primary_compute_secure_services.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/primary_compute_secure_services.svg) | embedded mxGraph 복원 | [02.2](../../02-source/02-build-source-contracts.md) · [06.2](../../06-software/02-ap-and-secure-services.md) |
| Arm RAS error processing | [draw.io](ras_error_processing.drawio) | [SVG](ras_error_processing.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/ras_error_processing.svg) | embedded mxGraph 복원 | [07.7](../../07-system/07-fmu-ssu-and-ras.md) |
| Arm RSE-oriented boot flow | [draw.io](rse_oriented_boot_flow.drawio) | [SVG](rse_oriented_boot_flow.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/rse_oriented_boot_flow.svg) | embedded mxGraph 복원 | [04.3](../../04-qbox/03-lua-composition.md) · [06.1](../../06-software/01-boot-and-lifecycle.md) |
| Arm SBISTC to FMU information flow | [draw.io](sbistc_info_flow.drawio) | [SVG](sbistc_info_flow.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/sbistc_info_flow.svg) | embedded mxGraph 복원 | [07.7](../../07-system/07-fmu-ssu-and-ras.md) |
| RSE, TF-A, SCP의 SCMI communication 관계 | [draw.io](scmi_comm_rse_tfa_scp.drawio) | [SVG](scmi_comm_rse_tfa_scp.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/scmi_comm_rse_tfa_scp.svg) | embedded mxGraph 복원 | [07.2](../../07-system/02-mailbox-and-ipc.md) |
| Arm Secure Firmware Update architecture | [draw.io](secure_firmware_update.drawio) | [SVG](secure_firmware_update.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/secure_firmware_update.svg) | embedded mxGraph 복원 | [06.4](../../06-software/04-secure-firmware-update.md) |
| Arm Safety Island GIC Multiple Views | [draw.io](si_gic_multiple_view.drawio) | [SVG](si_gic_multiple_view.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/si_gic_multiple_view.svg) | embedded mxGraph 복원 | [05.2](../../05-comparison/02-topology-device-mechanisms.md) · [07.1](../../07-system/01-interrupt-and-gic.md) |
| Arm SI CL1 PFDI architecture | [draw.io](si_platform_fault_detection_interface.drawio) | [SVG](si_platform_fault_detection_interface.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/si_platform_fault_detection_interface.svg) | embedded mxGraph 복원 | [07.6](../../07-system/06-pfdi-and-monitoring.md) |
| Arm SSU reference state machine | [draw.io](ssu_fsm_state.drawio) | [SVG](ssu_fsm_state.drawio.svg) | [PNG](../../../../../arm-zena-css/documentation/images/ssu_fsm_state.png) | embedded mxGraph 복원 | [07.7](../../07-system/07-fmu-ssu-and-ras.md) |
| Arm Transient Fault Protection mechanism | [draw.io](tfp_mechanism.drawio) | [SVG](tfp_mechanism.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/tfp_mechanism.svg) | embedded mxGraph 복원 | [07.7](../../07-system/07-fmu-ssu-and-ras.md) |
| Arm reference의 Yocto layer dependency | [draw.io](yocto_layers_dependency_diagram.drawio) | [SVG](yocto_layers_dependency_diagram.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/yocto_layers_dependency_diagram.svg) | embedded mxGraph 복원 | [03.1](../../03-build/01-configuration-and-entrypoints.md) |
| Arm reference RSE image encryption procedure | [draw.io](image-encryption-procedure.drawio) | [SVG](image-encryption-procedure.drawio.svg) | [SVG](../../../../../arm-zena-css/documentation/images/image-encryption-procedure.svg) | embedded mxGraph 복원 | [06.4](../../06-software/04-secure-firmware-update.md) |

전체 graph 구조와 export 검증 상태는 [SOURCES.md의 draw.io 전환 검증](../../SOURCES.md#drawio-validation)에 기록한다.
