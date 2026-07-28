---
name: update-local-build-conf
description: Compare Apollo local-build inputs with the active Yocto recipe environments, review differences, and update scripts/build/local_build.conf without adding runtime BitBake lookups. Use when Yocto machine, firmware platform, kernel, QBox, boot arguments, or UKI packaging metadata changes and the manually maintained local build configuration must be refreshed.
---

# Update Local Build Config

Refresh `scripts/build/local_build.conf` as an explicit maintenance operation.
Never connect the collector or its JSON output to `local_build.sh` runtime
execution.

## Workflow

1. Work from `/build/arm/arm-auto-solutions`. Inspect `git status --short`,
   `scripts/build/local_build.conf`, `build/conf/local.conf`,
   `build/conf/bblayers.conf`, and `build/conf/templateconf.cfg`. Preserve
   unrelated user changes.
2. Confirm that the active Yocto machine is the machine intended for the local
   build. If the two machines differ, report the difference before editing.
3. Capture a new review artifact explicitly:

   ```bash
   review_dir="build/local-build-conf-review/$(date +%Y%m%d-%H%M%S)"
   mkdir -p "${review_dir}"
   python3 scripts/build/collect_yocto_local_build_vars.py \
     --build-dir build \
     --output "${review_dir}/yocto-vars.json"
   ```

4. Compare only the mappings below. Treat whitespace-only differences in boot
   arguments as equivalent and keep QBox source paths workspace-relative via
   `${ROOT_DIR}`.

| `scripts/build/local_build.conf` | Recipe | Yocto variable |
| --- | --- | --- |
| `MACHINE` | `nexios-image` | `MACHINE` |
| `RD_ASPEN_VARIANT` | `nexios-image` | `RD_ASPEN_VARIANT` |
| `PC_CPUS_COUNT` | `nexios-image` | `PC_CPUS_COUNT_DEFAULT` |
| `BOOTLOADER_LINUX_APPEND` | `nexios-image` | `BOOTLOADER_LINUX_APPEND` |
| `UBOOT_MACHINE` | `u-boot` | `UBOOT_MACHINE` |
| `LINUX_DEFCONFIG` | `linux-yocto-rt` | `KBUILD_DEFCONFIG` |
| `KERNEL_DEVICETREE` | `linux-yocto-rt` | `KERNEL_DEVICETREE` |
| `OPTEE_PLATFORM` | `optee-os` | `PLATFORM` |
| `TF_A_PLATFORM` | `trusted-firmware-a` | `TF_A_PLATFORM` |
| `TFM_PLATFORM` | `trusted-firmware-m` | `TFM_PLATFORM` |
| `SCP_PLATFORM` | `scp-firmware` | `SCP_PLATFORM` |
| `ZEPHYR_BOARD` | `zephyr-demos-cl1` | `ZEPHYR_BOARD` |
| `QBOX_APOLLO_BUILD_TARGET` | `qbox-apollo-qvp-native` | `QBOX_APOLLO_BUILD_TARGET` |
| `QBOX_CORE_DIR` | `qbox-apollo-qvp-native` | `HSOC_APOLLO_QBOX_SRC` |
| `QBOX_PLATFORM_DIR` | `qbox-apollo-qvp-native` | `HSOC_APOLLO_QBOX_PLATFORM_SRC` |
| `QBOX_QEMU_DIR` | `qbox-apollo-qvp-native` | `HSOC_APOLLO_QEMU_SRC` |
| `EFI_ARCH` | `nexios-image` | `EFI_ARCH` |
| `INITRD_ARCHIVE` | `nexios-image` | `INITRD_ARCHIVE` |
| `AUTO_AD_NEXIOS_UKI_A` | `nexios-image` | `AUTO_AD_NEXIOS_UKI_A` |
| `AUTO_AD_NEXIOS_UKI_B` | `nexios-image` | `AUTO_AD_NEXIOS_UKI_B` |
| `AUTO_AD_NEXIOS_UKI_CMDLINE_A` | `nexios-image` | `AUTO_AD_NEXIOS_UKI_CMDLINE_A` |
| `AUTO_AD_NEXIOS_UKI_CMDLINE_B` | `nexios-image` | `AUTO_AD_NEXIOS_UKI_CMDLINE_B` |
| `UKIFY_CMD` | `nexios-image` | `UKIFY_CMD` |
| `UEFI_SECURE_BOOT` | `nexios-image` | `UEFI_SECURE_BOOT` |
| `UKI_SB_KEY` | `nexios-image` | `UKI_SB_KEY` |
| `UKI_SB_CERT` | `nexios-image` | `UKI_SB_CERT` |

5. Present the old value, captured value, and proposed value for every real
   difference. Update only reviewed assignments in
   `scripts/build/local_build.conf` with `apply_patch`. Do not edit component
   repositories or Yocto metadata.
6. Validate the result:

   ```bash
   bash -n scripts/build/local_build.conf local_build.sh \
     scripts/build/local_build_common.sh \
     scripts/build/modules/package_fvp_local.sh
   python3 scripts/test/audit_local_build_yocto_parity.py \
     --vars "${review_dir}/yocto-vars.json" \
     --output "${review_dir}/parity-audit.json"
   ./local_build.sh qbox --dry-run
   ```

7. Confirm that runtime code has no cache or collector dependency:

   ```bash
   ! rg 'APOLLO_LOCAL_BUILD_(USE_YOCTO_VARS|YOCTO_VARS)|collect_yocto_local_build_vars' \
     local_build.sh scripts/build/local_build_common.sh \
     scripts/build/modules/package_fvp_local.sh
   ```

Report the capture artifact path, reviewed changes, validation commands, and
any failed or intentionally deferred comparison. If collection fails, leave
`scripts/build/local_build.conf` unchanged and report the BitBake failure.
