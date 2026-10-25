# Source와 문서 검증 기록

[세미나 목차](README.md) · [전체 Diagram 편집 원본](DIAGRAMS.md)

## 1. 확인 범위

이 자료는 2026-10-25의 local checkout, `build/conf/`, 현재 launcher·recipe·Lua·firmware/driver source와 `arm-zena-css/documentation/`의 설계 문서를 읽어 작성했다. Arm reference는 hardware·protocol·boot 계약을 설명하는 기준이며, 현재 Apollo의 provider·image·model 선택은 owned source와 local configuration에서 확인했다. 기존 Phase 1 자료는 상세 구조를 설명하는 그림에 재사용하고 현재 source와의 차이는 그림 옆에 적었다.

Codebase index는 일부 project가 2026-09-30 snapshot이며 변경된 path의 coverage/freshness가 충분하지 않았다. 현재 `soc/`, `vp/`, `board/`와 build consumer는 직접 읽어서 확인했다. Index refresh, BitBake 실행, component source 변경, QBox/FVP boot는 수행하지 않았다.

## 2. 주요 source snapshot

Root `HEAD`: `c3f91677a416b2c52bb41cffcc7623fcb4435e44`, branch `feature/qbox-rebase`.
첫 작업 시작 시 root Git status는 clean이었다. 이 자료 작성 작업에서 수정한 범위는 `doc/phase1/materials/`이며, component repository와 build configuration은 수정하지 않았다. 작업 중 별도로 진행된 다른 경로의 변경은 이 검증의 변경 범위에 포함하지 않는다.

| Repository | 확인한 commit |
|---|---|
| QBox core | `5fc8c389f5f3d5a3c7bb92d60efa2ce826ec3d51` |
| QBox Apollo overlay | `795b92290f96f2096022288a3654d365aa1f4f83` |
| QEMU/libqemu | `f4abc1001d0d76322005ba5fcbff08e8592c25c9` |
| Linux | `3aaef1b1025505ba9dcd016bb4f35ccad6d662a4` |
| TF-A | `532c9e6dc679e18016cd4ec7620419692c663c26` |
| OP-TEE | `a2a275865d65c1dff6c5ffc87286fb6c71e3169c` |
| U-Boot | `3126346004207d7a14a1a7c561661f60a23c6d72` |
| TF-M | `94c5d43ae48c73faaa1da4f403da093f1d0dad6c` |
| SCP-firmware | `e6b1fbd91ea1ec86cc7d78c3bb7975ed58bfba94` |
| Zephyr kernel | `992228a26f3ff77d9bcf0c034601b2977bba8d3f` |
| Zephyr HSOC module | `c793fe7356e5d633e7a48cd2eb6b09ddb5c900e2` |
| meta-hsoc-bsp | `4ef8b0dd9f1d68a560e65ba61d32bc4bff34e797` |
| meta-hsoc-auto-solutions | `84f115c644b1421651e6b40b32736c8078ec800a` |
| Arm Zena CSS reference | `bf34d9e71f674e11beea3b8e84ea54486f555d2a` |
| Shared SW reference stack | `a42c7d9dee23dc929f1656d681845956dbc7d13b` |

전체 선택 revision과 config SHA-256은 local generated [source-snapshot.json](../../../build/qbox-apollo-qvp/seminar-materials-reference-enrichment-20261025/source-snapshot.json)에 기록했다. Root를 포함한 16개 repository HEAD와 3개 local build config hash가 바뀌지 않았음을 대조했다. 이 파일과 아래 QA report는 다른 clone에 없을 수 있다. 위 표와 각 장의 source 링크는 자료 자체에 남긴 기준이다.

## 3. 주제별 primary source

| 주제 | 확인한 entry / 핵심 symbol | 자료 |
|---|---|---|
| Project 역할 | [root README](../../../README.md), [emulation project](../../qbox-fvp-emulation-project.md) | [01](01-project-overview.md) |
| Git ownership | [.gitmodules](../../../.gitmodules), [AGENTS.md](../../../AGENTS.md), 각 nested repository `HEAD` | [02](02-project-source-architecture.md) |
| Source registry | [BSP layer.conf](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/layer.conf), `HSOC_APOLLO_*_SRC` | [02](02-project-source-architecture.md) |
| Build wrapper | [yocto_build.sh](../../../yocto_build.sh), `KEEP_CONF`, `BUILD_DIR`, `TEMPLATECONF` | [03](03-project-build-architecture.md) |
| Local config | [local.conf](../../../build/conf/local.conf), [bblayers.conf](../../../build/conf/bblayers.conf), [templateconf.cfg](../../../build/conf/templateconf.cfg) | [03](03-project-build-architecture.md) |
| Machine / DTB | [apollo-qvp.conf](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf), `PC_CPUS_COUNT`, `APOLLO_QVP_DTB` | [03](03-project-build-architecture.md) |
| Runtime contract | [qboxboot.bbclass](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/qboxboot.bbclass), `do_write_qboxboot_conf` | [03](03-project-build-architecture.md) |
| Native provider | [qbox-apollo-qvp-native.bb](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-apollo-qvp-native.bb), compile/check/install/sysroot | [03](03-project-build-architecture.md) |
| Launch / qualification | [Shell](../../../run_qbox_yocto.sh), [Python runner](../../../scripts/run/run_qbox_apollo_fvp_full.py), `--no-post-login-probe` | [04](04-qbox-runtime-and-lua.md) |
| Canonical Lua | [apollo-qvp-saturn-v.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua), `options.create`, full-system profile | [04](04-qbox-runtime-and-lua.md) |
| SoC / VP / Board | [SoC](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/apollo.lua), [composition](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/composition.lua), [board](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/saturn-v.lua) | [04](04-qbox-runtime-and-lua.md) |
| FVP topology / executable | [reference components](../../../arm-zena-css/documentation/design/components.rst), [cfg2 metadata](../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc) | [05](05-fvp-qbox-comparison.md) |
| RSE boot handoff | [boot_hal_bl2.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2/boot_hal_bl2.c), `boot_platform_pre_load_ap_bl2` | [06](06-component-software-architecture.md) |
| SCP service / recovery | [SI0 platform](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/si0_platform/src/mod_si0_platform.c) | [06](06-component-software-architecture.md), [07](07-system-software-core.md) |
| Zephyr board contract | [CL1 DTS](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1.dts), board defconfig | [06](06-component-software-architecture.md) |
| Interrupt / Timer / WDT binding | [soc/hw-block/](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/)의 domain별 `system.lua`, `cpu.lua`, mailbox와 reset modules | [07](07-system-software-core.md) |
| SCMI response condition | [SCP transport](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/transport/src/mod_transport.c), `IENABLED` | [07](07-system-software-core.md) |
| HIPC ownership | [arm_si_rproc](../../../sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src/arm_si_rproc.c), `RPROC_DETACHED`, attach/kick | [06](06-component-software-architecture.md), [07](07-system-software-core.md) |
| Firmware signing / flash assembly | [firmware-apollo-common.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/images/firmware-apollo-common.inc), [QVP firmware recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/images/firmware-apollo-qvp.bb), `do_sign_images`, `do_generate_rse_otp_image` | [03](03-project-build-architecture.md) |
| UKI / WIC / rootfs | [UKI class](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/auto-ad-nexios-uki-ab.bbclass), kernel·initramfs·cmdline·OS DTB 조립과 Secure Boot 선택 | [03](03-project-build-architecture.md) |
| RSE FWU / encryption | [Apollo TF-M configuration](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/config.cmake), [image key handle](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2/rse_bl2_rotkw.c), `NR_OF_FW_BANKS`, `MCUBOOT_ENC_IMAGES`, `get_enc_key_id_for_image()` | [06](06-component-software-architecture.md) |
| MMIO / thread / time | [QEMU initiator](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h), [CPU](../../../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h), [freerunning policy](../../../hsoc-stack/tools/qbox/systemc-components/common/include/qkmulti-freerunning.h), `do_regular_access()`, `sync_with_kernel()` | [04](04-qbox-runtime-and-lua.md) |
| SMMU / DMA / GIC view | [AP system objects](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua), [최종 binding](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua), `ap_smmu_lti00`, `ap_gic_multiview` | [04](04-qbox-runtime-and-lua.md), [05](05-fvp-qbox-comparison.md) |
| SMCF source와 model 경계 | [SCP configuration](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_smcf.c), [sampling client](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/smcf_client/src/mod_smcf_client.c), [QVP MGI](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_smcf_mgi/include/host_smcf_mgi.h) | [07](07-system-software-core.md) |

각 장에는 이 표보다 세부적인 model, driver, recipe 링크를 함께 적었다. 표의 source 존재 확인과 symbol 대조는 실행 성공의 증거가 아니다.

## 4. Arm reference RST coverage와 Apollo 적용 차이

아래 표는 이번 자료 작성·보강에서 읽고 설명에 사용한 절의 범위다. 원본 RST 전체와 모든 demo를 검증했다는 뜻은 아니다. 각 장에서 **reference architecture → 현재 source의 구현·선택 → 실행으로 확인할 항목** 순서로 연결했다.

### 4.1 System, source와 build

| 읽은 RST / 주요 절 | 자료에 반영한 기술 내용 | 현재 Apollo와 구분한 점 | 장 |
|---|---|---|---|
| [overview.rst](../../../arm-zena-css/documentation/overview.rst) — Software components, Platform IP, Architectures | AP/RSE/SI의 ISA·SW 배치, baremetal과 Xen Dom0/DomU의 구분 | 현재 local profile은 Nexios baremetal이며 Xen domain을 독립 firmware domain과 혼동하지 않음 | 01, 02, 05 |
| [components.rst](../../../arm-zena-css/documentation/design/components.rst) — System Management Block, GIC Multiple Views, MHUv3 Communication, Primary Compute, Address spaces | AP cluster, RSE/SI/SMD, ATU와 52-bit system region, TF-A/OP-TEE/U-Boot, GIC view | AP4 기본 population·AP4/AP16 DTB, 네 firmware domain과 다섯 QemuInstance, HW_CONFIG와 UKI OS DTB의 구분 | 01, 02, 04–07 |
| [integration.rst](../../../arm-zena-css/documentation/design/integration.rst) — meta-zena-css-bsp, Yocto build configuration, Yocto layers dependency | reference BSP와 solution layer가 component recipe를 조합하는 방식 | 원본 layer diagram에 없는 HSOC layer와 현재 `bblayers.conf`; root wrapper와 reference kas를 구분 | 02, 03, 05 |
| [boot_process.rst](../../../arm-zena-css/documentation/design/boot_process.rst) — Images layout, Image signing, Measured Boot, Boot Flow, UEFI Secure Boot, Primary Compute reset | signing/FIP/flash bank, RSE-first load·release, AP BL2→BL31/32/33, measurement, reload/reset | ROM 원본 그림의 71 KiB와 현재 recipe 예약 75 KiB, firmware bank와 Nexios WIC A/B rootfs, host loader와 firmware 인증을 구분 | 01, 03–07 |
| [secure_services.rst](../../../arm-zena-css/documentation/design/secure_services.rst) — Architecture, libts/libpsats, SE-Proxy SP, SMM Gateway SP | Linux FF-A/PSA 경로와 U-Boot UEFI variable의 RSE Protected Storage 경로 | TS source·OP-TEE SP composition·TF-M service를 서로 다른 component와 privilege로 연결 | 01, 02, 06 |
| [secure_firmware_update.rst](../../../arm-zena-css/documentation/design/secure_firmware_update.rst) — Introduction, Architecture | UEFI capsule→FWU Proxy→PSA FWU→RSE inactive bank, metadata와 accept 단계 | 현재 two-bank/trial-state configuration을 확인하되 capsule/key 배치와 실제 bank 전환 성공은 별도 결과 | 06 |
| [rse_image_encryption.rst](../../../arm-zena-css/documentation/design/rse_image_encryption.rst) — Encryption approach, Key hierarchy, Boot-time decryption | per-image DEK, AES-128-CTR, AES-KW, ENCKW TLV와 image 인증의 관계 | 원본 GUK→KEK 설명과 현재 `KMU_HW_SLOT_KCE_CM` 기반 key derivation·opaque handle 경로를 구분 | 06 |

### 4.2 Runtime service와 System SW core

| 읽은 RST / 주요 절 | 자료에 반영한 기술 내용 | 현재 Apollo와 구분한 점 | 장 |
|---|---|---|---|
| [power_and_performance_control.rst](../../../arm-zena-css/documentation/design/power_and_performance_control.rst) — Architecture, CPUIdle Design, CPUFreq Design | PSCI/SCMI 경로, cluster별 DVFS domain, 1.8/2.0/2.5 GHz demonstration OPP | 현재 DTS 기본 WFI와 opt-in deep idle, guest-visible frequency와 host TCG 처리량을 구분 | 01, 05, 07 |
| [hipc.rst](../../../arm-zena-css/documentation/design/hipc.rst) — HIPC Baremetal Architecture, RPMsg, Safety Island remoteproc driver | independently booted CL1 attach, 512 KiB resource table/vring/buffer, Name Service·virtual Ethernet | AP `0x00100000`와 CL1 `0xe0130000` alias, 현재 reattach patch, reference OVS/bridge와 실제 image service를 구분 | 01, 02, 05–07 |
| [platform_fault_detection_interface.rst](../../../arm-zena-css/documentation/design/platform_fault_detection_interface.rst) — AP/CL1 Implementation, Out-of-Reset, Online PFDI, Monitoring | AP SMC 경로, CL1 worker/management 경로, CL0 monitor의 결과·timeout 소비 | PFDI interface/test backend/monitor를 구분하며 dummy·예제 test가 physical diagnostic coverage를 뜻하지 않음 | 01, 06, 07 |
| [fmu.rst](../../../arm-zena-css/documentation/design/fmu.rst) — Design and Framework, RD-Aspen FMU Topology, Fault Handling Flow | leaf fault와 parent aggregation, critical/noncritical, SCP event·drain·ACK | QVP System/Root/NI hierarchy와 기존 named-case evidence; 전체 NI endpoint·physical FHI topology는 별도 | 01, 05, 07 |
| [ssu.rst](../../../arm-zena-css/documentation/design/ssu.rst) — FMU-SSU Integration, Finite State Machine | root FMU와 SSU, TEST/SAFE/ERRN/ERRC 상태와 software policy | 원본 FSM과 현재 QVP model의 fault/recovery 동작을 나란히 설명 | 01, 07 |
| [ras.rst](../../../arm-zena-css/documentation/design/ras.rst) — Error types, Primary Compute/Safety Island error processing | CE/DE/UC, Firmware-First handling, TF-A CPER→Linux GHES와 SCP 경로 | QVP register/injection·software consumer 범위와 physical cache ECC/containment를 구분 | 01, 07 |
| [sbistc.rst](../../../arm-zena-css/documentation/design/sbistc.rst) — Hardware, Test Status and Fault Reporting, Design and Framework | core별 chunk, STL status/watchdog, DEADLOCK/TESTSTATUS→FMU→SCP | SBISTC model·notification과 실제 STL 실행·silicon self-test 효과를 구분 | 01, 07 |
| [tfp.rst](../../../arm-zena-css/documentation/design/tfp.rst) — Transient Fault Detection Mechanism, Fault Reaction, Implementation in Software | flop parity fault의 RAS reporting, uncontainable error와 IERR 해석 | QEMU/QVP fault record 경로를 물리 flop parity logic의 검증으로 확장하지 않음 | 01, 07 |
| [smcf.rst](../../../arm-zena-css/documentation/design/smcf.rst) — Overview, Configuration, Software flow | Monitor→MLI→MGI→DMA buffer→SI0 IRQ→SCP consumer, PD_SYSTOP lifecycle | FVP source도 dummy/random이며, 현재 QVP MGI는 register model만 있고 DMA/IRQ/periodic sample delivery는 미구현 | 07 |
| [safety_boot.rst](../../../arm-zena-css/documentation/design/safety_boot.rst) — Safety Island Boot Architecture, Scope and Limitations, LBIST/MBIST, Image Integrity | RSE-oriented safety boot, image·ATU·SCR 점검, LBIST/MBIST의 목적 | FVP LBIST/MBIST dummy 경로와 formal safety qualification 제외를 명시 | 01, 07 |

### 4.3 User Guide와 재현 조건

| 읽은 RST / 주요 절 | 자료에 반영한 내용 | 적용 범위 |
|---|---|---|
| [user_guide/reproduce.rst](../../../arm-zena-css/documentation/user_guide/reproduce.rst) — Download, Kas build, FVP, baremetal/virtualization, BSP, HIPC·PFDI·debugger demo 관련 절 | reference checkout/setup, build target, FVP configuration과 demo prerequisite | reference `kas`/`core-image-minimal` 절차를 현재 root `yocto_build.sh`/Nexios 명령으로 소개하지 않음; demo 명령은 이번에 실행하지 않음 |
| [user_guide/customize.rst](../../../arm-zena-css/documentation/user_guide/customize.rst) — Available build environment variables, Using build environment variables | variant·CPU count·build option의 선택과 override 개념 | reference 선택지, 현재 `build/conf/` 값, recipe default를 구분; 새 `bitbake -e` 결과로 표현하지 않음 |

Arm 문서에 있는 기능도 현재 QVP의 model과 firmware consumer를 함께 확인해야 한다. 특히 encryption, FWU, SMCF와 safety 기능은 configuration 존재·register 구현·end-to-end runtime·physical 효과가 서로 다른 주장이다.

## 5. Diagram과 reference figure의 표현 범위

Apollo seminar 14개는 처음에 Diagram Design 기본 light token과 `1280×720` frame의 HTML/SVG로 작성했고, 현재는 native draw.io object·connector로 변환했다. 본문의 편집 원본은 `.drawio`, 표시 파일은 `.drawio.svg`다. 초기 HTML/SVG는 보존하며 [DIAGRAMS.md](DIAGRAMS.md)에서 비교할 수 있다. 한 장에서 생략한 세부는 본문 표와 상세 도식으로 나눴다.

| Diagram | 그림에서 보여 주는 것 | 요약하거나 생략한 것 |
|---|---|---|
| `01-project-overview` | source → build → execution → evidence | 전체 IP inventory, physical topology |
| `01-address-domains` | system selector와 RSE local ATU window | 모든 ATU region·aperture와 security permission 조합 |
| `02-source-map` | ownership 범주 | 각 범주 안의 모든 Git repository |
| `03-build-pipeline` | firmware/OS/native artifact dependency | 전체 task DAG, parallel scheduling, sstate 분기 |
| `04-qbox-runtime` | launcher/runner와 MMIO transaction | CPU instance별 별도 box, DMI fast path, error path |
| `04-lua-composition` | SoC/VP/Board의 구성 관계 | domain별 helper와 모든 `.apply()` 호출 |
| `04-domain-fabric` | AP/RSE/SI router·ATU와 HIPC shared backing 연결 | 모든 peripheral decode window와 DMI policy |
| `05-fvp-qbox` | software 계약과 model 비교 | 기능별 결과·차이의 전체 목록은 본문 표로 이동 |
| `06-domain-software` | 네 Firmware Domain과 대표 연결 | 전체 channel, AP↔RSE service, RSE→CL1 load edge |
| `06-boot-handoff` | readiness/load/power dependency | 독립 Domain의 실제 timestamp·모든 boot failure branch |
| `07-interrupt-route` | SPI/PPI/NVIC 세 번호 공간 | 모든 IRQ route와 MSI/ITS 상세 |
| `07-mailbox-flow` | SCMI payload와 notification | 실제 방향별 PBX/MBX 개별 instance, HIPC vring sequence |
| `07-timer-watchdog` | CPU Generic Timer와 AP NS Watchdog | SI/RSE watchdog 및 전체 reset tree는 별도 표로 이동 |
| `07-smcf-monitor` | reference sampling data path와 현재 QVP register model 경계 | 실제 sensor 품질·periodic/DMA/IRQ 구현 완료를 뜻하지 않음 |

표의 생략 범위는 미구현 판정이 아니다. 그림의 복잡도를 줄이기 위해 펼쳐 보이지 않은 내용이며, 구현 제한은 각 장에서 별도로 표시했다.

현재 편집 원본은 **Apollo seminar 14개 + Arm reference 24개 + 기존 Phase 1 상세 diagram 23개 = 61개 `.drawio`**다. 동일한 그림을 여러 장에 사용하는 경우 file 수는 한 번만 센다. 7개 장 안내와 32개 상세 문서는 같은 이름의 `.drawio.svg`를 총 77회 삽입하고 각 image 바로 아래에 native source를 연결한다.

Arm reference는 22개의 embedded mxGraph를 복원하고 Compute Complex와 System Management Block 두 PNG는 block·label·관계를 기준으로 native object로 재작성했다. 두 그림의 caption은 재작성임을 명시한다. 최초 SVG/PNG, 이전 표시용 PNG와 저작권·license는 [reference figure index](figures/reference/README.md)에 보존했다. 기존 Phase 1 23개는 8개 multi-page source의 해당 page를 재사용했으며 [전체 index](DIAGRAMS.md)에 기존 source/page ID를 연결한다.

## 6. 이전 reference 보강 단계의 문서 검증

아래는 **native draw.io 전환 이전**에 7개 본문 Markdown, 14개 HTML/SVG와 24개 reference PNG를 대상으로 수행한 결과다. 이전 표시·경로·source 대조의 PASS를 보존하며, 새 61개 draw.io/export의 검증 상태는 다음 절에서 별도로 기록한다.

| 검사 | 결과 | 범위 |
|---|---|---|
| Markdown local link와 image target | PASS | 자료 내부, reference index와 참조 source 경로 존재 확인 |
| 새 HTML accessible SVG / single-file 검사 | PASS, 14개 | skill의 `scripts/self_check.py` |
| Connector / mask geometry | PASS, 14개 | skill repository의 `scripts/verify-geometry.py` |
| SVG export / XML parsing | PASS, 14개 | `scripts/export_svg.py`, XML parser |
| Browser text bounds | PASS, 14개 | node 내부 text와 canvas 바깥 overflow 확인 |
| Narrow viewport / Print CSS | PASS, 14개 | 390px page overflow, diagram scroll, print 시 전체 그림 표시 |
| Markdown image 방식의 SVG 표시 | PASS, 14개 | `<img>` 로딩과 intrinsic size 확인 |
| 본문 Markdown browser rendering | PASS, 7장 | 73개 image insertion의 `img.decode()` 성공, 고유 image 61종 |
| Arm reference render | PASS, 24개 | 원본 SHA unchanged, white opaque PNG, PIL integrity 확인 |
| Visual review | PASS | 전체 contact sheet, reference figure와 대표 확대 그림 확인 |
| Source 의미 대조 | PASS | ABI/build DAG, address·instance, boot·secure service, IRQ·timer·watchdog, SMCF 구현 범위 |
| Source/config snapshot | PASS | 16개 repository HEAD, 3개 local build config hash unchanged |
| Whitespace / table structure | PASS | 새 Markdown·HTML·SVG 검사 |

Browser font와 SVG image의 fallback 표시를 확인했다. SVG를 image로 넣는 renderer는 external font를 제한할 수 있으므로 HTML 표시와 Markdown image 표시를 나누어 확인했다. Viewer마다 font metrics는 다를 수 있다.

Local QA artifact 경로:

| Report | 기록한 내용 |
|---|---|
| [render-report.json](../../../build/qbox-apollo-qvp/seminar-materials-reference-enrichment-20261025/render-report.json) | 새 HTML/SVG의 geometry, browser rendering과 viewport 검사 |
| [reference-render-report.json](../../../build/qbox-apollo-qvp/seminar-materials-reference-enrichment-20261025/reference-render-report.json) | Arm 원본 figure의 white-background PNG export와 대응 정보 |
| [markdown-render-report.json](../../../build/qbox-apollo-qvp/seminar-materials-reference-enrichment-20261025/markdown-render-report.json) | 7개 본문 Markdown의 browser rendering과 image decode |
| [static-report.json](../../../build/qbox-apollo-qvp/seminar-materials-reference-enrichment-20261025/static-report.json) | Markdown link/image/table와 SVG 구조 검사 |
| [source-snapshot.json](../../../build/qbox-apollo-qvp/seminar-materials-reference-enrichment-20261025/source-snapshot.json) | repository revision과 local build config hash |

Report는 문서의 표시·연결·source snapshot을 검증하며 virtual hardware 동작을 검증하지 않는다.

<a id="drawio-validation"></a>

## 7. Native draw.io 전환 검증

앞선 native draw.io 전환 단계에서 61개 graph를 draw.io Desktop에서 import/export하고 당시 7개 본문의 73개 image 연결을 확인했다. 아래 PASS는 그 단계의 native source와 export에 대한 결과이며, 이번 문서 분리 이후의 경로·표시는 다음 절에 기록한다. 22개 Arm 복원본과 23개 Phase 1 재사용본은 원본 graph를 보존했다. SVG의 embedded graph도 source와 비교했으며 default zero 좌표·숫자 표기·named geometry field 순서 등 draw.io의 XML 정규화만 허용했다.

| 검사 | 상태 | 범위 |
|---|---|---|
| Native source inventory | PASS | Seminar 14 + Arm reference 24 + Phase 1 23, 총 61개 |
| mxGraphModel 구조 | PASS | XML parse, unique IDs, root/layer, parent/source/target 참조, edge geometry |
| 편집 가능한 object 확인 | PASS | native text·shape·connector; image cell 0개 |
| Arm 원본 대응 | PASS | embedded graph 22개, PNG 기준 재작성 2개, caption·최초 원본 링크·MIT 유지 |
| Phase 1 source 대응 | PASS | 기존 8개 master의 사용 page 23개와 native cell·geometry 비교 |
| draw.io SVG export | PASS | 61개 `.drawio.svg`, embedded source 일치, 밝은 배경 표시 |
| Markdown 연결 | PASS | 7장 73회 image, 바로 아래 편집 링크 73개, 고유 pair 61종 |
| Browser / visual review | PASS | SVG 61개 decode, Desktop PNG 61개, contact sheet와 확대 그림 확인 |
| 원본 보존 / local links | PASS | 기존 HTML/SVG/PNG와 Arm·Phase 1 원본 유지, source/render 링크 |

Mailbox sequence는 lifeline의 native invisible port에 message를 연결하여 8개 request/response의 시간 위치를 유지했다. Compute Complex는 대표 core를 그린 축약이며 DSU/L3가 cluster별 구성임을 표시했다. Font 파일은 내장하지 않아 설치된 font에 따라 글자 폭이 달라질 수 있다.

이번 단계의 local QA artifact:

| Report | 기록한 내용 |
|---|---|
| [drawio-report.json](../../../build/qbox-apollo-qvp/seminar-drawio-20261025/drawio-report.json) | Native graph 구조·편집성·source 대응과 draw.io export 검사 |
| [report.json](../../../build/qbox-apollo-qvp/seminar-drawio-20261025/report.json) | 전체 Markdown link/image와 browser/visual QA 결과 |
| [phase1-manifest.json](../../../build/qbox-apollo-qvp/seminar-drawio-20261025/phase1-manifest.json) | 기존 SVG/master page → local native source 23개 매핑과 XML·hash 검사 |

기존 master 8개는 provenance source이며 그 안의 미사용 page 전체를 재검증한 것은 아니다. 이번 표시·편집 검증 대상은 세미나에서 사용하는 single-page 61개다.

이 report도 local generated artifact이며 다른 clone에는 없을 수 있다. 문서의 편집성과 표시를 확인하는 검사이며 virtual hardware runtime을 검증하지 않는다.

<a id="deep-dive-validation"></a>

## 8. Subchapter 분리와 기술 심화 검증

기존 7개 장은 개요·책임·읽기 순서를 안내하는 문서로 유지하고 상세 내용을 32개 Markdown으로 분리했다. 단순한 분량 분할에 그치지 않고 목적→구성→동작 순서→interface와 완료 조건→source 추적→실패 진단으로 설명을 확장했다. 전체 Markdown은 index·source·reference 안내 4개를 포함해 43개다.

| 장 | 상세 문서 | 심화한 source 계약 |
|---|---:|---|
| 01 Overview | 3 | Hardware/firmware/control boundary, privilege·lifetime, CL1 alias 계산, recovery state 수명 |
| 02 Source | 3 | Git ownership, source/recipe/provider, external Linux module과 CL1 patch의 consumer |
| 03 Build | 5 | Configuration precedence, task graph/native provider, firmware signing/Flash, OS integrity/storage, runtime artifact |
| 04 QBox | 4 | Launcher input, ModuleFactory·QOM lifecycle, ctx/platform composition, address/DMI/IRQ/time |
| 05 Comparison | 3 | Matching baseline, topology/IP mechanism, named profile·provenance·FVP reference gate |
| 06 Domain SW | 6 | Boot hooks/ATU, AP FF-A, TF-M SPM/manifest, FWU bank/key, SCP event/bind, CL1 reattach |
| 07 System Core | 8 | IRQ dispatch, SCMI token/timeout, comparator scheduling, recovery deadline, DVFS completion, PFDI generation, FMU ACK, SMCF data delivery |

### Source 설명의 정확도를 보완한 사례

- **HIPC source owner:** AP `arm_si_rproc`은 `sw-ref-stack`의 외부 kernel module이며 CL1 reattach는 Yocto integration patch까지 따라간다. [Source tracing](02-source/03-change-tracing-and-diagnosis.md)과 [Zephyr HIPC](06-software/06-zephyr-and-hipc.md)에 양쪽 publication·attach 경계를 연결했다.
- **Validation policy:** 현재 allowlist의 11개 named QBox profile은 standalone 실행을 허용한다. Reference를 제공하면 별도 strict gate를 적용한다. [비교 evidence](05-comparison/03-evidence-and-diagnosis.md)는 실행 policy와 runtime PASS, FVP/QVP WIC 동일성 여부를 구분한다.
- **TF-M partition:** Global IPC SPM 선택과 개별 service manifest의 SFN/IPC model은 다른 설정이다. [RSE runtime](06-software/03-rse-and-psa-runtime.md)과 [FWU](06-software/04-secure-firmware-update.md)에서 실제 manifest와 state machine을 따라간다.
- **PFDI restart:** generation 전환은 모든 power notification의 자동 효과가 아니다. 현재 AP watchdog recovery의 명시적 `prepare_restart()`와 일반 OFF/ON 처리를 [PFDI monitor](07-system/06-pfdi-and-monitoring.md)에 나누어 적었다.
- **FMU notification:** ACK 성공, atomic notification enqueue 성공, consumer handler 실행은 다른 관측 지점이다. 실패 후 mask 유지와 `recover()` 재개 조건은 [Fault management](07-system/07-fmu-ssu-and-ras.md)에서 설명한다.

### 문서와 그림 검사

| 검사 | 결과 | 적용 범위 |
|---|---|---|
| 문서 구조 | PASS | 장 안내 7개 + 상세 32개, 상세별 상위·이전·다음 읽기 연결 |
| Local link·Markdown anchor·table | PASS | 전체 43개 Markdown; source·편집 원본·목차 상대경로 확인 |
| Diagram 삽입과 native 연결 | PASS | 77회 삽입, 고유 SVG/draw.io pair 61종, 원본 누락 없음 |
| Browser rendering | PASS | 7개 장 안내 + 상세 32개, 표시 이미지 77회 decode 및 본문 overflow 검사 |
| 기존 자산 보존 | PASS | Markdown 이외 기존 자산 175개의 SHA-256 동일 |
| Source snapshot | PASS | 기존 16개 repository HEAD와 local config 3개 hash 동일 |
| Source 의미 검토 | PASS | 선택된 함수·config·manifest의 설명 대조; runtime 실행 결과를 주장하지 않음 |

이번 작업에서 graph geometry와 export는 변경하지 않았다. SHA-256이 같은 61개 graph/export의 편집성·Desktop import/export·확대 visual 검증은 앞선 native 전환 결과를 유지하며, 이번에는 새 문서 위치의 링크와 표시를 확인했다. 그림 재export를 새로 수행했다고 주장하지 않는다.

| Local generated report | 기록 |
|---|---|
| [static-report.json](../../../build/qbox-apollo-qvp/seminar-deep-dive-20261025/static-report.json) | 전체 문서·상대경로·anchor·table·image/native 연결·asset hash |
| [browser-render-report.json](../../../build/qbox-apollo-qvp/seminar-deep-dive-20261025/browser-render-report.json) | 분리한 본문의 image decode와 viewport 표시 |
| [source-snapshot.json](../../../build/qbox-apollo-qvp/seminar-deep-dive-20261025/source-snapshot.json) | 16개 repository revision과 3개 local build config 비교 |

Report는 local generated artifact이므로 다른 clone에는 없을 수 있다. 문서의 구조·표시·source 설명에 대한 검사이며 QBox/FVP runtime qualification은 아니다.

## 9. 실행하지 않은 검사와 과거 기록

| 항목 | 이번 작업 |
|---|---|
| `bitbake -e`, provider/image rebuild | 미실행 |
| QBox / FVP boot, post-login suite | 미실행 |
| Physical timing, cache coherence, silicon safety | 검증 대상 아님 |
| 과거 FMU hierarchy result | 기존 JSON을 읽고 당시 범위로만 인용 |

과거 [FMU hierarchy result](../../../build/qbox-apollo-qvp/fmu-hierarchy-20261024/verification-summary.json)의 `guest-2` 결과를 현재 모든 source revision에 재적용하지 않는다. 특히 AP16, 전체 NI topology, physical ECC/CRC/DCLS/PING 및 timing 한계는 그 기록 자체에 남아 있다.
