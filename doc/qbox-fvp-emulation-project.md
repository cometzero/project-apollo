# QBox FVP Emulation Project

Initialized: 2026-05-20

## Goal

Implement the Arm Zena CSS RD-Aspen FVP behavior in QBox using
SystemC/TLM/QEMU with a target of near-FVP functional equivalence for the active
`apollo-qvp` configuration, using FVP as the explicit reference. The project
should model hardware behavior as
closely as practical instead of accumulating compatibility-only stubs.

The current workspace baseline is `MACHINE = "apollo-qvp"`,
`RD_ASPEN_VARIANT = "cfg2"`, baremetal architecture, `nexios-image`, and
`PC_CPUS_COUNT_DEFAULT = "4"` as recorded in `build/conf/local.conf`.

## Non-Goals

- Do not claim 99% equivalence from Linux boot alone.
- Do not treat register-only stubs as final hardware models.
- Do not edit generated `build/` output as source.
- Do not change upstream/pinned Yocto layers unless explicitly requested.
- Do not implement from guesses when Arm documentation, generated device trees,
  FVP logs, QEMU models, or open-source SystemC models can be inspected.

## Reference Priority

For every hardware IP, collect evidence in this order:

1. Local Arm Zena CSS sources and documentation:
   - `arm-zena-css/documentation/overview.rst`
   - `arm-zena-css/documentation/design/components.rst`
   - `arm-zena-css/documentation/design/*.rst`
   - `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf`
   - `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/*.inc`
   - generated DTS/DTB and FVP boot logs under `build/`
2. Official Arm documentation and TRMs:
   - Arm Zena CSS documentation site
   - IP-specific technical reference manuals and programmer guides
   - record document version, URL, and access date in implementation notes
3. Existing open-source implementations:
   - SystemC/TLM models on GitHub or other public repositories
   - QEMU upstream or local `hsoc-stack/tools/qemu` device models
   - qbox components already present under `hsoc-stack/tools/qbox`
4. Runtime behavior:
   - Arm FVP console logs
   - Linux driver probe output
   - interrupt counters, remoteproc/RPMsg status, systemd state, and QBox logs

## Fidelity Policy

Use these labels for each block:

| Status | Meaning |
| --- | --- |
| `fvp-equivalent` | Register behavior, interrupts, memory map, boot behavior, and driver evidence match the FVP target for the supported use case. |
| `functional-model` | Real SystemC/TLM or libqemu-backed behavior exists, but some documented FVP behavior is not modeled yet. |
| `static-map-only` | Address/IRQ/device-tree compatibility exists, but meaningful device behavior is absent. |
| `temporary-stub` | A stub is used only to unblock integration. Missing behavior and replacement plan must be documented. |
| `not-modeled` | The block is known from FVP/Zena evidence but absent from QBox. |

`temporary-stub` is technical debt. Prefer replacement with an existing QEMU
model, upstream SystemC model, or local SystemC/TLM model based on the TRM.

## Current Implemented Surface

The Apollo full-system machine now loads a declarative Lua contract for
topology, address ranges, transactions, signals, boot/control ownership, and
software ABI before constructing the platform. The root fabric is named
`system_router`; AP, SMD, RSE, SI CL0, and the FVP CFG2 SI CL1 extension have
separate runtime address-view routers. The SMD high-nibble uses an explicit NCI
decode, AP/SI/SMDEXP use the RSE-programmed ATU data paths, and HIPC/SCMI use
narrow static windows. The three A3 broad system bridges are removed. A
repository validator exports nine JSON evidence files and checks view widths,
overlap/backing rules, references, routes, reset default-deny, and the absence
of broad passthrough. Full-system AP CPU default is four, matching active
Yocto configuration. Local full-system rootfs patching also writes the resolved
CPU count as `maxcpus=`, so guest topology cannot silently retain the separate
16-core direct-boot experiment value.

The structural migration phase is now `A4_policy_routing`; compatibility debt
is empty. Complete NI-710AE APU permissions, requester/StreamID propagation,
debug/direct/DMI policy, negative guest-fault evidence, and complete ABI error
paths remain fidelity work rather than boot-compatibility bridges.

The QBox `addrtr` component fixes descending DMI address translation and has a
regression for source `0x1000` mapped to downstream `0x100`. QBox CPU lifecycle
also keeps reset-held CPUs out of the SystemC quantum-keeper suspend set and
completes reset release on the target vCPU. The reset regression passed 50
consecutive runs; local-source full-system boot/coverage passed 5/5 and Yocto
`nexios-image` boot/coverage passed 3/3 through RSE, live SI CL0/CL1, TF-A,
OP-TEE, U-Boot, and Linux login. See
`doc/apollo-qvp-architecture-debt-validation-2026-07-16.md` for exact commands
and evidence paths.

The AP/SI non-secure MHU shared SRAM is address-visible in the AP view but
owned and initialized by SMD/SI0 before AP release. Its machine contract now
uses `preserve_on_ap_reset`, and AP reset fan-out does not clear that backing.
The post-review acceptance boot reaches Linux login and probes SCMI v2.0 with
the same vendor and firmware marker as the recorded FVP boot, without the
earlier `shmem_tx_prepare` warning and secondary SCMI response timeout.
SI0 secure transport initialization also preserves a valid request that AP or
SI CL1 posted before the completer started. This closes the trace-sensitive
first-PFDI-request race without changing the global quantum. SCP module tests
passed 77/77; trace-off local and rebuilt Yocto full-system runs each passed
3/3 with PFDI ready, four AP CPUs, SCMI v2.0, Linux login, and 49/49 coverage.

The current QBox RD-Aspen primary-compute platform has file-backed build and
runtime helpers:

- `./local_build.sh qbox`
- `scripts/test/validate_qbox_fvp_rd_aspen_map.py`
- `scripts/run/run_qbox_fvp_rd_aspen_rse.py`
- `scripts/test/audit_qbox_fvp_rd_aspen_coverage.py`

The latest local coverage evidence reports 19 tracked primary-compute blocks
passing static or runtime checks, including CPU/PSCI, DRAM, timers, GICv3,
ITS, PL011, SBSA watchdog, PL031 RTC, virtio-mmio block/net/rng, SRAM/SCMI
shared memory, SI remoteproc reserved memory, armv7 memory-mapped timer, DSU
PMU, RAS FFH, SMMUv3, MHUv3 SCMI transport, and SI remoteproc/RPMsg.

An RSE-oriented skeleton now exists at
`hsoc-stack/tools/qbox-platform/platforms/fvp-rd-aspen-rse/conf.lua` with the
runner `scripts/run/run_qbox_fvp_rd_aspen_rse.py`. It uses the existing QBox
`RemoteCPU` Cortex-M55 wrapper so the CPU-local NVIC/SCS window remains inside
the M-profile CPU process, and it records file-backed per-console logs plus
`result.json`. Limited CC3XX, DTCM/ITCM alias, DMA350, RSE system-control,
ATU, LCM/OTP, KMU, Integrity Checker, host PPU, RSE Strata boot-flash,
AP handoff host windows, and RSE-SI MHUv3/SCMI SystemC/TLM models now let the
generated RSE ROM pass the earlier `0x501541c4` CC3XX Data Abort, complete the
observed BL1_1 DTCM/ITCM erase/fill writes through DMA350, and progress
through RSE system-control, ATU register programming and translation, LCM/OTP
reads, KMU random-delay reads, BL1_2 decrypt/validate, BL2 entry, PSA Crypto
initialization, SI CL0 load, SI CL0 key-hash validation, SI CL0 post-load,
RSE-SCP SCMI init, AP BL2 load, AP ATU programming, RSE runtime image load, AP
power-domain SCMI success, RSE runtime chainload, modeled AP0 reset release,
and AP BL2 secure-console output. The LCM/OTP model exposes the generated
`rse-otp-image.img` at the TF-M-visible LCM OTP window, uses the active TCI
mode value, writes OTP updates back to per-run copied OTP images, and locks
later OTP writes after secure-provisioning completion. The RSE TCM model now
defaults CPU0 DTCM aliases to the same
backing store after GDB proved the split alias path made CC3XX hash DMA read
stale `0xa4093822` TRAM-fill data from `0x34003820`. The latest focused
regression fixes shared-memory fd reporting, fd-backed QEMU RAM aliases, and
QEMU DMI granted-access preservation: the byte-store, shared-memory byte-store,
shared-memory external-write, and remote Cortex-M55 DMI byte-store tests now
pass. RSE-local CC3XX/KMU, RSE-local boot flash, and RSE ITCM/DTCM/VM DMI now
default on for short-timeout iteration. The current AP-RSE bridge path maps
AP secure mailbox requests through `ap_s_to_rse` and responses through
`rse_to_ap_s`; RSE MHU0/MHU2 receiver interrupts now route to TF-M IRQs
41/45, and the SI CL0-to-RSE receiver routes to IRQ 139. A 2026-05-24 GDB
sample proves AP writes reach RSE MHU2, TF-M clears the receiver channels,
and RSE MHU2 replies back to the AP mailbox. Additional GDB snapshots now
cover QBox host threads, TF-M/RSE, SCP-Firmware symbols, AP TF-A BL31 PFDI,
AP OP-TEE initialization, and the AP/Linux GDB target. Current runtime
evidence records SI CL1 and SI CL0 RAM-load/key-hash/post-load success, SI ATU
regions 0..16, `RT_0`, `SCMI Comms subscribed to power state notifications`,
RSE measured-boot markers through `BL_33`, AP TF-A BL31 runtime services,
Linux login, and file-backed post-login driver/module probes. Short GDB
samples remain intentionally bounded and may stop before Linux, but the AP
BL31 RAS trap is no longer the active blocker. Targeted TF-M branch traces now
prove static-boundary
setup and `tfm_core_init()` both return successfully after the MPC reset-value
offset fix and DMA350 ID-register fix; the remaining TF-M blocker is a later
secure partition panic. The current GDB split attributes the first panic to
ITS when boot-flash DMI is enabled, but proves the storage-safe path with
`QBOX_RDASPEN_BOOT_FLASH_DMI=false` progresses past ITS and now fails in TF-M
Protected Storage: `ps_system_wipe_all()` succeeds, while
`ps_system_prepare()` returns `PSA_ERROR_GENERIC_ERROR`. That blocker is
superseded by the AP-RSE bridge/IRQ and storage-safe marker runs for the
current default path.

The 2026-05-25 GDB split shows the current pre-Linux AP sample is in the
expected U-Boot authenticated-variable provisioning path, not an unknown Linux
entry failure. AP CPU0 resolves to the SE-Proxy secure partition
`mhu_v3_x_doorbell_read()` while `secure_storage_ipc_set()` waits for an RSE
Protected Storage response, and the paired RSE/TF-M sample is in
`CMU_MHU2_Receiver_Handler()` receiving the matching AP secure-service
transaction. The debug helper now includes TS SP symbol/source discovery and
per-run SE-Proxy/SMM Gateway load-base handling for this class of issue. A
later bounded run proves this was not a persistent secure-storage hang:
`build/qbox-fvp-rd-aspen/rse-secure-storage-bounded-20260525-v1/` reaches
Linux login and completes the post-login driver probe with `passed=true`.
The full V004-style run
`build/qbox-fvp-rd-aspen/rse-v004-full-postlogin-20260525-v1/` rebuilds the
required QBox targets, boots the RSE-oriented path to Linux, records all RSE
boot/SCP handoff/measured-boot/Linux marker groups true, and completes the
same post-login driver probe with blocker `none`.
The runner also has a bounded secure-service post-login probe. Current evidence
`build/qbox-fvp-rd-aspen/rse-t065-secure-service-probe-20260525-v1/` proves the
probe path and records the current gap: PSA IAT/ITS/PS test binaries are
present but timeout, while `ts-service-test` and `uefi-test` are absent from
the active rootfs and secure-console logs still report SE-Proxy/SMM Gateway
errors.
The file-backed V007 FVP comparison
`build/qbox-fvp-rd-aspen/rse-v007-fvp-qbox-compare-20260525-v1/comparison.json`
now passes against
`build/fvp-boot-logs/rse-v007-fvp-verbose-20260525-v1/`, with no FVP-observed
RSE boot, RSE/SCP handoff, measured-boot, or Linux markers missing in QBox.
The direct primary-compute path also remains available through
`build/qbox-fvp-rd-aspen/direct-v008-primary-compute-20260525-v1/`.
The latest RSE short-timeout diagnostics classify pre-AP PC traces through the
TF-M BL1_1 map as shared CC3XX/CFI work instead of generic platform timeouts.
The QBox CC3XX model now uses a bounded 1024-byte DMA processing chunk for
AES, hash, and CMAC DMA paths; a larger 4096-byte experiment was rejected
because it caused SI CL1 image validation failure. This does not close the
Protected Storage PS403 acceptance gap, whose best QBox evidence still stops
after UID 21 cleanup, but it keeps the CC3XX path closer to a useful hardware
DMA model while preserving the firmware-visible register protocol.
The FWU preflight helper
`build/qbox-fvp-rd-aspen/fwu-inspect-20260525-v2/` now records the static CFG2
Secure FWU baseline: RSE/AP flash raw sizes match the generated media, primary
slots are populated while secondary slots are zeroed, AP metadata is version 2
with active bank 0 and five images, and VirtIO block 1 contains `fw.cap`
matching the generated capsule image. This is only preflight evidence; capsule
application, bank-1 boot markers, and cross-reboot writeback persistence remain
open.
The coverage audit now records RSE fidelity labels from RSE-oriented
`result.json`; the current V004 audit has no missing labels and explicitly
keeps `mhuv3`, `rse_sacfg`, and `rse_nsacfg` as fidelity debt.
RSE FVP defaults for `VMADDRWIDTH`, reset syndrome, CPUWAIT, and DMA boot
enable are now exposed through Lua/CCI parameters and covered by
`rse_sysctrl-tests`; the short T024 smoke records `VMADDRWIDTH=18` as a
`0x40000` VM window.
Boot-media unit coverage now directly tests the read-only ROM load path,
RSE Strata flash loader path, LCM OTP image load, and provisioning bundle
offset load. Focused OTP/NVM coverage now also tests LCM OTP file writeback
and lock-after-provision behavior; a bounded runtime shows the copied OTP image
changes while the deploy OTP image remains untouched.
The Strata flash model now has optional per-run `backing_file` write-through
for program/erase mutations, and the RSE runner enables it only for copied
writable RSE/AP flash images. This is the T076 persistence plumbing
prerequisite; full Secure FWU remains open until the runtime proves RSE image
1, TF-A `FIP_B`, U-Boot `Trial State`, and persisted metadata in one bounded
run. The optional RSE ATU translated-DMI path also now rejects partial
downstream DMI grants unless the clipped upstream range covers the entire TLM
request span, preventing short downstream windows from becoming over-broad
host-window aliases. It also rejects negative add-value mappings that would
underflow physical address zero. The first short post-fix FWU probe uses a
180-second cap and times out
before Linux login, so it sends no capsule commands and leaves the inspected
FWU banks in their initial active-bank-0 state. A matching GDB sample shows
RSE BL2 still reading/copying the SI CL0 image from Strata flash while AP CPU0
is parked at TF-A BL2 entry, narrowing the next short-cap blocker to first-boot
RSE flash-read/copy latency before any Linux/FWU capsule stage starts.
The latest all-target short GDB snapshot
`build/qbox-fvp-rd-aspen/gdb-fast-linux-current-20260525-v1/` confirms the
generated debug environment remains usable for QBox host, TF-M/RSE, AP target
attachment, SCP-Firmware source/symbol inspection, and SI CL1 symbols. In that
bounded run Linux has not started: RSE TF-M runtime is halted below
`tfm_spm_partition_psa_panic()`, AP CPU0 is in TF-A BL2
`mhu_v3_x_doorbell_read()`, and SCP-Firmware still has no live CPU GDB target
because the active path uses the SystemC/TLM SCP service model.
The follow-up range-limited DMI snapshot
`build/qbox-fvp-rd-aspen/gdb-ranged-dmi-writeback-20260525-v1/` avoids the
full-flash DMI side-effect issue by exposing only primary image slots through
read-only DMI (`0x7000:0x260000` for RSE flash and `0x7000:0x240000` for AP
flash). That bounded run reaches AP BL31, OP-TEE, U-Boot, and Trusted
Services within the short GDB cap. RSE/TF-M is sampled in
`Driver_FLASH0_ProgramData()` below ITS flash filesystem writes, while AP
SE-Proxy is waiting for the RSE secure-storage response over MHUv3; this
shows storage writes are back on the SystemC CFI path rather than hidden by
DMI.
`build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1/`
captures the reusable all-target GDB view after Linux is running: TF-M/RSE is
in `psa_wait_thread_fn_call()`, AP/Linux CPU0 is in
`d_alloc_parallel+336`, AP CPUs 1-3 are in `cpu_do_idle()`, QBox host
SystemC/QEMU threads are sampled under host GDB, and SCP-Firmware remains
symbol/source-only because the active path uses the SCP service model. The
secure console still records an SE-Proxy panic and SMM Gateway busy/PK-read
errors, so secure-service fidelity remains open even though it no longer
blocks AP Linux boot.

Important caveat: coverage success means the tracked Linux-visible surface is
covered by current checks. It does not prove full FVP equivalence for reset
behavior, firmware side effects, safety diagnostics, error injection, power
management, or all IP registers.

## Initial IP Matrix

| IP / Block | Current QBox Direction | Fidelity Target | Primary Evidence |
| --- | --- | --- | --- |
| Cortex-A720AE Primary Compute | QEMU/libqemu CPU model via QBox | Functional AP boot, PSCI, timers, SMP, affinity, exception routing | `.config.yaml`, FVP DTS, `arm-zena-css/documentation/overview.rst`, QBox runtime logs |
| DSU-120AE / DSU PMU | QBox-visible PMU evidence exists | Model enough PMU and topology behavior for Linux/FVP parity | `arm-zena-css/documentation/design/components.rst`, Linux probe logs |
| GIC-720AE / GICv3 / ITS | libqemu-backed GICv3/ITS | Match FVP distributor, redistributors, ITS, IRQ numbering, multi-view constraints where used | FVP DTS, machine config, Linux `/proc/interrupts` |
| SMMUv3 | libqemu-backed `arm_smmuv3` | Replace previous stub; maintain PCI bus, memory links, IRQs, Linux driver behavior | QEMU SMMUv3 model, FVP DTS, runtime driver probe |
| PL011 UART | QBox UART + backend | Console compatibility, interrupt behavior, backend behavior, stop semantics | FVP config, QBox backend docs, Linux console logs |
| SBSA watchdog | QEMU model | Linux watchdog probe and reset behavior where practical | FVP DTS, Linux probe logs, Arm SBSA watchdog docs |
| PL031 RTC | QEMU model | Linux RTC behavior and IRQ compatibility | FVP DTS, Linux probe logs, Arm PL031 docs |
| Virtio block/net/rng | QEMU virtio-mmio models | Match FVP device count, address/IRQ, and Linux driver behavior | FVP config, generated image artifacts, Linux probe logs |
| MHUv3 | QBox compatibility components with reusable PBX/MBX frame model and SCMI/RPMsg service hooks | Move from reusable register-frame behavior toward full TRM-based channel/doorbell and service semantics | Zena HIPC/SCMI docs, Arm MHUv3 docs, Linux/Zephyr RPMsg evidence |
| Safety Island CL0/CL1 | Partial AP-visible remoteproc/RPMsg surface | Model boot, shared memory, MHU, Zephyr/OpenAMP interactions, and CL1 runtime behavior | Zena Safety Island docs, Zephyr DTS, remoteproc logs |
| RSE / System Management Block | Skeleton starts RSE ROM through RemoteCPU; limited CC3XX, DTCM/ITCM alias, DMA350 fill and ID registers, RSE system-control, ATU translation/DMI, LCM/OTP, KMU, Integrity Checker, RSE Strata boot flash, AP/SI host windows, host PPU, AP-RSE/RSE-SI/AP-SI MHUv3 frames, and RSE-SI/AP-SI SCMI service remove the previous `0x501541c4` Data Abort, BL1_1 DMA erase/fill timeout, `0x58021100` reset-syndrome fault, first ATU programming gap, untyped KMU/Integrity Checker placeholders, BL2 decrypt/validate gaps, first BL2 host-window gap, PPU polling loop, SI CL0 AES-KW unwrap failure, host ATU placeholder gap, RSE-SI MHU init failure, AP reset-release blocker, AP-RSE MHU channel-count failure, AP SDS warning, AP image-authentication blockers, AP timer abort, AP-SI SCMI MHU abort, the RSE VM DMI encrypted-IV mismatch, TF-M `tfm_core_init()` static-boundary/DMA init failures, the ITS/PS storage blockers in the storage-safe path, and the TF-M NS mailbox local-MHU fault. Current defaults enable RSE-local KMU/CC3XX, RSE-local boot flash, and RSE ITCM/DTCM/VM DMI. The AP-RSE secure mailbox now bridges AP->RSE and RSE->AP doorbells, routes RSE MHU receiver IRQs to TF-M-visible IRQ numbers, reaches the FVP RSE runtime SCMI subscription marker plus measured-boot markers through `BL_33`, and service-models SI CL1 RPMsg name service far enough for Linux to create `ethsi1`. | Keep boot-flash DMI disabled for TF-M storage debug, replace the service-modeled SI CL1 RPMsg endpoint with a real SI CL1 CPU/Zephyr peer, add secure-service userspace tests, and preserve host SCR/PPU/MHU/shared-memory semantics before any ATU/host-SRAM co-location. | Zena RSE docs, TF-M artifacts, FVP logs, `doc/spec/rse-qbox/evidence.md` |
| FMU / SSU / SBISTC / SMCF / RAS | Some AP-visible RAS evidence; other safety IP mostly not modeled | Implement documented register and interrupt behavior needed for diagnostics and tests | `arm-zena-css/documentation/design/fmu.rst`, `ssu.rst`, `sbistc.rst`, `smcf.rst`, `ras.rst` |
| PFDI | Live SI CL1/SI0 messaging, per-CPU ready marker, and secure pending-mailbox startup preservation are covered by local/Yocto runtime | Add malformed, peer-offline, timeout/recovery and fault-injection behavior | Zena PFDI docs, Linux/Zephyr/SCP code, runtime logs |
| Power/performance control | AP-visible behavior only | Model SCMI-visible power/performance contracts before low-level PPU fidelity | Zena power/performance docs, SCMI logs |

## Implementation Workflow

For each IP:

1. Create an evidence note:
   - local Zena docs and line references
   - official Arm doc/TRM URL and version
   - matching FVP DTS nodes, FVP parameters, boot log lines
   - existing QEMU/SystemC implementation candidates and license notes
2. Define the compatibility target:
   - register ranges and reset values
   - IRQ lines and polarity/trigger semantics
   - DMA/TLM transactions and DMI behavior
   - CCI/Lua parameters
   - Linux, firmware, or Zephyr observable behavior
3. Implement the narrowest useful model:
   - prefer existing QBox/libqemu patterns
   - preserve C++14 and SystemC/TLM conventions
   - keep Lua platform object names and bindings stable when possible
4. Validate in layers:
   - compile target
   - unit/component test or focused runtime test
   - static map validation
   - QBox boot and `--post-login-probe`
   - coverage audit
   - FVP-vs-QBox log comparison where relevant
5. Update status:
   - QBox platform README or implementation note
   - this document's IP matrix
   - generated verification report under `build/qbox-fvp-rd-aspen/`

## Validation Commands

Use these before claiming progress:

```bash
python3 -m py_compile scripts/run/run_qbox_apollo_fvp_full.py scripts/run/run_qbox_fvp_rd_aspen_rse.py scripts/test/validate_qbox_apollo_topology.py
git -C hsoc-stack/tools/qbox-platform diff --check
git -C hsoc-stack/tools/qbox diff --check
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/validate_qbox_apollo_topology.py
python3 scripts/test/audit_qbox_core_boundary.py
QBOX_PLATFORM_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR:-build/local-apollo-qvp/work/qbox-platform}"
cmake --build "${QBOX_PLATFORM_BUILD_DIR}" --target <target> --parallel 8
cmake --build "${QBOX_PLATFORM_BUILD_DIR}" --target platforms-vp --parallel 8
./local_build.sh qbox --qbox-unit-tests --no-package --jobs 8
make -C hsoc-stack/components/system_mgmt/scp-firmware -f Makefile.cmake \
  mod_test BUILD_PATH=<repo>/build/tests/scp-firmware-unit
python3 scripts/run/run_qbox_apollo_fvp_full.py --si-mode live-cl0-cl1 --timeout 600 --out-dir build/qbox-apollo-qvp/<run-id>
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py --result-json build/qbox-apollo-qvp/<run-id>/result.json --output build/qbox-apollo-qvp/<run-id>/full-coverage-audit.json
```

For Arm FVP comparison, use non-interactive, file-backed FVP logging rather
than relying on tmux screen state.

## Research Rules

- Browse or otherwise verify official Arm docs before citing specific TRM
  claims not already present in this checkout.
- Prefer primary sources: Arm docs, local Zena docs, QEMU source, QBox source,
  Linux/Zephyr source, and directly captured logs.
- When using GitHub/SystemC implementations, record repository URL, commit,
  license, modeled IP version, and deltas from the target Arm IP.
- Do not copy incompatible licensed code into QBox.

## Near-Term Backlog

1. Implement the complete NI-710AE APU permission/lock model on top of the A4
   ATU/static-window structure and add secure/domain deny evidence.
2. Carry CPU and GPEX requester/domain/StreamID through QEMU/TLM, SMMU, and APU;
   add denied-access and guest-fault evidence for regular/debug/DMI paths.
3. Convert remaining compatibility stubs into tracked fidelity debt with owner,
   missing behavior, and replacement path.
4. Extend signal and ABI coverage to IRQ/reset/power/fault injection and
   SCMI/PFDI/HIPC/FF-A malformed, denied, peer-offline, and timeout paths.
5. Add an IP evidence ledger for MHUv3, RAS FFH, DSU PMU, PFDI, and Safety
   Island CL1.
6. Add automated same-artifact FVP-vs-QBox comparison for boot, maps, access
   policy, interrupt routes, device probes, remoteproc/RPMsg, and failed
   services.
