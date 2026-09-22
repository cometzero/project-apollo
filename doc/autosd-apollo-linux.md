# AutoSD nightly on Apollo Linux

The `--autosd` mode of `run_qemu_linux.sh` and `run_qbox_linux.sh` boots
an AutoSD disk with the Apollo Yocto BSP kernel and the **original AutoSD
dracut initramfs**. It does not replace AutoSD userspace or import its
6.12 kernel modules into the Apollo 6.18 kernel. Required boot drivers and
filesystems must be built into the Apollo kernel.

Upstream documentation is pinned in the `autosd/sig-docs` submodule:

- [Get AutoSD](../autosd/sig-docs/docs/discover/get-autosd.md)
- [Sample images](../autosd/sig-docs/docs/getting-started/autosd-sample-images.md)
- [OSTree filesystem](../autosd/sig-docs/docs/building/understanding_ostree-file-system.md)
- [Composefs](../autosd/sig-docs/docs/features-and-concepts/con_tamperproof.md)

Additional source checkouts for this integration belong under `autosd/`.
Downloaded images and preparation output belong under `build/autosd/`.
`autosd/composefs` pins the upstream mount implementation used to inspect
the EROFS-to-loop-device fallback.

## Prepare images

Install `qemu-img` and `guestfish` (Ubuntu packages `qemu-utils` and
`guestfish`) with a usable libguestfs appliance. No privileged host mount
is used. A readable host kernel is required by supermin; when `/boot/vmlinuz-*`
is restricted, extract the matching distribution kernel package under
`build/autosd/host-tools/` and set `SUPERMIN_KERNEL` to its readable vmlinuz.
`LIBGUESTFS_BACKEND=direct` avoids requiring a system libvirt connection.

```sh
LIBGUESTFS_BACKEND=direct python3 scripts/prepare_autosd.py
```

Use `--build-id 2869696176.466d2e78` to select the evaluated nightly,
`--mode regular` or `--mode ostree` to prepare only one image, and
`--guestfish /path/to/guestfish` for a locally extracted tool.

The helper verifies each compressed image against the publisher's SHA256,
retains the compressed and qcow2 files, converts to sparse raw, discovers
the ext4 root and BLS boot entry, and extracts its initramfs read-only.
The resulting `regular.json` and `ostree.json` record source URLs, hashes,
boot entry, initrd and raw disk paths. These checks detect download corruption;
they do not establish a Secure Boot chain.

Boot arguments retain the image's root UUID and OSTree deployment path.
The helper replaces the original console selections with Apollo PL011 and
removes `rd.modules-load=nvme,virtio_mmio`: these drivers are built into
Apollo, and the image's modules have a different kernel ABI.
Boot logs are enabled on the UART with `loglevel=7`,
`systemd.show_status=yes` and `rd.systemd.show_status=yes`; upstream quiet
and graphical splash options are removed. Re-running the preparation helper
also refreshes these arguments in cached manifests without rebuilding images.

## Build and boot

```sh
./yocto_build.sh --keep-conf --bsp
./yocto_build.sh --keep-conf qemu-apollo-native

./run_qemu_linux.sh --autosd build/autosd/regular.json \
    --headless --exit-after-pass --timeout 180
./run_qemu_linux.sh --autosd build/autosd/ostree.json \
    --headless --exit-after-pass --timeout 180

./run_qbox_linux.sh --autosd build/autosd/regular.json \
    --headless --exit-after-pass --timeout 300
./run_qbox_linux.sh --autosd build/autosd/ostree.json \
    --headless --exit-after-pass --timeout 300
```

Omit `--headless` to use the existing tmux console. The sample image credentials
are `root` / `password`; the launcher responds to those login prompts.
`--autosd` and `--bsp` are mutually exclusive. Explicit `--kernel`, `--initrd`,
`--rootfs`, and `--bootargs` still override defaults. Use `--netdev user,id=net0`
with QEMU to omit its default localhost SSH port forwarding.

Each launch copies the raw disk into its own output directory. QEMU defaults
to `build/qemu-apollo-qvp/`; QBox defaults to `build/qbox-apollo-qvp/`.
`launch.json`, `linux-uart.log`, emulator log and `result.json` retain evidence.
`--exit-after-pass` requires an actual guest command response: AutoSD identity,
CPU count, disk read, and for OSTree `/run/ostree-booted`, `ostree admin status`,
an overlay root. Mounts, loop devices, SELinux state and failed services are printed
for diagnosis. This is a boot smoke check, not a complete service qualification.
The evaluated AutoSD 10 nightly provides `ostree` and `bootc`, not
`rpm-ostree`; `bootc status` can be used for additional interactive inspection.

## Yocto UKI with standalone QEMU

The deployed BSP UKI cannot boot AutoSD unchanged: its initramfs starts the
BSP test shell, its command line selects `/init`, and its embedded DTB describes
the full platform rather than standalone QEMU. The normal Apollo U-Boot also
expects secure-world services that this machine does not implement.

Build the BSP UKI and its standalone firmware/UKIBoot prerequisites:

```sh
./yocto_build.sh --keep-conf --bsp
./run_qemu_linux.sh --autosd build/autosd/regular.json \
    --uki build/tmp_baremetal/deploy/images/apollo-qvp/nexios-bsp-initramfs-a.efi \
    --headless --exit-after-pass --timeout 180
./run_qemu_linux.sh --autosd build/autosd/ostree.json \
    --uki build/tmp_baremetal/deploy/images/apollo-qvp/nexios-bsp-initramfs-a.efi \
    --headless --exit-after-pass --timeout 180
```

`--uki` requires `--autosd` and rejects `--kernel`/`--dtb`. It creates
`autosd.efi` in the run directory, replaces `.initrd`, `.cmdline` and `.osrel`,
and removes `.dtb` to use the firmware-supplied QEMU DT. The source UKI and
all other PE sections, including `.linux` and the EFI stub, are preserved;
their hashes are recorded in `launch.json`. A GNU AArch64 `objcopy` supporting
`--change-section-vma` is required. Signed images and signed PCR policies
are rejected, not silently invalidated.

The regular nightly's legacy LZ4 stream ends at EOF without a zero-length
terminator. UKI stubs can append credential cpio archives, which would then
be misread as another LZ4 block. For a complete legacy block stream ending
exactly at EOF, the adapter adds a four-byte zero terminator to the embedded
copy only. No files are unpacked or recompressed. The original initrd and
OSTree's already terminated LZ4 plus trailing gzip cpio are unchanged;
input/embedded hashes and this normalization are recorded in `launch.json`.

The launcher validates both GPT copies and installs the adapted UKI into
`ukiboot_a` and `ukiboot_b` on its private disk copy. Both slots initially
contain the same bootstrap kernel/initrd/root selection, not two different
OS deployments. The downloaded image, GPT and root filesystem are preserved.
Existing boot-control metadata is never initialized or marked successful by
the host. Each launch refreshes both UKI slots, so this is not an OTA deployment
tool and must not be used to preserve independently updated slot contents.

The Yocto-built `ukibootaa64.efi` is installed as `/EFI/BOOT/BOOTAA64.EFI`, with
its A/B addons under `/EFI/BOOT/ukiboot_{a,b}.efi.extra.d/`. U-Boot loads this
file from the ESP with `fatload` and executes `bootefi`. UKIBoot then initializes
invalid metadata, chooses a slot, decrements trial attempts and chainloads
the raw UKI partition. Its matching addon supplies `androidboot.slot_suffix`;
manually supplying that argument is rejected. This is neither a host-selected
slot nor an extracted-kernel direct boot.

UKI mode requires at least 1 GiB RAM, limits UKI preparation to 256 MiB and
also checks the actual slot capacity (128 MiB in the evaluated nightly).
UART logs include U-Boot, UKIBoot, EFI, kernel and systemd output.
`--exit-after-pass` requires `/sys/firmware/efi`, a slot suffix, active
`ukiboot-set-success.service`, matching `ukibootctl get-booted/get-active`,
and a CRC-valid on-disk state with `successful_boot=1`, `tries_remaining=0`
for the booted slot after QEMU exits. `result.json` retains that state.
`--uboot PATH` overrides firmware; `--ukiboot-dir DIR` overrides the deployed
loader/addon directory. Host `mtools` is required for unprivileged ESP editing.
The original full-platform U-Boot artifact is not replaced.

UKI mode adds `efi=runtime` unless an explicit `efi=` argument is present:
the PREEMPT_RT kernel otherwise disables EFI runtime services by default.
This mode does not qualify real-time latency, Secure Boot, persistent EFI
variables, or an end-to-end OTA update/rollback between distinct OS versions.

### UKIBoot requirements and the invalid-partition failure

The pinned [UKIBoot source and protocol](../autosd/ukiboot/README.md) describe
the three raw partitions and CRC-protected 24-byte control structure:

| Partition | GPT type | Nightly capacity |
| --- | --- | --- |
| `ukiboot_a`, `ukiboot_b` | `DF331E4D-BE00-463F-B4A7-8B43E18FB53A` | 128 MiB each |
| `ukibootctl` | `FEFD9070-346F-4C9A-85E6-17F07F922773` | 1 MiB |

Both downloaded nightlies have 512 literal `X` bytes at the start of
`ukibootctl`, intentionally awaiting loader initialization. The former
direct-UKI path skipped UKIBoot, so the userspace success service rejected
the sentinel as `Bootctl partition is invalid`. The new path lets the actual
loader initialize it and the unmodified AutoSD service record success.

Required firmware facilities include partition Block I/O and Partition Info,
loaded-image device paths, Simple File System for addons, CRC32, and buffered
`LoadImage`/`StartImage`. Apollo U-Boot supplies these. Its DT handoff provides
the standalone hardware map. Apollo-only `gnu-efi` uses baseline
`-march=armv8-a`, and UKIBoot uses `-mgeneral-regs-only`: CPU-tuned SVE code in
`RtZeroMem` otherwise traps before the loader starts. GNU-EFI's floating-point
formatting requires the baseline FP ABI. No guest service is masked or forced
successful.

`ukiboot_0.2.1.bb` builds from the `autosd/ukiboot` submodule, revision
`ec869c79ea10741e8bd0c8043e4f2c0c5b740ce2`. The BSP image's Apollo-QVP-only
deploy dependencies include UKIBoot and standalone U-Boot; neither is added
to the BSP initramfs or its original boot disk.

## Preserve native AIB UKIs for OTA testing

Standalone QEMU can boot an existing raw AutoSD AIB disk without extracting
BLS entries or replacing its UKIs:

```sh
./run_qemu_linux.sh --native-autosd-disk /absolute/path/base.raw \
  --native-autosd-mode ostree --headless --timeout 180
```

This creates a private sparse copy, checks both GPTs and bootctl, and hashes
the complete A/B and control partitions before/after preparation. The native
UKIs and control bytes are preserved. The default also preserves the ESP.
Explicit `--ukiboot-dir build/tmp_baremetal/deploy/images/apollo-qvp` installs
only the known Apollo EFI loader/addons into that private ESP. No external
kernel, initramfs or command-line override is accepted; configure those in AIB.
Use `--native-autosd-mode regular` for a non-OSTree image.

After a completed run, combine the original `--native-autosd-disk` argument
with `--reuse-autosd-disk PREVIOUS_OUT_DIR` to retain updates across launches.
Omit `--ukiboot-dir` on reuse: neither slots nor ESP are rewritten. This is
not evidence of a guest-initiated automatic rollback, which must be observed
separately. Native preservation was boot-tested with a prepared regular image
in `build/autosd/qemu-native-uki-regular-smoke/`; fresh AIB/OTA validation is
tracked in [the follow-up report](autosd-remaining-validation-ko.md).

## Kernel requirements

Both evaluated images use ext4 for the root partition, LZ4-compressed dracut
initramfs, and virtio block. Apollo already supplies these drivers built-in.
The OSTree image sets `[composefs] enabled=signed` and transient `/etc` in
`usr/lib/ostree/prepare-root.conf`.

`arch/arm64/configs/apollo_qvp_defconfig` adds:

| Option | Purpose |
| --- | --- |
| `CONFIG_EROFS_FS=y` | Composefs metadata filesystem |
| `CONFIG_EROFS_FS_BACKED_BY_FILE=n` | Use composefs's loop-device fallback; avoid exceeding the filesystem stacking limit with transient `/etc` |
| `CONFIG_FS_VERITY=y` | Authenticate composefs backing files on ext4 |
| `CONFIG_AUDIT=y` | AutoSD audit service and SELinux dependency |
| `CONFIG_SECURITYFS=y` | Security subsystem filesystem |
| `CONFIG_SECURITY_SELINUX=y` | Load and enforce the supplied AutoSD policy |
| `CONFIG_SECURITY_SELINUX_BOOTPARAM=y` | Standard explicit SELinux boot control |

Overlayfs, ext4 security labels, loop devices and initrd decompression were
already enabled. EROFS xattrs/security labels are enabled by its Kconfig
defaults. Neither XFS nor a replacement initramfs is needed for these images.

File-backed EROFS in this Linux 6.18 tree adds one to `s_stack_depth`
(`fs/erofs/super.c`). Composefs adds an overlay, and AutoSD's transient
`/etc` adds another, exceeding `FILESYSTEM_MAX_STACK_DEPTH=2`. The observed
failure is `overlayfs: maximum fs stacking depth exceeded` followed by
`ostree-prepare-root.service` failure. Disabling only file-backed EROFS makes
the EROFS file mount return `ENOTBLK`; libcomposefs then mounts through a loop
device (`libcomposefs/lcfs-mount.c` in the pinned composefs source). This keeps
the upstream stack limit and signed composefs configuration intact.
The temporary EROFS backing mount is detached after creating the composefs
overlay, so its absence from `/proc/mounts` is expected. The loop device
backing `.ostree.cfs`, overlay root and successful OSTree initialization are
the relevant runtime evidence.

## Qualification boundary

Both launchers boot the AP directly: TF-A, U-Boot, RSE and SI firmware do not
execute. QBox retains its documented mock domain services. AutoSD UKI boot
selection, Secure Boot, OTA updates, rollback, and full-system Apollo/FVP
behavior are not qualified by these runs. The direct boot kernel and initrd
are not automatically updated by an AutoSD deployment update; prepare/select
matching artifacts again before attempting such a workflow.

The original AutoSD kernel modules remain on disk and are not ABI-compatible
with Apollo. Devices requiring modules need matching Apollo modules packaged
into a future custom AutoSD image. Boot smoke does not qualify all AutoSD
services, container workloads, or every Apollo peripheral.

## Validation on 2026-09-22

### UKIBoot protocol follow-up

The current `--uki` path has these additional results (four CPUs, 4080 MiB):

| Image / slot | Boot and success service | Elapsed | Evidence |
| --- | --- | --- | --- |
| regular / A | PASS | 48.7 s | [result](../build/autosd/ukiboot-regular-second/result.json) |
| OSTree / A | PASS | 56.2 s | [result](../build/autosd/ukiboot-ostree-second/result.json) |
| regular / B | PASS | 41.2 s | [result](../build/autosd/ukiboot-regular-b/result.json) |

All three have `ukiboot_service=PASS`, valid bootctl magic/CRC, and
`successful_boot=1`, `tries_remaining=0` in the actual booted slot. Their UART
logs show the selected raw partition, addon-provided `_a`/`_b`, successful
service completion and SELinux Enforcing; neither the invalid-partition nor
missing-slot-suffix error occurs. The original nightlies retain their `X`
sentinel, demonstrating that only private run disks were changed.

The B-slot check used a cleanly shut-down guest to run:

```sh
ukibootctl prepare-switch 1
ukibootctl finalize-switch 1
ukibootctl dump
sync
poweroff
```

That console is retained in `build/autosd/ukiboot-switch-b/linux-uart.log`.
The next invocation selected its disk using
`--rootfs build/autosd/ukiboot-switch-b/rootfs.wic`; UKIBoot itself selected B.
Both slots use the same OS deployment in this test. This proves slot handoff
and success persistence, not an OTA update or exhausted-retry fallback test.

`./yocto_build.sh --keep-conf --bsp` completed 5,817 tasks after integration;
see `build/autosd/ukiboot-bsp-final-build.log`. The standalone `ukiboot` target
completed 1,668 tasks including package QA; see
`build/autosd/ukiboot-build-baseline-efi.log`. Existing forced-task taint
warnings were retained. `ukiboot-bitbake.env` records externalsrc selection.
The final loader SHA256 is
`8c1822d7ea68c75a51b397cc2a388a81c5d3b8fad9fcfea11a0e05ca242ede51`.

Host verification: 88 tests passed across `test_run_qemu_linux.py`,
`test_run_qbox_linux.py`, `test_prepare_autosd.py`, `test_autosd_uki.py`, and
`test_autosd_disk.py`. Direct BSP regression boot smoke remains PASS (8.3 s),
with its pre-existing unsupported-device selftest FAIL retained in
`build/autosd/ukiboot-direct-regression/result.json`.

U-Boot emits a non-fatal handle-cleanup warning during UKI addon loading;
it does not prevent EFI entry or the verified boot-control updates. Earlier
SVE-fault evidence is retained in `build/autosd/ukiboot-regular-first/`.

### Earlier direct-kernel and direct-EFI baselines

Nightly: `2869696176.466d2e78`, AutoSD 10 developer aarch64, from the
[official sample-image directory](https://autosd.sig.centos.org/AutoSD-10/nightly/sample-images/).
Documentation revision: `75cb479c89c8ee01350d03ca031a9b780158a99d`.
Composefs reference revision: `ec2573a0f68f548ae91f3e10acc990a08f9122dc`.

The final deployed Apollo kernel is `6.18.5-rt3-yocto-preempt-rt`, SHA256
`252fc4b8ed3ca258d4621c4ef374cd14e73e4e61bb568da942a5956757f05cf7`.
The preserved `build/autosd/Image.autosd-loop` matches the deployed `Image`.
The resolved configuration and hashes are in `build/autosd/kernel-loop.config`
and `build/autosd/kernel-loop.sha256`.

| Emulator / image | Boot smoke | Elapsed | Result |
| --- | --- | --- | --- |
| QEMU regular | PASS | 45.4 s | [JSON](../build/autosd/qemu-regular-validated/result.json) |
| QEMU OSTree | PASS | 51.1 s | [JSON](../build/autosd/qemu-ostree-validated/result.json) |
| QBox regular | PASS | 89.2 s | [JSON](../build/qbox-apollo-qvp/autosd-regular/result.json) |
| QBox OSTree | PASS | 101.8 s | [JSON](../build/qbox-apollo-qvp/autosd-ostree/result.json) |
| QEMU direct-EFI regular (historical) | PASS | 47.0 s | [JSON](../build/autosd/qemu-uki-regular-validated/result.json) |
| QEMU direct-EFI OSTree (historical) | PASS | 56.5 s | [JSON](../build/autosd/qemu-uki-ostree-validated/result.json) |

The historical direct-EFI runs execute the generated `nexios-bsp-initramfs-a.efi` kernel and
stub through standalone U-Boot, with the adaptation described above. Their
results record `boot_method=uki-efi` and `efi_boot_observed=true`; UART logs
show `EFI v2.11 by Das U-Boot`, `APOLLO_EFI_BOOTED`, and SELinux Enforcing.
Neither final run reports the earlier LZ4 `Decoding failed` warning. Kernel
SHA256 is unchanged from the deployed kernel listed above. Firmware SHA256 is
`b68c51c177940b0acad48cc8dd3446b4819766774f49ce979d1d4ad86ccdcd22`.
The initial failed firmware/UKI probes remain under `build/autosd/` as evidence.

The four direct-kernel runs use the default four CPUs, original AutoSD initramfs, prepared BLS
arguments and final deployed kernel; no final-run `--bootargs` override is
needed. UART logs alongside each result show AutoSD identity, CPU/disk checks
and SELinux **Enforcing**. Both OSTree runs show the active deployment
`c6da042842823bb2eec1f9dfc61306d13946440fb3110f78e16f72f0d2c708c2.0`,
the read-only composefs overlay root and `/dev/loop0` backing `.ostree.cfs`.
An additional interactive `bootc status` inspection is preserved in
`build/autosd/qemu-ostree-final/linux-uart.log`.

All four direct-kernel AutoSD runs retain a visible **FAIL** for
`ukiboot-set-success.service`. Direct AP boot does not provide the AutoSD
UKI boot-selection/handoff workflow. No service was masked or removed to
produce the boot PASS; the service result is outside that smoke claim.
The historical direct-EFI runs also retained this failure: the service journal explicitly reports
`No slot suffix in command line, assuming slot 0` and
`Bootctl partition is invalid`. Executing a UKI through U-Boot does not
initialize AutoSD's boot-control partition or implement its slot-selection
protocol. The current `--uki` path instead executes UKIBoot itself as described
above; it does not forge a slot-success result.

Build and host verification:

- Final `./yocto_build.sh --keep-conf --bsp`: 5,793 tasks succeeded;
  [build log](../build/autosd/bsp-build-loop-erofs.log).
- QBox `do_check`: 62 tests and 60 thread-local-disabled tests passed.
- Launcher/preparation tests: 45 passed with
  `python3 -m pytest -q tests/test_run_qemu_linux.py tests/test_run_qbox_linux.py tests/test_prepare_autosd.py`.
- UKI follow-up: 65 tests passed with the same command plus
  `tests/test_autosd_uki.py`. Standalone U-Boot build/deploy: 1,034 tasks
  succeeded. Effective source/build variables are retained in
  `build/autosd/u-boot-apollo-qemu.env`; compile logs confirm the active
  `hsoc-stack/components/primary_compute/u-boot` external source. No devtool
  workspace or changes to that source repository are required.
- Direct BSP regression after UKI integration: boot smoke PASS (7.7 s),
  pre-existing standalone BSP selftest FAIL retained;
  [result](../build/autosd/qemu-uki-direct-regression/result.json).
- Both publisher checksums and prepared-artifact cache hashes verified;
  [preparation](../build/autosd/prepare.log) and
  [cache verification](../build/autosd/prepare-cache.log).
- Original Yocto BSP on QEMU: AP boot smoke PASS (8.7 s), original BSP
  selftest FAIL for `dsu_cache`, `watchdog`, `remoteproc`, `rpmsg_bus`,
  `pfdi_misc`, and `dsu_pmu`, consistent with the standalone machine's
  unsupported devices. [Result](../build/autosd/qemu-bsp-regression/result.json).
- Original Yocto BSP on QBox: AP boot smoke PASS (14.4 s), original BSP
  selftest retains FAIL for `pfdi_misc` in the mock-domain profile.
  [Result](../build/qbox-apollo-qvp/autosd-bsp-regression/result.json).

Earlier failed attempts remain under `build/autosd/`: the original kernel
booted regular but failed OSTree preparation; enabling file-backed EROFS
then exposed the stacking limit described above. A regular-image run during
heavy concurrent compilation timed out waiting for the ESP device. The same
BLS arguments subsequently passed after build load subsided; run bounded
qualification after shared builds complete.
