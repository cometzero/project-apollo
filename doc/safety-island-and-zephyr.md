# Safety Island And Zephyr Analysis

Generated: 2026-05-15

## Summary

The Safety Island is a Cortex-R82AE subsystem. In CFG2, Safety Island Cluster 1
adds four SMP cores and runs Zephyr. Apollo now carries the full Zephyr project
workspace under `hsoc-stack/components/system_mgmt/zephyrproject/` so the
Safety Island CL1 image can be built either through Yocto `EXTERNALSRC` or
through `./local-build.sh zephyr`. The important cross-domain features are HIPC
over MHUv3/shared SRAM/RPMsg and PFDI on both Primary Compute and Safety Island
CL1.

## Platform Role

The Zena overview states that the platform combines Primary Compute,
Safety Island, and RSE. The Safety Island is Cortex-R82AE and is used for
real-time services and safety monitoring
(`arm-zena-css/documentation/overview.rst:20`,
`arm-zena-css/documentation/overview.rst:22`,
`arm-zena-css/documentation/overview.rst:23`,
`arm-zena-css/documentation/overview.rst:24`).

The components design document describes the Safety Island block as one or more
Cortex-R82AE clusters. SCP-firmware handles power, clock, CMN control, runtime
power services, and platform-side SCMI
(`arm-zena-css/documentation/design/components.rst:72`,
`arm-zena-css/documentation/design/components.rst:75`,
`arm-zena-css/documentation/design/components.rst:76`,
`arm-zena-css/documentation/design/components.rst:95`,
`arm-zena-css/documentation/design/components.rst:97`,
`arm-zena-css/documentation/design/components.rst:104`).

## CFG1 vs CFG2

CFG1 has one Safety Island cluster with a dual lock-step core pair. CFG2 adds a
second cluster with four SMP cores and supports Safety Island GIC multi-view
(`arm-zena-css/documentation/design/components.rst:79`,
`arm-zena-css/documentation/design/components.rst:80`,
`arm-zena-css/documentation/design/components.rst:81`,
`arm-zena-css/documentation/design/components.rst:82`,
`arm-zena-css/documentation/design/components.rst:148`,
`arm-zena-css/documentation/design/components.rst:149`,
`arm-zena-css/documentation/design/components.rst:150`).

The current generated config selects CFG2 (`.config.yaml:15`,
`.config.yaml:26`).

## Zephyr Module Layout

The Yocto include file originally set:

- `ZEPHYR_SAFETY_ISLAND_MODULE =
  "${ARM_ZENA_CSS_REPO_DIRECTORY}/components/safety_island/zephyr/src"`
- `ZEPHYR_MODULES:append = "${ZEPHYR_SAFETY_ISLAND_MODULE};"`

Evidence:
`arm-zena-css/yocto/meta-zena-css-safety-island/recipes-kernel/zephyr-kernel/zephyr_arm_safety_island.inc:26`,
`arm-zena-css/yocto/meta-zena-css-safety-island/recipes-kernel/zephyr-kernel/zephyr_arm_safety_island.inc:29`.

The Zephyr module declares local `cmake`, `kconfig`, `board_root`, `dts_root`,
and `soc_root` settings in `module.yml`
(`arm-zena-css/components/safety_island/zephyr/src/zephyr/module.yml:6`,
`arm-zena-css/components/safety_island/zephyr/src/zephyr/module.yml:7`,
`arm-zena-css/components/safety_island/zephyr/src/zephyr/module.yml:8`,
`arm-zena-css/components/safety_island/zephyr/src/zephyr/module.yml:9`,
`arm-zena-css/components/safety_island/zephyr/src/zephyr/module.yml:10`,
`arm-zena-css/components/safety_island/zephyr/src/zephyr/module.yml:11`,
`arm-zena-css/components/safety_island/zephyr/src/zephyr/module.yml:12`).

The top-level CMake entry adds `drivers`, `lib`, and `subsys`
(`arm-zena-css/components/safety_island/zephyr/src/CMakeLists.txt:7`,
`arm-zena-css/components/safety_island/zephyr/src/CMakeLists.txt:9`,
`arm-zena-css/components/safety_island/zephyr/src/CMakeLists.txt:10`,
`arm-zena-css/components/safety_island/zephyr/src/CMakeLists.txt:11`).
The top-level Kconfig sources `drivers/Kconfig` and `subsys/Kconfig`
(`arm-zena-css/components/safety_island/zephyr/src/Kconfig:7`,
`arm-zena-css/components/safety_island/zephyr/src/Kconfig:8`).

## Board And SoC

The board metadata names `fvp_rd_aspen_safety_island_c1` and binds it to
`fvp_aemv8r_aarch64`
(`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/board.yml:6`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/board.yml:7`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/board.yml:10`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/board.yml:11`).

The board YAML marks the target as `arm64`, type `sim`, with Zephyr and
cross-compile toolchains
(`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.yaml:6`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.yaml:8`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.yaml:9`,
`arm-zena-css/components/safety_island/zephyr/src/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.yaml:10`).

## Safety Island Features

The source tree contains Zephyr overlays for:

- `hipc`
- `pfdi`
- `pfdi_agent`
- `zperf`

It also contains drivers for virtual Ethernet over RPMsg, PFDI, PFDI agent, and
MHUv3 mailbox:

- `drivers/ethernet/veth_rpmsg.c`
- `drivers/pfdi/pfdi_module.c`
- `drivers/pfdi_agent/pfdi_agent.c`
- `drivers/mbox/mbox_mhuv3.c`

These paths were found under
`arm-zena-css/components/safety_island/zephyr/src/`. Apollo-specific board,
DTS, Kconfig, and overlay integration now lives under
`hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/`.

## HIPC

The HIPC design is explicitly for communication between Armv9-A Primary Compute
and Armv8-R AArch64 Safety Island using MHUv3 and shared SRAM
(`arm-zena-css/documentation/design/hipc.rst:17`,
`arm-zena-css/documentation/design/hipc.rst:18`,
`arm-zena-css/documentation/design/hipc.rst:19`,
`arm-zena-css/documentation/design/hipc.rst:20`).

Zephyr is deployed on Safety Island CL1 in RD-Aspen CFG2, and HIPC is between
Primary Compute and Safety Island CL1
(`arm-zena-css/documentation/design/hipc.rst:23`,
`arm-zena-css/documentation/design/hipc.rst:26`,
`arm-zena-css/documentation/design/hipc.rst:27`).

The communication stack uses Linux remoteproc/RPMsg on Primary Compute and
OpenAMP/RPMsg on Zephyr
(`arm-zena-css/documentation/design/hipc.rst:50`,
`arm-zena-css/documentation/design/hipc.rst:51`,
`arm-zena-css/documentation/design/hipc.rst:55`,
`arm-zena-css/documentation/design/hipc.rst:56`,
`arm-zena-css/documentation/design/hipc.rst:94`,
`arm-zena-css/documentation/design/hipc.rst:96`,
`arm-zena-css/documentation/design/hipc.rst:97`).

The shared memory layout is 512 KiB with a resource table, two vrings, and an
RPMsg Virtio buffer (`arm-zena-css/documentation/design/hipc.rst:87`,
`arm-zena-css/documentation/design/hipc.rst:89`,
`arm-zena-css/documentation/design/hipc.rst:90`,
`arm-zena-css/documentation/design/hipc.rst:91`).

## PFDI

PFDI is a modular framework for hardware fault detection and reporting
(`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:16`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:17`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:19`).

The Primary Compute PFDI flow crosses user space, Linux ioctl, SMC, and TF-A
firmware execution
(`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:114`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:116`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:121`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:123`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:127`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:129`).

Safety Island CL1 PFDI is implemented on Zephyr, with a PFDI driver, subsystem,
and shell utility
(`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:167`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:173`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:176`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:186`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:194`).

Unlike the AP-side interface, Safety Island CL1 does not expose PFDI through SMC
because Cortex-R82AE lacks EL3 Secure Monitor in this execution model; it runs
as a local secure EL1 firmware service in Zephyr
(`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:209`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:211`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:213`,
`arm-zena-css/documentation/design/platform_fault_detection_interface.rst:217`).

## Build Artifacts

The current deploy directory contains Safety Island artifacts:

- `si0_ramfw.elf`
- `si0_ramfw.bin`
- `zephyr-demos-cl1.elf`
- `zephyr-demos-cl1.bin`
- `signed_safety_island_cl1.bin`
- `signed_capsule_safety_island_cl1.bin`

These are local build outputs under
`build/tmp_baremetal/deploy/images/fvp-rd-aspen/`, not source files.

Apollo local builds produce the CL1 Zephyr image with:

```bash
./local-build.sh zephyr
```

The generated files are installed under
`build/local-apollo-fvp/deploy/firmware/zephyr-demos-cl1.bin` and
`build/local-apollo-fvp/deploy/firmware/zephyr-demos-cl1.elf`. The full
`./local-build.sh build` flow uses those local artifacts when signing the
Safety Island CL1 firmware image.

## Change Guidance

- For Apollo Zephyr board, DTS, Kconfig, CMake, or overlay changes, start under
  `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src`.
- For common Safety Island Zephyr driver, library, subsystem, or sample app
  changes, start under `arm-zena-css/components/safety_island/zephyr/src`.
- For Zephyr RTOS core or module dependency changes, start under
  `hsoc-stack/components/system_mgmt/zephyrproject`.
- For Apollo Yocto build integration of Zephyr CL1 images, start in
  `hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel`. Use
  `arm-zena-css/yocto/meta-zena-css-safety-island/recipes-kernel/zephyr-kernel`
  for upstream/common Safety Island recipe changes.
- For AP-side HIPC and Linux remoteproc/RPMsg integration, inspect
  `sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel`.
- For PFDI behavior, separate AP-side SMCCC/SMC paths from Safety Island local
  Zephyr firmware service paths before changing interfaces.
