# Apollo Linux on standalone QEMU

`run_qemu_linux.sh` boots the deployed Apollo Linux kernel and product
dm-verity initramfs with a private copy of `nexios-image-apollo-qvp.wic`.
`--bsp` selects the original `nexios-bsp-initramfs` cpio and boot/misc WIC;
the BSP root remains in RAM. Neither mode modifies the deployed images.

`--autosd build/autosd/regular.json` or `--autosd build/autosd/ostree.json`
selects a prepared AutoSD nightly disk and its original dracut initramfs,
using the deployed Apollo kernel. See [AutoSD preparation and qualification](autosd-apollo-linux.md).
Add `--uki PATH` to install an adapted unsigned Yocto UKI into both raw
AutoSD boot slots of a private disk copy. Dedicated `u-boot-apollo-qemu.bin`
firmware executes the Yocto-built UKIBoot loader from the ESP, which selects
the slot and maintains boot-control metadata. Kernel and EFI stub are preserved.
`./yocto_build.sh --keep-conf --bsp` deploys these prerequisites.

Build the host emulator with:

```bash
./yocto_build.sh --keep-conf qemu-apollo-native
./run_qemu_linux.sh --headless --exit-after-pass --timeout 180
./run_qemu_linux.sh --bsp --headless --exit-after-pass --timeout 180
```

The native recipe belongs to `meta-hsoc-bsp/recipes-devtools/qemu/` and uses
`EXTERNALSRC` pointing to `hsoc-stack/tools/qemu`. Its configure/Ninja build
disables libqemu and installs a dedicated `usr/libexec/qemu-apollo/` binary.
The deployment manifest is
`build/tmp_baremetal/deploy/qemu-apollo-native/qemu-apollo-native.json`;
it records the native executable and library paths used by the launcher.
This manifest is tied to this build tree. `--qemu PATH` selects another
binary and uses the caller's library environment.

The machine implementation is `hw/arm/apollo-qvp.c`. Its generated DT
describes the implemented Linux-facing Apollo hardware:

| Device | Address | Interrupt / contract |
| --- | --- | --- |
| Cortex-A720AE | 1–16 CPUs, default 4 | Native PSCI SMC; Generic Timer at 125 MHz |
| DRAM low | `0x80000000` | Up to 2032 MiB |
| DRAM high | `0x20000000000` | Remaining RAM, up to 2048 MiB |
| GICv3 distributor | `0x20800000` | 480 SPIs |
| GICv3 redistributors | `0x20880000 + cpu * 0x40000` | One region per CPU |
| PL011 UART | `0x1a400000` | SPI 52 |
| Virtio block | `0x30020000` | SPI 257; bus `virtio-mmio-bus.0` |
| Virtio network | `0x30060000` | SPI 261; bus `virtio-mmio-bus.1` |
| Virtio RNG | `0x30080000` | SPI 263; bus `virtio-mmio-bus.2` |
| PL031 RTC | `0x300d0000` | SPI 268 |

The default RAM size is 4080 MiB, preserving the Apollo gap below 4 GiB.
`--cpus`, `--memory`, `--kernel`, `--initrd`, `--rootfs` and `--bootargs`
override individual inputs. `--dtb` is an advanced override: it must match
this machine's devices; the full-system Apollo DT contains extra devices.

Interactive mode uses the same 70/30 tmux layout as the Linux-only QBox
launcher: UART above, interactive QEMU HMP monitor and host shell below. Mouse selection
and F12 session shutdown are enabled. Use `--session NAME` for a separate
session. The default user network forwards localhost TCP 2222 to guest SSH;
use `--netdev user,id=net0` to omit forwarding or specify another host port.

Outputs reside in `build/qemu-apollo-qvp/<timestamp>-<pid>/`. `launch.json`
records the exact command and source artifacts, `linux-uart.log` holds the
guest console, `qemu.log` holds emulator diagnostics, and `result.json`
separates boot smoke from the original BSP selftest result. Monitor input
is saved in `qemu-monitor.in` and its terminal transcript in `qemu-monitor.log`.
The monitor remains available through these files in headless mode, too.
`--headless` prints live UART output and saves the same logs without tmux.
`--timeout SECONDS` stops the emulator at the deadline in both modes (0:
unlimited); `--exit-after-pass` can finish earlier after smoke checks.
The bounded
smoke check verifies an interactive guest, the CPU count and a disk read.
Interactive sessions retain a `qemu.pid` for diagnostics; the supervisor
owns and terminates its child when the session closes.

RSE, SI CL0/CL1, SCMI, remoteproc/RPMsg, PFDI, DSU, watchdog, DMA, PCIe,
I2C, SPI and audio are not implemented by this Linux boot machine.
Direct-kernel modes do not execute firmware; `--uki` executes standalone
U-Boot and the EFI stub, not TF-A, OP-TEE, RSE or Safety Island firmware.
The generated DT omits unavailable devices;
the original BSP checks still report their failures and enter the
`nexios-bsp-failed#` shell. Boot smoke PASS is not full BSP qualification
or evidence of FVP timing, power/reset or safety fidelity.

Validated on 2026-09-21 with the deployed 6.18.5-rt3 Apollo kernel:

- Native recipe: all 579 tasks succeeded, including the machine registration check.
- Default four-CPU BSP: boot, CPU count and disk read PASS (7.6 seconds).
- Default four-CPU product: dm-verity root, login and disk read PASS (37.7 seconds).
- Sixteen-CPU BSP: all CPUs online; block/RNG/RTC reads and four network pings PASS.
- tmux: 70/30 split, equal lower panes, mouse selection and F12 child cleanup PASS.

Evidence is under `build/qemu-apollo-qvp/{bsp-first,yocto-first,bsp-tmux-16}/`.
The default BSP selftest remains FAIL for `dsu_cache`, `watchdog`,
`remoteproc`, `rpmsg_bus`, `pfdi_misc` and `dsu_pmu`. The sixteen-CPU run
additionally fails the original BSP's fixed four-CPU expectation.
