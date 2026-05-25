# QBox RD-Aspen GDB Debug

This note records the repo-local GDB setup for inspecting the QBox
RD-Aspen RSE boot path with short, log-backed runs.

## Helper

Generate a debug bundle:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-debug-YYYYMMDD-vN
```

Generate the bundle and run short non-interactive probes:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-debug-YYYYMMDD-vN \
  --launch \
  --host-sample
```

When the target is expected to print `[ERR]` and then spin in a firmware error
loop, add `--ignore-fail-patterns`. The runner still records matched failure
patterns in `result.json`, but it keeps QBox alive until the GDB probes and
short timeout finish.
The helper defaults are intentionally short: `--runner-timeout 45`,
`--port-timeout 8`, `--gdb-timeout 8`, and `--sample-delay 8`. For the current
post-decrypt RSE progress point, use `--sample-only --sample-delay 28`.
For U-Boot or secure-service progress points that are visible in a UART log,
prefer marker-gated sampling instead of a long fixed delay:
`--sample-marker '<text>' --sample-delay <cap>`. Add
`--sample-marker-post-delay <seconds>` when the useful GDB snapshot is just
after the marker rather than exactly at the marker.

The helper launch path also defaults to the current short RSE debug
environment: AP CPU GDB enabled, RSE-local CC3XX/KMU and boot flash enabled,
and RSE ITCM/DTCM/VM DMI enabled. ATU, AP boot-flash, and host-memory DMI stay
disabled unless the caller overrides those environment variables.

For Linux login, post-login driver probe, or first-boot secure-storage
writeback debugging, add
`--copy-writable-flash --post-login-probe --keep-running-after-pass`. This
uses the same per-run writable flash copies as the normal runtime helper,
feeds the primary UART post-login probe, and keeps the platform attachable
until the bounded GDB probe finishes.

For TF-M storage and secure-partition debugging, either keep
`QBOX_RDASPEN_BOOT_FLASH_DMI=false` for strict CFI command visibility or use
range-limited boot-flash DMI for bounded progress probes. Full-device
boot-flash DMI can bypass or obscure Strata CFI command writes. The current
bounded fast path exposes only immutable image slots through DMI:
`QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES=0x7000:0x260000` and
`QBOX_RDASPEN_AP_FLASH_DMI_RANGES=0x7000:0x240000`. Storage and FWU sectors
then continue through the SystemC Strata flash model.

The helper writes:

- `README.md`: exact launch and attach commands.
- `debug-env.json`: ports, symbol paths, generated scripts, probe result.
- `progress-report.md`: short target/probe/source-map summary.
- `gdb/*.gdb`: QBox host, TF-M/RSE, TF-M runtime partition traces, AP TF-A,
  AP OP-TEE, AP U-Boot, Linux/AP, SCP-Firmware, and SI CL1 Zephyr symbol
  scripts.
- `gdb/qbox-host-sample.gdb`: QBox host foreground run script. The helper
  sends `SIGINT` to the child GDB after `--host-sample-seconds` and records
  `info threads` plus `thread apply all bt`.
- `probes/*.txt`: short GDB register/backtrace snapshots when `--launch` is
  used.

The generated GDB scripts also add Yocto source path mappings for TF-M, AP
TF-A, AP OP-TEE, AP U-Boot, SCP-Firmware, Linux, and SI CL1 Zephyr so
`/usr/src/debug/...` paths resolve to the local
`build/tmp_baremetal/work/.../git` source trees when available.
The TF-M/RSE bundle includes `gdb/tfm-rse-current.gdb`, which loads BL1_1 as
the main symbol file and adds BL1_2/BL2 symbols at their ELF `.text`
addresses. Use this first for current-PC/backtrace inspection because the live
RSE CPU can be executing code from more than one TF-M image.

## 2026-05-25 Range-Limited All-Target Probe

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-ranged-dmi-efi-ps-trace-20260525-v1/`

Use this when the goal is to see where the run is now without waiting for a
full Linux boot:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES='0x7000:0x260000' \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_AP_FLASH_DMI_RANGES='0x7000:0x240000' \
QBOX_RDASPEN_MHU_TRACE=true \
QBOX_RDASPEN_MHU_TRACE_LIMIT=6000 \
timeout 280s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-ranged-dmi-efi-ps-trace-YYYYMMDD-vN \
  --launch \
  --sample-only \
  --sample-marker 'EFI: MM partition ID' \
  --sample-marker-post-delay 25 \
  --sample-delay 170 \
  --runner-timeout 210 \
  --trace-timeout 80 \
  --gdb-timeout 6 \
  --port-timeout 8 \
  --host-sample \
  --host-sample-seconds 2 \
  --ignore-fail-patterns \
  --copy-writable-flash \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result from the 2026-05-25 run:

- RSE/TF-M GDB port `12700` and AP/Linux GDB port `12701` both opened.
- QBox host GDB captured a `platforms-vp` thread/backtrace sample.
- TF-M/RSE was executing ITS/PS flash filesystem writes through
  `Driver_FLASH0_ProgramData()` and `nor_send_cmd_byte()`.
- AP CPU0 was inside Trusted Services SE-Proxy
  `secure_storage_ipc_set()` -> `__psa_call(type=1001)` ->
  `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read()`.
- The Linux GDB script attached to the AP target, but the sampled PC was still
  in the secure-service address range. Linux had not started at this marker.
- SCP-Firmware symbols/source loaded for `rdaspen-si0-bl2.elf`; live SCP
  stepping is still unavailable while the platform uses `scp-strategy` service
  model.

## 2026-05-25 EFI Marker Current Recheck

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-user-efi-current-20260525-v1/`

Command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES='0x7000:0x260000' \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_AP_FLASH_DMI_RANGES='0x7000:0x240000' \
QBOX_RDASPEN_MHU_TRACE=true \
QBOX_RDASPEN_MHU_TRACE_LIMIT=6000 \
timeout 280s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-user-efi-current-20260525-v1 \
  --launch \
  --sample-only \
  --sample-marker 'EFI: MM partition ID' \
  --sample-marker-post-delay 15 \
  --sample-delay 170 \
  --runner-timeout 210 \
  --trace-timeout 80 \
  --gdb-timeout 6 \
  --port-timeout 8 \
  --host-sample \
  --host-sample-seconds 2 \
  --ignore-fail-patterns \
  --copy-writable-flash \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- The `EFI: MM partition ID` primary-console marker was reached after
  101.526 seconds.
- RSE/TF-M GDB port `12340` and AP/Linux GDB port `12341` opened; all target
  probes returned 0.
- QBox host GDB captured a foreground `platforms-vp` SystemC/QEMU
  thread/backtrace sample. Late `gdb -p` attach to an already running
  `platforms-vp` process remains blocked by the current ptrace/TTY policy.
- AP CPU0 was in Trusted Services SE-Proxy
  `secure_storage_ipc_remove()` -> `__psa_call(type=1004)` ->
  `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read()`. CPU1-CPU3 were
  halted.
- RSE/TF-M was in `tfm_its_remove()` below ITS flash filesystem
  delete/compact, programming the SystemC Strata flash model through
  `Driver_FLASH0_ProgramData()` and `nor_send_cmd_byte()`.
- The Linux script attached to the AP target, but the sampled PC was still in
  secure-service code. Linux had not started at this marker.
- SCP-Firmware symbols/source loaded for `rdaspen-si0-bl2.elf`; live SCP
  stepping is still unavailable while the active platform uses the SCP
  service model.

## 2026-05-25 All-Layer Short Probes

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-all-layer-short-20260525-v2/`
- `build/qbox-fvp-rd-aspen/gdb-current-all-targets-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-all-layer-short-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-all-layer-60s-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-short-100s-targets-20260525-v1/`

A 65-second all-layer recheck used short GDB timeouts and storage-safe boot
flash settings:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
timeout 120s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --ignore-fail-patterns \
  --runner-timeout 80 \
  --port-timeout 5 \
  --gdb-timeout 5 \
  --sample-delay 65 \
  --host-sample \
  --host-sample-seconds 2 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-all-layer-short-20260525-v2 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- RSE/TF-M GDB port `12340` and AP/Linux GDB port `12341` both opened.
- QBox host GDB captured a foreground `platforms-vp` thread/backtrace sample.
- TF-M/RSE was in TF-M BL2 image validation:
  `cc3xx_lowlevel_pka_and()` below `bootutil_img_validate()` and
  `boot_load_and_validate_images()`.
- The RSE UART had reached AP BL2 post-load, RSE-to-SCP SCMI power-on, and
  TF-M runtime image loading/validation markers.
- AP CPU0 was still at TF-A BL2 entry `0x82000`; Linux had not started in
  this short sample.
- SCP-Firmware and SI CL1 Zephyr symbol/source scripts loaded successfully.
- SCP remains symbol-only in the current `service-model` path; no live SCP CPU
  GDB target is instantiated.

A current 35-second storage-fidelity sample used AP CPUs, ATU DMI, host-memory
DMI, and disabled boot-flash DMI:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
timeout 140s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-delay 35 \
  --runner-timeout 80 \
  --port-timeout 8 \
  --gdb-timeout 6 \
  --host-sample \
  --host-sample-seconds 2 \
  --ignore-fail-patterns \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-all-targets-20260525-v1 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- RSE/TF-M GDB port `12340` and AP/Linux GDB port `12341` both opened.
- QBox host GDB sampling captured a thread/backtrace snapshot in
  `host-gdb-run/qbox-platform.log`.
- TF-M/RSE was in BL2 `clear_safety_island_memory()` via `memset()` for the
  SI CL0 SRAM window at `0x753a6000`.
- AP CPU0 was still at TF-A BL2 entry `0x82000`; Linux had not started in
  this short sample.
- SCP-Firmware and SI CL1 Zephyr symbol/source scripts loaded successfully.
- SCP remains symbol-only in the current `service-model` path; no live SCP CPU
  GDB target is instantiated.

The 20-second all-layer sample used fast AP/host-memory DMI and captured QBox
host, TF-M/RSE, AP firmware/Linux, SCP-Firmware symbols, and SI CL1 Zephyr
symbols in one bounded helper run:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-all-layer-short-20260525-v1 \
  --launch \
  --sample-only \
  --sample-delay 20 \
  --runner-timeout 40 \
  --port-timeout 8 \
  --gdb-timeout 4 \
  --host-sample \
  --host-sample-seconds 2 \
  --copy-writable-flash \
  --post-login-probe \
  --keep-running-after-pass \
  --ignore-fail-patterns
```

Result:

- QBox host GDB captured a thread/backtrace sample through
  `gdb/qbox-host-sample.gdb`.
- TF-M/RSE was still in BL1_2 signature verification through the CC3XX hash
  path.
- AP CPU0 was still at TF-A BL2 entry PC `0x82000`; Linux had not started.
- SCP-Firmware and SI CL1 Zephyr symbol/source scripts loaded successfully.
- SCP remains symbol-only in the current `service-model` path; no live SCP CPU
  GDB target is instantiated.

The 60-second fast-DMI sample showed the next failure point:

- TF-M reached `tfm_hal_system_halt()` through
  `tfm_spm_partition_psa_panic()`.
- RSE console printed `Creating an empty ITS flash layout.` followed by
  `Partition initialization FAILED`.
- AP CPU0 had entered TF-A BL2 `mhu_v3_x_doorbell_read()` and was waiting on
  RSE/SCP-doorbell traffic; Linux had not started.

For storage-fidelity debugging, keep `QBOX_RDASPEN_BOOT_FLASH_DMI=false`.
The 100-second storage-fidelity sample
`gdb-short-100s-targets-20260525-v1` reached a later RSE/AP interaction:

- TF-M was in `nor_send_cmd_byte()` from the CFI Strata flash driver.
- AP/Trusted Services SE-Proxy was in `mhu_v3_x_doorbell_read()`.
- AP secure-service probes resolved through the Trusted Services symbol map.

This makes the current GDB triage point explicit: fast boot-flash DMI can
expose or hide ITS flash command behavior, so storage issues should be
debugged with boot-flash DMI disabled even when ATU and host-memory DMI are
enabled for speed.

## 2026-05-25 Secure-Storage Marker Samples

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-t064-ps-object-trace-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-20260525-v1/`

Use marker-gated samples for U-Boot variable enrollment instead of tmux
screen inspection:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
timeout 360s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-marker '2023 bytes read' \
  --sample-marker-post-delay 30 \
  --sample-delay 260 \
  --runner-timeout 300 \
  --gdb-timeout 12 \
  --copy-writable-flash \
  --ignore-fail-patterns \
  --out-dir build/qbox-fvp-rd-aspen/gdb-t064-db-read-post30-YYYYMMDD-vN \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result from the 2026-05-25 run:

- `gdb-t061-db-enroll-marker-20260525-v1` found
  `Error: "db" not defined` after 196.064 seconds. U-Boot had enrolled PK and
  KEK, then entered the `db` path. AP SE-Proxy was waiting in
  `secure_storage_ipc_remove()` with PSA call type `1004`; RSE/TF-M was in
  SFCP pointer-access deserialization and ATU mapping. The MHU trace had
  `105/104` requests/responses with one bounded in-flight request.
- `gdb-t064-ps-object-trace-20260525-v1` used the heavier
  `--tfm-ps-object-table-trace` path. It proved PS object-table initialization,
  authentication, HUK/key derivation, and RSE flash erase calls, but the
  breakpoint trace did not reach `db` enrollment before its short cap.
- `gdb-t064-db-read-post30-20260525-v1` did not reach `2023 bytes read` within
  260.085 seconds, but the all-target probes attached. The sampled AP
  SE-Proxy call was Protected Storage GET_INFO (`type=1003`, uid 7) waiting
  for MHU sender clear, while RSE/TF-M was receiving the request in the
  CMU_MHU2 interrupt path. The MHU trace paired 26 of 27 requests; the single
  missing request was the bounded in-flight transaction.

Current interpretation: AP-RSE GDB, AP firmware/Linux GDB, QBox host GDB, and
SCP/Zephyr symbol inspection are operational. The remaining secure-variable
gap is the RSE Protected Storage transaction sequence around `db`/`dbx`
completion, not basic GDB setup or AP-RSE MHU doorbell routing.

Follow-up non-GDB and GDB evidence changed the split:

- `rse-t064-db-nogdb-20260525-v1` reaches `PK key is enrolled successfully!`,
  `KEK key is enrolled successfully!`, `db key is enrolled successfully!`,
  `dbx key is enrolled successfully!`, and
  `FWU: ExitBootServices: Booting in regular state` before the short
  Linux-login timeout.
- `gdb-exitbootservices-sample-20260525-v1` waited 340.108 seconds for the
  same `ExitBootServices` marker and did not reach it, but all live GDB
  probes still completed. AP CPU0 sampled in SE-Proxy
  `secure_storage_ipc_get_info()` / `mhu_v3_x_doorbell_read()` with PSA type
  `1003`, handle `0x40000101`, uid `6`; RSE/TF-M sampled in the CMU_MHU2
  receive path at `mhu_v3_x_get_num_channel_implemented()`. The MHU trace
  paired 21 of 22 AP secure-service requests and left only the bounded
  in-flight request `0x80061601`.

Current interpretation update: non-GDB runtime proves U-Boot secure-variable
enrollment through `dbx`. GDB remains usable for QBox host, TF-M/RSE,
AP/Linux, AP secure partitions, and symbol-only SCP-Firmware inspection, but
short GDB samples can stop earlier in the Protected Storage GET_INFO sequence
than the equivalent non-GDB run.

## Targets

The current QBox RSE configuration exposes these live GDB targets:

- RSE/TF-M: `platform.rse_cpu_pass.cpu_0.gdb_port`, default helper port
  `12340`.
- AP firmware/Linux: `platform.ap_cpu_0.gdb_port`, default helper port
  `12341`.
  The AP QEMU GDB target exposes CPU#0-CPU#3 as GDB threads in the active
  CFG2/4-CPU configuration. Use `ap-tfa-bl2.gdb`, `ap-tfa-bl31.gdb`,
  `ap-optee-core.gdb`, or `ap-u-boot.gdb` before Linux starts, and
  `linux-ap.gdb` after the kernel has started.

The current `fvp-rd-aspen-rse` path uses `scp-strategy=service-model`, so SCP
firmware has symbols but no live SCP CPU GDB target yet. The generated
`scp-firmware-symbols.gdb` script is for symbol/source inspection until a real
SCP CPU model is wired. SCP-Firmware and SI CL1 Zephyr images are AArch64 ELF
files in this build, so inspect their symbol-only scripts with
`gdb-multiarch`, not `arm-none-eabi-gdb`.

## 2026-05-24 AP Firmware Symbol Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-ap-firmware-probes-20260524-v1/`

Command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 70s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-ap-firmware-probes-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 25 \
  --runner-timeout 45 \
  --port-timeout 15 \
  --gdb-timeout 10 \
  --ignore-fail-patterns
```

Result:

- RSE/TF-M, AP/Linux, AP TF-A BL2/BL31, AP OP-TEE, AP U-Boot,
  SCP-Firmware symbol, and SI CL1 Zephyr symbol probes completed.
- At the 25-second sample, AP CPU threads were still at `0x82000`; the AP TF-A
  BL2 script resolves that address to `bl2_entrypoint`.
- The RSE sample was in TF-M BL2 `memset()` while clearing the SCMI shared
  memory window at `0x753a6000`, so this sample is before AP release rather
  than a Linux stall.
- A later AP sample in
  `build/qbox-fvp-rd-aspen/gdb-ap-login-tail-20260524-v1/` reached relocated
  U-Boot `get_ticks`, while non-GDB AP runs can reach Linux/systemd in the
  same 120-second budget.

## QBox Host Debug

Attaching to an already running `platforms-vp` process can fail on hosts with
Linux `ptrace_scope=1`, because the platform process is started by the runner.
Use the runner-side host GDB wrapper instead:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --timeout 900 \
  --out-dir build/qbox-fvp-rd-aspen/rse-host-gdb \
  --host-gdb-script build/qbox-fvp-rd-aspen/gdb-debug-YYYYMMDD-vN/gdb/qbox-host-sample.gdb \
  --platform-param platform.rse_cpu_pass.cpu_0.gdb_port=12340 \
  --platform-param platform.ap_cpu_0.gdb_port=12341
```

The runner invokes host GDB with `-iex 'set debuginfod enabled off'` so the
file-backed run does not stop for an interactive debuginfod prompt. For
non-interactive sampling, prefer the top-level helper with `--host-sample`; it
finds the child GDB process and sends `SIGINT` after the requested delay so the
GDB command file can continue to `info threads` and `thread apply all bt`.

For systems where attach is allowed, use:

```bash
gdb -p $(pgrep -n platforms-vp) \
  -x build/qbox-fvp-rd-aspen/gdb-debug-YYYYMMDD-vN/gdb/qbox-host.gdb
```

The current `tools/qbox/build` tree is configured as `CMAKE_BUILD_TYPE=Release`.
`platforms-vp` is not stripped, so host GDB can still capture process/thread
state and symbol-level backtraces, but source-line debugging requires a Debug or
RelWithDebInfo QBox build.

## 2026-05-24 Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-debug-20260524-v8/`

Command:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-v8 \
  --launch \
  --runner-timeout 90 \
  --port-timeout 30 \
  --gdb-timeout 20 \
  --sample-delay 5
```

Result:

- RSE/TF-M GDB port opened and both initial/later probes completed.
- AP/Linux CPU0 GDB port opened and both initial/later probes completed.
- QBox host attach was blocked by host `ptrace_scope`; use
  `--host-gdb-script` for host-side QBox debugging.
- The helper cleaned up `platforms-vp` and `remote_cpu` after the probe.

Observed progress:

- TF-M/RSE initial snapshot was at BL1_1 `Reset_Handler()`.
- TF-M/RSE later snapshot reached PC `0x11007342`.
- AP/Linux CPU0 remained at PC `0x82000` with SP `0x0`, disassembling as
  undefined instructions, so AP CPU0 had not reached Linux execution in this
  short probe window.

## 2026-05-24 Source-Mapped Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-debug-20260524-codex-final/`

Command:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-codex-final \
  --launch \
  --runner-timeout 60 \
  --port-timeout 25 \
  --gdb-timeout 15 \
  --sample-delay 4
```

Result:

- Source maps were generated for TF-M, SCP-Firmware, and Linux.
- RSE/TF-M and AP/Linux GDB ports opened and probe commands completed.
- TF-M/RSE reached BL1_1 startup at PC `0x110005de`, then later reached PC
  `0x11007342`.
- AP/Linux CPU0 was still at PC `0x82000` with SP `0x0` in this short probe.
- QBox host attach remained blocked by host `ptrace_scope`; use
  `--host-gdb-script` for host-side debugging without changing host policy.
- SCP-Firmware remains symbol/source-only because the current QBox path uses
  the SCP service model and has no live SCP CPU target.
- Host-GDB wrapper smoke was run at
  `build/qbox-fvp-rd-aspen/rse-host-gdb-smoke-20260524/`; it launched
  `platforms-vp` under GDB and timed out intentionally after 20 seconds.

## 2026-05-24 Short Timeout Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-debug-20260524-short-codex-v3/`

Command:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-short-codex-v3 \
  --runner-timeout 40 \
  --port-timeout 12 \
  --gdb-timeout 8 \
  --sample-delay 3 \
  --launch
```

Result:

- `tfm-rse-current.gdb` restored source-mapped TF-M backtraces across BL1_1
  and BL1_2.
- RSE/TF-M reached BL1_2 `main()` image validation and was reading encrypted
  image data through `Driver_FLASH0_ReadData()` and the Strata CFI path.
- AP/Linux CPU0 GDB was reachable, but CPU0 was still at PC `0x82000` with
  SP `0x0`; Linux had not started in this short window.
- QBox host attach remained blocked by host `ptrace_scope`; the generated
  `qbox-host-run.gdb` path was separately smoke-tested with
  `--host-gdb-script` and launched `platforms-vp` under GDB.

## 2026-05-24 All-Target Host-Sample Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-debug-20260524-all-targets-v3/`

Command:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-all-targets-v3 \
  --runner-timeout 45 \
  --port-timeout 12 \
  --gdb-timeout 10 \
  --sample-delay 3 \
  --host-sample \
  --host-sample-seconds 8 \
  --launch
```

Result:

- RSE/TF-M GDB port opened; the later sample reached BL1_2 image validation
  and `Driver_FLASH0_ReadData()` through the Strata CFI path.
- AP/Linux GDB port opened; `info threads` showed CPU#0 running and CPU#1-3
  halted at PC `0x82000`, SP `0x0`, so Linux had not started in this short
  window.
- QBox host attach still failed under host `ptrace_scope`, but the host
  `--host-sample` path captured a GDB interrupt/backtrace successfully:
  `host_gdb_sample_backtrace_captured: True`.
- SCP-Firmware source/symbol mapping was generated from
  `scp-firmware/2.16.0+git`, but no live SCP CPU GDB port exists while this
  QBox configuration uses the SCP service model.
- SI CL1 Zephyr source/symbol mapping was generated from
  `zephyr-demos-cl1/4.1.0+git`; no live SI CL1 CPU target is instantiated yet.

Key progress:

```text
TF-M/RSE PC: 0x11007342 <nor_cfi_reg_read+2>
TF-M/RSE stack: Driver_FLASH0_ReadData -> bl1_image_copy_to_sram ->
  copy_and_decrypt_image -> bl1_2_validate_image -> main
AP/Linux threads: CPU#0 running at 0x82000, CPU#1-3 halted at 0x82000
QBox host: sc_core::sc_start plus QemuCpu::wait_for_work/prepare_run_cpu
```

## 2026-05-24 Short All-Target Fault Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-short-all-targets-20260524-v2/`

Command:

```bash
QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true \
QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true \
QBOX_RDASPEN_ATU_DMI=false \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_HOST_MEMORY_DMI=false \
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-delay 4 \
  --runner-timeout 15 \
  --port-timeout 8 \
  --gdb-timeout 10 \
  --host-sample \
  --host-sample-seconds 2 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-short-all-targets-20260524-v2 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- RSE/TF-M GDB port opened and the later probe completed.
- AP/Linux GDB port opened and the later probe completed.
- SCP-Firmware and SI CL1 Zephyr symbol/source probes completed with
  `gdb-multiarch`; they remain symbol-only because no live SCP or SI CL1 CPU
  GDB target is instantiated in the current QBox configuration.
- QBox host `--host-sample` captured a foreground GDB interrupt/backtrace
  without changing host `ptrace_scope`.

Observed state:

```text
TF-M/RSE: PC 0x110004ec <exception_handler>, SP 0x300055d0
TF-M/RSE fault regs: CFSR 0x01001000, HFSR 0x40000000
TF-M/RSE stack sample: 0xa4093822 repeated at 0x300055d0..0x30005600
AP/Linux: CPU#0 running at PC 0x82000, SP 0x0; CPU#1-3 halted at 0x82000
SCP-Firmware symbols: rdaspen-si0-bl2.elf, entry 0x120000000
SI CL1 Zephyr symbols: zephyr-demos-cl1.elf, entry 0x14000647c
QBox host: sc_core::sc_start plus QemuCpu::wait_for_work/prepare_run_cpu
```

Interpretation:

The current short probe shows the rebuilt RSE path failing early in BL1_1
before any RSE UART banner or AP/Linux boot handoff. The stack is overwritten
with the CC3XX RNG fill pattern `0xa4093822`; this matches the BL1_1
`startup_dma_double_word_memset(DTCM_CPU0_BASE_S, DTCM_SIZE, ...)` path used
while TF-M has TRAM enabled. The immediate modeling gap is the QBox RSE
DTCM/ITCM CPU0 alias behavior around the DMA350/TRAM erase/fill sequence, not
Linux or SCP execution.

## 2026-05-24 Keepalive Register Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-keepalive-regs-20260524-v1/`

Command:

```bash
QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true \
QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true \
QBOX_RDASPEN_ATU_DMI=false \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_HOST_MEMORY_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=false \
QBOX_RDASPEN_LCM_TRACE=true \
QBOX_RDASPEN_LCM_TRACE_LIMIT=140 \
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --ignore-fail-patterns \
  --sample-delay 4 \
  --runner-timeout 15 \
  --port-timeout 8 \
  --gdb-timeout 10 \
  --host-sample \
  --host-sample-seconds 2 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-keepalive-regs-20260524-v1 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- RSE/TF-M and AP/Linux GDB ports opened and later probes completed.
- SCP-Firmware and SI CL1 Zephyr symbol/source probes completed with
  `gdb-multiarch`; both remain symbol-only because the current QBox path uses
  the SCP service model and does not instantiate live SCP/SI CL1 CPUs.
- QBox host `--host-sample` captured a foreground GDB interrupt/backtrace
  without changing host `ptrace_scope`.
- The runner was intentionally terminated at the short timeout after keeping
  the target alive despite `[ERR]`.

Observed state:

```text
TF-M/RSE: boot_platform_error_state(error=0x95a5a5be)
TF-M/RSE PC: 0x11006e24 <boot_platform_error_state+24>
TF-M/RSE SP: 0x30005630
TF-M/RSE fault regs: CFSR/HFSR/SFSR all zero; this is not a HardFault.
Decoded error: 0x95a5a5be ^ 0xa5a5a5a5 = 0x3000001b
Decoded source: LCM_ERROR_OTP_READ_READ_VERIFY_FAIL
AP/Linux: CPU#0 running at PC 0x82000, SP 0x0; CPU#1-3 halted at 0x82000
SCP-Firmware symbols: rdaspen-si0-bl2.elf, entry 0x120000000
SI CL1 Zephyr symbols: zephyr-demos-cl1.elf, entry 0x14000647c
QBox host: sc_core::sc_start plus QemuCpu::wait_for_work/prepare_run_cpu
```

Source mapping:

- `boot_platform_error_state()` is the common TF-M BL1_1 fatal loop in
  `platform/ext/common/boot_hal_bl1_1.c`.
- The RSE-specific `boot_platform_init()` calls `minimal_otp_init()` before
  debug setup.
- `minimal_otp_init()` selects `tfm_plat_otp_mini_init()` for SE lifecycle.
- `tfm_plat_otp_mini_init()` calls `load_area_info()`, which reads LCM OTP
  area metadata.
- The decoded error maps to the LCM double-read verification path in
  `lcm_otp_read()`.

Interpretation:

The previous early BL1_1 HardFault is removed when DTCM DMI is disabled for
the current local-crypto/local-boot-flash debug path. The current blocker is
now the LCM OTP read-verify path, not Linux or SCP execution. AP/Linux remains
pre-boot because RSE has not reached the RSE/SCP/AP handoff.

## 2026-05-24 User Short All-Target Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-debug-20260524-user-short-v1/`

Command:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-debug-20260524-user-short-v1 \
  --launch \
  --runner-timeout 35 \
  --port-timeout 10 \
  --gdb-timeout 8 \
  --sample-delay 3 \
  --host-sample \
  --host-sample-seconds 5 \
  --ignore-fail-patterns
```

Result:

- RSE/TF-M and AP/Linux GDB ports opened and both initial/later probes
  completed.
- QBox host foreground `--host-sample` captured a GDB interrupt/backtrace;
  direct attach still hit the host `ptrace_scope` restriction.
- SCP-Firmware and SI CL1 Zephyr symbol/source scripts completed with
  `gdb-multiarch`. They remain symbol-only in the current QBox path because
  no live SCP or SI CL1 CPU target is instantiated.

Observed state:

```text
TF-M/RSE initial: atu_rse_set_start_logical_address()
TF-M/RSE later: boot_platform_error_state(error=0x95a5a5be)
TF-M/RSE decoded error: 0x95a5a5be ^ 0xa5a5a5a5 = 0x3000001b
AP/Linux: CPU#0 running at PC 0x82000, SP 0x0; CPU#1-3 halted at 0x82000
SCP-Firmware symbols: rdaspen-si0-bl2.elf, entry 0x120000000
SI CL1 Zephyr symbols: zephyr-demos-cl1.elf, entry 0x14000647c
QBox host: sc_core::sc_start plus QemuCpu::wait_for_work()/prepare_run_cpu()
```

The reusable entry points from this bundle are:

- `gdb/tfm-rse-current.gdb` for TF-M/RSE current-PC and backtrace inspection.
- `gdb/linux-ap.gdb` for AP/Linux CPU0-3 thread state.
- `gdb/qbox-host-sample.gdb` for launching QBox under host GDB when attach is
  blocked.
- `gdb/scp-firmware-symbols.gdb` for SCP-Firmware source/symbol inspection
  until a live SCP CPU model is wired.

## 2026-05-24 DTCM Alias And Post-Fix Probe

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-bl1-2-source-alias-compare-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-bl1-2-dtcm-alias-compare-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-dtcm-unified-default-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-debug-20260524-post-alias-v1/`

The focused GDB breakpoint at `bl1_1_validate_image_at_addr + 94` showed:

```text
ITCM 0x10004000 sha256: 18d5ffb0747feba821b64ac9eda4367b0b7ae998663916b2dfa107619566d33c
ITCM 0x1a004000 sha256: 18d5ffb0747feba821b64ac9eda4367b0b7ae998663916b2dfa107619566d33c
stored BL1_2 hash:       18d5ffb0747feba821b64ac9eda4367b0b7ae998663916b2dfa107619566d33c
CC3XX computed hash:     b3c904a855b9d1e8ff160d56ad1fd93c797538e6a8b4c08fe33b74a6d1adf228
```

The computed hash matched SHA-256 over the correct first `0x1fc0` bytes plus
the stale final 64-byte DTCM CPU0 alias buffer:

```text
0x30003820: 64 bytes of zero, matching BL1_2 tail
0x34003820: repeated 0xa4093822 TRAM-fill pattern
```

`QBOX_RDASPEN_RSE_SPLIT_CPU0_DTCM_ALIAS` therefore now defaults to `false`.
With the unified DTCM alias default, the short local-crypto/local-flash run
reaches:

```text
[INF] Starting TF-M BL1_1
[INF] Jumping to BL1_2
[INF] Starting TF-M BL1_2
[INF] Attempting to boot image 0
[ERR] BL2 image failed to decrypt
```

The post-fix all-target GDB bundle confirmed the same reusable environment:
RSE/TF-M and AP/Linux ports opened, TF-M probes completed, AP/Linux CPU0-3
remained at `0x82000`, SCP-Firmware and SI CL1 symbol probes completed, and
the QBox host GDB wrapper captured `sc_core::sc_start()` and QEMU CPU worker
backtraces. Live SCP-Firmware stepping is still unavailable until a real SCP
CPU model with a `gdb_port` replaces the service-model path.

## 2026-05-24 RSE VM DMI And Current Post-Decryption Probe

Artifacts:

- `build/qbox-fvp-rd-aspen/rse-vm-dmi-disabled-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-vm-dmi-disabled-60s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/rse-pc-trace-post-decrypt-60s-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-current-post-decrypt-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-current-post-decrypt-20260524-v2/`
- `build/qbox-fvp-rd-aspen/gdb-vm-dmi-perm-fix-effective-env-20260524-v1/`

The BL2 decrypt failure after the DTCM alias fix was isolated to RSE VM0/VM1
DMI. GDB showed the encrypted image IV copied into VM0 as `0x00000067`
followed by zero words, while the raw boot flash contained the correct
consecutive bytes `67 a4 79 10 ...`. Disabling
`QBOX_RDASPEN_RSE_VM_DMI` lets BL1_2 read the proper encrypted-image header
and print:

```text
[INF] Starting TF-M BL1_2
[INF] Attempting to boot image 0
[INF] BL2 image decrypted successfully
```

The focused DMI byte-store issue is fixed by preserving granted access in
`QemuInstanceDmiManager::get_region()`. The plain byte-store, shared-memory
byte-store, and same-process shared-memory external-write tests all pass with
DMI enabled. Before the fd-backed remote-DMI follow-up in the next section, a
VM-DMI-on sample still failed in the full RSE path:

```bash
QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true \
QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true \
QBOX_RDASPEN_ATU_DMI=false \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_HOST_MEMORY_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=false \
QBOX_RDASPEN_RSE_VM_DMI=true \
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --ignore-fail-patterns \
  --runner-timeout 18 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --sample-delay 10 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-vm-dmi-perm-fix-effective-env-20260524-v1
```

That bundle records `QBOX_RDASPEN_RSE_VM_DMI=true` in `debug-env.json`.
Observed state:

```text
TF-M/RSE: vm_partial_write_fix_apply() at PC 0x1100f750
Backtrace: vm_partial_write_fix_apply ->
  cc3xx_dma_platform_epilogue -> trigger_dma ->
  cc3xx_lowlevel_dma_buffered_input_data ->
  cc3xx_lowlevel_aes_update -> bl1_aes_256_ctr_decrypt ->
  copy_and_decrypt_image -> bl1_2_validate_image -> main
RSE UART: [ERR] BL2 image failed to decrypt
AP/Linux: CPU#0 remains at PC 0x82000, SP 0x0
```

The 28-second all-target GDB sample used:

```bash
QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true \
QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true \
QBOX_RDASPEN_ATU_DMI=false \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_HOST_MEMORY_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=false \
QBOX_RDASPEN_RSE_VM_DMI=false \
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --ignore-fail-patterns \
  --runner-timeout 45 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --sample-delay 28 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-post-decrypt-20260524-v2 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Observed state:

```text
TF-M/RSE: hash_digit_array() at PC 0x1100a42c
Backtrace: hash_digit_array ->
  mbedtls_lmots_calculate_public_key_candidate ->
  mbedtls_lms_verify -> pq_crypto_verify ->
  validate_image_signature -> bl1_2_validate_image_at_addr ->
  bl1_2_validate_image -> main
Fault registers: CFSR/HFSR/SFSR all zero
AP/Linux: CPU#0 running at PC 0x82000, SP 0x0; CPU#1-3 halted at 0x82000
SCP-Firmware: symbols/source available, no live SCP CPU GDB target
SI CL1 Zephyr: symbols/source available, no live SI CL1 CPU GDB target
```

A 60-second file-backed PC trace confirms this is not a fault/reset loop: the
RSE remains secure, `VTOR_S` stays at `0x10004000`, fault registers stay zero,
and the samples remain in BL1_2 flash copy, CC3XX hash state, and LMS/LMOTS
signature validation. The next implementation issue is therefore model
performance/fidelity in the BL1_2 signature-validation path, especially the
then-unfixed remote-process VM DMI behavior in the full CC3XX AES decrypt path
and the expensive Strata flash/CC3XX hash access pattern. The following
fd-backed remote-DMI probe supersedes the decrypt-failure part of this
analysis.

## 2026-05-24 Remote FD DMI And All-Target GDB Probe

Artifacts:

- `build/qbox-fvp-rd-aspen/rse-vm-dmi-remote-fd-fix-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-rse-vm-dmi-remote-fd-fix-20260524-v4/`

The earlier VM-DMI-on decrypt failure was superseded by exporting
`memory_region_init_ram_from_fd()` through libqemu and passing the shared-memory
file descriptor/offset from SystemC memory services into QEMU DMI aliases. This
keeps RemotePass and QEMU DMI views on the same fd-backed memory instead of a
private pointer mapping.

Focused validation:

```bash
cmake --build tools/qbox/build \
  --target remote_cpu cortex-m55-vp cortex-m55-dmi-byte-store-test \
  --parallel 8

timeout 45s ctest --test-dir tools/qbox/build \
  -R 'cortex_m55_remote_dmi_byte_store_(on|off)' \
  --output-on-failure
```

Result:

```text
100% tests passed, 0 tests failed out of 2
```

The short RSE runtime with `QBOX_RDASPEN_RSE_VM_DMI=true` now reaches:

```text
[INF] Starting TF-M BL1_2
[INF] Attempting to boot image 0
[INF] BL2 image decrypted successfully
```

The all-target GDB bundle was generated with AP CPUs enabled and short
timeouts:

```bash
QBOX_RDASPEN_RSE_VM_DMI=true \
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --ignore-fail-patterns \
  --runner-timeout 20 \
  --port-timeout 5 \
  --gdb-timeout 6 \
  --sample-delay 12 \
  --host-sample \
  --host-sample-seconds 2 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-rse-vm-dmi-remote-fd-fix-20260524-v4
```

Observed state:

```text
RSE/TF-M port: listening on 12340
TF-M/RSE: cc3xx_lowlevel_dma_buffered_input_data()
Backtrace: CC3XX hash update -> LMS/LMOTS signature validation ->
  validate_image_signature -> bl1_2_validate_image -> main
RSE UART: BL2 image decrypted successfully

AP/Linux port: listening on 12341
AP/Linux: CPU#0 running at PC 0x82000, SP 0x0;
  CPU#1-3 halted at PC 0x82000

SCP-Firmware: rdaspen-si0-bl2.elf symbols/source loaded, entry 0x120000000
SI CL1 Zephyr: zephyr-demos-cl1.elf symbols/source loaded, entry 0x14000647c
QBox host: foreground GDB sample captured sc_start() and QEMU CPU threads
```

SCP-Firmware still has no live CPU GDB port in this configuration because the
current launch uses `--scp-strategy service-model`; the symbol script remains
the supported inspection path until a real SCP CPU model is selected. AP/Linux
is reachable through GDB, but it has not started executing Linux in this short
RSE sample because RSE/TF-M remains in BL1_2 signature validation.

## 2026-05-24 AP PFDI/OP-TEE Snapshot And Host Sample

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-ap-pfdi-snapshot-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260524-v1/`
- Slim quiet-console runtime logs:
  `build/qbox-fvp-rd-aspen/rse-current-quiet-console-login-20260524-v1-slim/`

The quiet-console rootfs preparation patches the WIC boot entry in a per-run
sparse copy, adding `console=ttyAMA0,115200` while removing `earlycon`,
`ignore_loglevel`, and `initcall_debug` from the copied image only. The 140
second runtime with that rootfs reached RSE AP power-on and AP secure BL2/BL31,
then timed out before login. The slim artifact preserves `summary.txt`,
`result.json`, UART logs, and the patched `boot.conf`; the large copied WIC was
removed to recover `/build` space.

AP firmware snapshot command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 190s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-ap-pfdi-snapshot-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 90 \
  --runner-timeout 125 \
  --port-timeout 18 \
  --gdb-timeout 10 \
  --ignore-fail-patterns
```

Observed state:

```text
RSE/TF-M:
  PC 0x31063480, WFE loop in RSE runtime; fault registers captured

AP TF-A BL31:
  CPU#0 pc 0xc350 <pfdi_cpu_self_test_result+68>
  Backtrace:
    pfdi_cpu_self_test_result ->
    plat_pfdi_pe_init -> std_svc_setup ->
    runtime_svc_init -> bl31_main
  CPU#1 was in psci_pwrdown_cpu_end_terminal()

AP OP-TEE:
  CPU#0 pc 0xffc161f0 <pl011_putc+24>
  Backtrace:
    pl011_putc -> trace_ext_puts -> trace_vprintf ->
    trace_printf -> boot_mem_release_unused ->
    init_primary -> boot_init_primary_early -> _start

AP/Linux:
  Linux symbols attach through the same AP GDB port, but the sample is still
  secure-world firmware, before Linux execution.

SCP-Firmware:
  rdaspen-si0-bl2.elf symbols/source loaded, entry 0x120000000.
  No live SCP CPU GDB port exists while using the service-model strategy.
```

The secure UART log from the same run shows BL31 PFDI secondary-core tests
complete and OP-TEE primary CPU initialization start. This means the GDB
snapshot is a secure-world firmware progress sample, not evidence of a Linux
stall.

QBox host sample command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 90s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 1 \
  --runner-timeout 20 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --host-sample \
  --host-sample-seconds 6 \
  --ignore-fail-patterns
```

Result:

```text
host_gdb_sample_backtrace_captured: True
QBox host GDB captured platforms-vp, RPC server/client threads,
QEMU iothreads, call_rcu threads, worker threads, and CPU 0..3/TCG threads.
The AP CPU worker frames include QemuCpu::wait_for_work() and
QemuCpu::prepare_run_cpu() through cpu_arm_cortexA720AE.so.
```

## 2026-05-24 Current Short And Linux Tail Probes

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-current-all-target-short-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-current-ap-linux-tail-20260524-v1/`

Short all-target command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 135s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-all-target-short-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 75 \
  --runner-timeout 105 \
  --port-timeout 10 \
  --gdb-timeout 8 \
  --host-sample \
  --host-sample-seconds 3 \
  --ignore-fail-patterns \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Observed 75-second state:

```text
RSE/TF-M:
  PC 0x31063480, WFE loop in the RSE runtime image

AP TF-A BL31:
  CPU#0 pc 0xc30c <pfdi_cpu_self_test_result>
  Backtrace:
    pfdi_cpu_self_test_result ->
    plat_pfdi_pe_init -> std_svc_setup ->
    runtime_svc_init -> bl31_main

AP/Linux GDB script:
  The AP target is reachable, but the sampled PC is still pre-Linux firmware
  at this 75-second point.

SCP-Firmware:
  rdaspen-si0-bl2.elf symbols/source loaded, entry 0x120000000.
  No live SCP CPU GDB port exists while using the service-model strategy.

QBox host:
  host_gdb_sample_backtrace_captured: True
  Captured platforms-vp, SystemC sc_start, RPC server/client, QEMU iothread,
  call_rcu, worker, and AP CPU TCG threads.
```

Linux tail command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 155s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-ap-linux-tail-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 112 \
  --runner-timeout 125 \
  --port-timeout 10 \
  --gdb-timeout 8 \
  --ignore-fail-patterns \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Observed 112-second state:

```text
RSE/TF-M:
  PC 0x31063480, WFE loop in the RSE runtime image after AP handoff

AP/Linux:
  CPU#0 pc 0xffff80008090a368 <pl011_putc+32>
  Backtrace:
    pl011_putc -> uart_console_write
  CPU#1-3 are halted at 0xf1d0 from the AP GDB target view.

Primary UART:
  Linux entered early initcall processing, brought up CPU1-CPU3, and
  activated all 4 CPUs before the probe ended.
```

The copied raw flash/disk/SRAM files from these two debug artifacts were
removed after capturing `README.md`, `debug-env.json`, `progress-report.md`,
`gdb/`, `probes/`, and UART/platform logs to keep `/build` usable.

## 2026-05-24 Current All-Layer Debug Bundle

Artifact:
`build/qbox-fvp-rd-aspen/gdb-current-all-debug-20260524-v1/`

Command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 190s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-all-debug-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 112 \
  --runner-timeout 130 \
  --port-timeout 10 \
  --gdb-timeout 6 \
  --host-sample \
  --host-sample-seconds 3 \
  --ignore-fail-patterns \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Observed state:

```text
QBox host:
  host_gdb_sample_backtrace_captured: True
  Captured platforms-vp, SystemC sc_start, RPC server/client,
  QEMU iothreads, call_rcu, worker, and AP CPU TCG threads.
  AP CPU worker frames include QemuCpu::wait_for_work(),
  QemuCpu::prepare_run_cpu(), and QemuCpu::end_of_loop_cb().

TF-M/RSE:
  PC 0x31063480, WFE loop in the RSE runtime image after AP handoff.
  Fault/status registers and stack words are captured in probes/tfm-later.txt.

SCP-Firmware:
  gdb/scp-firmware-symbols.gdb loads rdaspen-si0-bl2.elf and resolves
  entry point 0x120000000.
  No live SCP CPU GDB target exists in the current QBox path because
  scp-strategy=service-model does not instantiate Safety Island CL0/SCP.

AP/Linux:
  Linux symbols resolve the AP target to kernel text.
  CPU#0 PC 0xffff800080e91b68 <cpu_do_idle+8>.
  CPU#1 PC 0xffff800080316dd8 <__slab_alloc.isra.0>.
  CPU#2 and CPU#3 are also in cpu_do_idle.
```

The primary UART from the same run reached Linux rootfs mount and systemd
startup:

```text
arm-scmi arm-scmi.1.auto: SCMI Notifications - Core Enabled.
arm-scmi arm-scmi.1.auto: SCMI Protocol v2.1 'QBox:RD-Aspen' Firmware version 0x1
VFS: Mounted root (ext4 filesystem) readonly on device 253:2.
Run /sbin/init as init process
systemd[1]: systemd 257.4 running in system mode
Welcome to Edge Workload Abstraction and Orchestration Layer v.2.2.0 (walnascar)!
systemd[1]: Hostname set to <fvp-rd-aspen>.
```

The RSE console still stops after the runtime jump marker and does not emit
the FVP RSE runtime measured-boot markers or
`SCMI Comms subscribed to power state notifications`:

```text
[INF] BL2: RSE to SCP SCMI power on AP succeeded.
[INF] Bootloader chainload address offset: 0x27000
[INF] Image version: v2.2.2
[INF] Jumping to the first image slot
```

The helper terminates the sampled platform after the GDB probes, so
`run/result.json` is not expected for this bundle. The preserved evidence is
`progress-report.md`, `debug-env.json`, `gdb/`, `probes/`, `run/qbox-*.log`,
`run/mhuv3-trace.log`, and `host-gdb-run/qbox-platform.log`. Reproducible raw
flash/disk/SRAM copies were removed after capture to keep `/build` usable.

## 2026-05-24 TF-M Runtime Halt And Linux GDB Update

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-runtime-cpu0secctrl-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-runtime-fast-after-cpu0secctrl-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-setup-regenerated-20260524-v3/`

The earlier all-layer bundle left the TF-M/RSE PC at `0x31063480` without the
runtime `tfm_s.elf` symbol file. Its captured fault registers showed a precise
BusFault:

```text
CFSR 0x00008200
HFSR 0x40000000
BFAR 0x50011000
```

TF-M maps `0x50011000` to `CPU0_SECCTRL_BASE_S`; the stacked PC was inside
`sau_and_idau_cfg()`. The QBox Lua platform now provides the CPU0 security,
power-control, and identity register windows, plus the RSE SIC and VM/SIC MPC
identification fields needed by TF-M's SIE MPC driver.

Fast post-fix probe command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-runtime-fast-after-cpu0secctrl-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 112 \
  --runner-timeout 135 \
  --port-timeout 10 \
  --gdb-timeout 6 \
  --ignore-fail-patterns
```

Post-fix result:

| Target | Evidence |
| --- | --- |
| TF-M/RSE | `probes/tfm-s-later.txt` resolves PC `0x31063480` to `tfm_hal_system_halt+2`; backtrace is `tfm_hal_system_halt()` -> `tfm_core_panic()` -> `main()` at `secure_fw/spm/core/main.c:122`. |
| TF-M fault state | `CFSR`, `HFSR`, `MMFAR`, and `BFAR` are all zero, so the previous `CPU0_SECCTRL_BASE_S` precise BusFault is gone. |
| TF-M return value | `r0 = 0xffffff03` at the panic path, which is the next value to split inside `tfm_core_init()`. |
| AP/Linux | `probes/linux-later.txt` resolves CPU#0 to `cpu_do_idle+8`; CPU#1 and CPU#2 also idle, and CPU#3 is executing userspace/unknown VA from the AP GDB thread view. |
| Primary UART | `run/qbox-primary-console.log` reaches SCMI Linux probe, rootfs mount, `/sbin/init`, `systemd 257.4`, EWAOL welcome, and hostname setup. |
| SCP-Firmware | `probes/scp-symbols.txt` still loads `rdaspen-si0-bl2.elf` and resolves entry `0x120000000`; no live SCP CPU GDB target exists while `scp-strategy=service-model` is active. |

The reusable bundle in
`build/qbox-fvp-rd-aspen/gdb-setup-regenerated-20260524-v3/` now includes a
dedicated `gdb/tfm-s.gdb` script, so future RSE runtime samples resolve
`tfm_s.elf` instead of treating the runtime image as anonymous memory. The
README commands also pass `--no-copy-writable-flash` to avoid large per-run raw
flash copies for debug-only sampling.

## 2026-05-24 TF-M Core-Init Split

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-static-boundary-trace-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-static-boundary-success-after-mpc-load-fix-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-core-init-trace-after-mpc-load-fix-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-core-init-trace-after-dma-iidr-fix-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-host-and-live-sample-after-dma-iidr-fix-20260524-v1/`

The helper now emits two branch-oriented TF-M scripts in addition to the
current-PC samplers:

- `gdb/tfm-static-boundary-trace.gdb` traces
  `tfm_hal_set_up_static_boundaries()`, `mpc_init_cfg()`, and
  `mpc_sie_init()` branch outcomes while dumping VM0/VM1 MPC register
  snapshots.
- `gdb/tfm-core-init-trace.gdb` traces the major `tfm_core_init()` failure
  branches and the RSE platform HAL initialization branches.

The first static-boundary trace proved that the QBox Lua `load.data` numeric
register keys were effectively shifted one 32-bit slot early. VM0/VM1 MPC
snapshots showed `BLK_CFG` and `PIDR0` at the wrong effective offsets:

```text
0x50083010: 0x00000007
0x50083014: 0x00000000
0x50083fe0: 0x00000000
```

After shifting the configured Lua keys for VM0/VM1 MPC and SIC MPC reset
values, the same GDB trace shows SIE300-compatible values at the TF-M-visible
offsets and reaches the static-boundary success return:

```text
0x50083010: 0x00000001
0x50083014: 0x00000007
0x50083fe0: 0x00000065
0x50084010: 0x00000001
0x50084014: 0x00000007
0x50084fe0: 0x00000065
TRACE mpc_init_cfg shared-return success pc=0x10000296
SUCCESS static-boundary return pc=0x100005da
```

The next `tfm_core_init()` split then failed in the RSE platform HAL DMA
initialization branch:

```text
FAIL tfm_hal_platform_init dma-init branch pc=0x100006a2
```

Source inspection of the generated TF-M DMA350 driver showed that
`dma350_init()` checks `DMA_INFO.IIDR` and `DMA_INFO.AIDR` before platform
initialization can continue. The QBox DMA350 model now exposes those reset
identification values at offsets `0xfc8` and `0xfcc`. With that change,
`tfm-core-init-trace.gdb` reaches the common success return:

```text
TRACE tfm_core_init entry pc=0x10000000
SUCCESS tfm_core_init common-return pc=0x10000048
```

The follow-on TF-M runtime sample still reaches `tfm_hal_system_halt()`, but
the backtrace has moved past `tfm_core_init()`:

```text
#0  tfm_hal_system_halt()
#1  tfm_spm_partition_psa_panic()
#2  tfm_arch_thread_fn_call(...)
```

So the current TF-M blocker is no longer static boundary setup,
`CPU0_SECCTRL_BASE_S`, or DMA350 initialization. It is now a later secure
partition panic after core initialization succeeds.

The same after-DMA host/live bundle confirms the reusable all-target debug
environment is still available:

| Target | Current evidence |
| --- | --- |
| QBox host | `host_gdb_sample_backtrace_captured: True`; host GDB captures `platforms-vp`, SystemC `SC_START`/`sc_start`, RPC server/client, QEMU iothread, `call_rcu`, worker, and AP CPU TCG threads. |
| TF-M/RSE | Short sample can be taken either as early BL1_1 current-PC state or as targeted static-boundary/core-init branch traces. |
| SCP-Firmware | `gdb/scp-firmware-symbols.gdb` loads `rdaspen-si0-bl2.elf` and resolves entry `0x120000000`; there is still no live SCP CPU GDB target while `scp-strategy=service-model` is active. |
| AP/Linux | The after-DMA 8-second host sample catches AP CPU0 at AP BL2 entry `0x82000`; use the earlier `gdb-runtime-fast-after-cpu0secctrl-20260524-v1/` or a longer `--sample-delay` for Linux `cpu_do_idle`/systemd evidence. |

Useful short commands:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-core-init-trace-<run-id> \
  --launch \
  --sample-only \
  --tfm-core-init-trace \
  --runner-timeout 75 \
  --port-timeout 8 \
  --gdb-timeout 6 \
  --ignore-fail-patterns

QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-static-boundary-trace-<run-id> \
  --launch \
  --sample-only \
  --tfm-static-boundary-trace \
  --runner-timeout 75 \
  --port-timeout 8 \
  --gdb-timeout 6 \
  --ignore-fail-patterns
```

## 2026-05-24 TF-M Storage Partition Split

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-partition-panic-trace-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-its-init-step-trace-strata-ff-compat-20260524-v5/`
- `build/qbox-fvp-rd-aspen/rse-no-bootflash-dmi-its-probe-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-ps-init-trace-no-bootflash-dmi-20260524-v1/`

The partition-panic trace first attributed the post-`tfm_core_init()` panic to
TF-M ITS:

```text
psa_panic -> common_sfn_thread
p_curr_thrd = 0x3101a114
pid = 0x101
entry = 0x31047cc5 -> tfm_its_entry
```

Source and symbol inspection showed the generated TF-M Strata erase path does
not issue a hardware block-erase command. Its
`cfi_strataflashj3_erase()` implementation loops through the sector and
programs `0xff` bytes. QBox therefore keeps default NOR byte-program semantics
unchanged, but the RD-Aspen RSE boot-flash instances enable the compatibility
parameter `program_ff_sets_bits=true` so this firmware erase path can restore
bytes to `0xff`.

With `QBOX_RDASPEN_BOOT_FLASH_DMI=true`, `tfm-its-init-trace.gdb` still showed
ITS failing:

```text
its_flash_fs_prepare() -> r0 = 0xffffff7c
its_flash_fs_wipe_all/status check -> r0 = 0xffffff6e
```

The matching platform log contained flash reads but no command-write effects.
That makes boot-flash DMI unsafe for storage debug until command-state DMI
invalidation/write semantics are proven.

With boot-flash DMI left disabled, ITS no longer panics and the next precise
partition blocker is PS:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_TRACE=true \
QBOX_RDASPEN_BOOT_FLASH_TRACE_LIMIT=2000 \
timeout 160s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-ps-init-trace-no-bootflash-dmi-20260524-v1 \
  --launch \
  --sample-only \
  --tfm-ps-init-trace \
  --runner-timeout 100 \
  --trace-timeout 130 \
  --port-timeout 8 \
  --gdb-timeout 6 \
  --ignore-fail-patterns
```

Result:

- `progress-report.md` records successful QBox host, TF-M/RSE, AP/Linux,
  AP TF-A BL2/BL31, AP OP-TEE, AP U-Boot, SCP-Firmware symbol, and SI CL1
  symbol probes. The helper terminates QBox after sampling, so
  `runner_returncode = -15` is expected.
- `tfm-ps-init-trace.txt` hits `tfm_ps_init()` and shows
  `ps_system_wipe_all()` returning `0x0`.
- The first and second `ps_system_prepare()` calls both return `0xffffff7c`
  (`PSA_ERROR_GENERIC_ERROR`), after which `common_sfn_thread` calls
  `psa_panic`.
- The panic stack is `tfm_sp_ps_stack`, and `0x31043529` maps to
  `tfm_ps_entry` in `tfm_ps_req_mngr.c:160`.
- AP/Linux GDB attaches through the AP target, but the sample PC is still in
  secure-world/early firmware rather than the Linux kernel.
- SCP-Firmware remains source/symbol-only because the current QBox path uses
  `scp-strategy=service-model`; live SCP stepping requires an executable SCP
  CPU model with its own GDB port.

Current conclusion: the reusable GDB environment covers QBox host, TF-M
runtime, AP firmware/Linux target state, SCP-Firmware symbols, and SI CL1
symbols. The active TF-M runtime blocker is no longer ITS flash erase/status.
It is PS `ps_system_prepare()` returning `PSA_ERROR_GENERIC_ERROR` after a
successful wipe, likely in the Protected Storage object-table crypto/key path.

## 2026-05-24 PS Object Table And Sector Erase Evidence

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-ps-its-file-trace-no-bootflash-dmi-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-ps-sector-erase-fix-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-all-targets-sample-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-all-targets-linux-sample-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-tfm-partition-panic-after-sector-fix-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-after-sector-fix-20260524-v1/`

The PS object-table trace split the earlier PS failure below
`ps_system_prepare()`. Before the flash model compatibility change, the first
`psa_its_get(uid=1)` returned success, `psa_its_get(uid=2)` returned
`PSA_ERROR_DOES_NOT_EXIST`, and `psa_its_set(uid=1)` returned success, but the
next `psa_its_get(uid=1)` failed internally while reading flash file metadata:

```text
TRACE its_flash_fs_file_get_info mblock_get_file_idx_meta return status=0xffffff7c signed=-132
TRACE ps_object_table_init table0 psa_its_get return status=0xffffff74 signed=-140
```

The generated TF-M CSS-Aspen Strata driver erases by programming `0xff` bytes
instead of issuing a CFI block-erase command. The QBox `strata_flash_j3`
component therefore now has an opt-in compatibility parameter,
`program_ff_erases_sector`, used only by the RD-Aspen RSE boot-flash instances.
It maps a sector-aligned one-byte `0xff` program operation to a full sector
erase while preserving the default NOR bit-clear behavior for other users.

The focused component test and platform validation commands were:

```bash
python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py
luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua
cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 4
ctest --test-dir tools/qbox/build -R strata_flash_j3 --output-on-failure
git -C tools/qbox diff --check
./scripts/validate_qbox_fvp_rd_aspen_map.py
cmake --build tools/qbox/build --target platforms-vp --parallel 4
```

After the change, the same PS object-table path reads the saved metadata back:

```text
TRACE ps_object_table_save_table psa_its_set return status=0x0 signed=0
TRACE its_flash_fs_file_get_info mblock_get_file_idx_meta return status=0x0 signed=0
TRACE ps_object_table_init table0 psa_its_get return status=0x0 signed=0
TRACE ps_set_active_object_table entry state0=0x2 state1=0x1
```

The trace-attached run reached AP Linux and systemd before the short timeout.
`run/result.json` reports RSE boot and measured-boot markers through BL1_2,
BL2, SI_CL0, AP_BL2, RT_0, SECURE_RT_EL3, SECURE_RT_EL1_SPMD, and BL_33, plus
the RSE-to-SCP SCMI AP power-on marker. The primary console log includes Linux
driver evidence such as `pfdi_misc`, `remoteproc remoteproc0: si-cl1 is
available`, `remote processor si-cl1 is now attached`, `virtio_net virtio0
eth0`, SMMUv3 driver markers, and systemd reaching serial login prompts.

For a non-trace all-target snapshot, the helper can attach to QBox host,
TF-M/RSE, AP/Linux, TF-A BL2/BL31, OP-TEE, U-Boot, SCP-Firmware symbols, and
SI CL1 symbols with short timeouts:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 190s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-all-targets-linux-sample-20260524-v1 \
  --launch \
  --sample-only \
  --sample-delay 105 \
  --runner-timeout 150 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --ignore-fail-patterns
```

That run produced successful GDB probe return codes for TF-M, AP/Linux,
TF-A, OP-TEE, U-Boot, SCP symbols, and SI CL1 symbols. The sampled AP CPU0 PC
was still in BL31 at `pfdi_cpu_self_test_result`, so the all-target sample
proves attachability rather than Linux runtime progress. Linux progress is
currently evidenced by the trace-attached run's file-backed console log.

The QBox-host sample run launches `platforms-vp` under GDB and interrupts it
after a short delay. `debug-env.json` reports
`host_gdb_sample_backtrace_captured=true`; the probe excerpt includes
`platforms-vp`, the SystemC `SC_START` point, QEMU `call_rcu`,
`qemu-iothread`, and AP CPU TCG threads. The host sample returns non-zero
because the helper intentionally sends SIGINT to capture the snapshot and then
terminates the sampled platform.

The current post-fix non-trace blocker is a TF-M BusFault in the NS mailbox
agent:

```text
tfm_hal_system_halt
tfm_core_panic
C_BusFault_Handler
BusFault_Handler
pid = 0x106
entry = 0x31045a0d
```

`pid.h` maps `0x106` to `TFM_NS_MAILBOX_AGENT`, and `addr2line` maps
`0x31045a0d` to `ns_agent_mailbox_entry()` in
`secure_fw/partitions/ns_agent_mailbox/ns_agent_mailbox.c`. SCP-Firmware still
has symbol/source GDB coverage only while the platform uses
`--scp-strategy service-model`; live SCP stepping requires an executable SCP
CPU model with a GDB port.

## 2026-05-24 SCMI Notify And NS Mailbox Fault

Artifacts:

- `build/qbox-fvp-rd-aspen/rse-ap-scmi-subscribe-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-all-targets-after-scmi-patch-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-tfm-partition-panic-after-scmi-notify-20260524-v2/`

The SCMI gap was split from the later TF-M runtime fault. TF-M sends a System
Power `SYS_POWER_STATE_NOTIFY` subscription request (`protocol=0x12`,
`msg=0x5`) from `scmi_comms_notification_subscribe()`. QBox now answers that
request in the MHUv3 SCMI responder, and the MHU trace proves the runtime
request succeeds:

```text
header=0x4805 protocol=0x12 msg=0x5
event=scmi-sys-power-state-notify notify_enable=1
status=0x0 length=8
```

The current halt is after that response. The focused GDB trace reports:

```text
TRACE tfm_hal_system_halt pc=0x3106347e lr=0x10001d9b
#0  tfm_hal_system_halt()
#1  tfm_core_panic()
#2  C_BusFault_Handler()
#3  BusFault_Handler()
TRACE current-load-info pid=0x106 flags=0x77f entry=0x31045a0d
```

`pid.h` maps `0x106` to `TFM_NS_MAILBOX_AGENT`, and `tfm_s.elf` maps
`0x31045a0d` to `ns_agent_mailbox_entry`. The next GDB split should focus on
`boot_ns_core()`, `tfm_inter_core_comm_init()`, `mailbox_enable_interrupts()`,
`tfm_rpc_client_call_handler()`, and the QBox AP-RSE mailbox MMIO/IRQ path.

## 2026-05-24 RSE Local MHU Split

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-tfm-ns-mailbox-trace-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-tfm-ns-mailbox-local-mhu-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-host-sample-20260524-v1/`

The focused NS mailbox trace showed the BusFault was not in
`mailbox_enable_interrupts()` or `psa_wait()`. It happened earlier, during
SFCP MHU driver initialization:

```text
#2  mhu_v3_x_driver_init(dev=0x3101999c <MHU0_SENDER_DEV_S>)
#6  sfcp_hal_init()
#7  sfcp_init()
#10 ns_agent_mailbox_entry()
CFSR = 0x00008200
BFAR = 0x50160fcc
stacked pc = 0x3104c5b8 <mhu_v3_x_driver_init+16>
```

`0x50160fcc` is `MHU0_SENDER_BASE_S + CTRL_AIDR`. The RSE platform now maps
secure local MHU0/MHU2 sender and receiver frames at `0x50160000`,
`0x50170000`, `0x501a0000`, and `0x501b0000`.

Validation:

```bash
luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua
python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py
git -C tools/qbox diff --check
cmake --build tools/qbox/build --target platforms-vp --parallel 4
./scripts/validate_qbox_fvp_rd_aspen_map.py
```

The post-fix GDB bundle no longer hits the NS mailbox fault handler. The
long-running TF-M trace exits by timeout, and the later TF-M runtime sample is
in the expected wait path:

```text
__tfm_arch_thread_fn_call_veneer()
psa_wait_thread_fn_call(signal_mask=0xffffffff, timeout=0)
```

The same AP/Linux GDB bundle resolves all AP CPU threads to `cpu_do_idle()`,
and the primary UART reaches:

```text
Edge Workload Abstraction and Orchestration Layer v.2.2.0 fvp-rd-aspen ttyAMA0
fvp-rd-aspen login:
```

QBox host debugging was also re-checked with the host-GDB wrapper. Direct
attach still fails under host ptrace restrictions, so the supported path is to
launch `platforms-vp` under GDB with `--host-sample`. The sample captures
SystemC `sc_start()`, RPC server/client threads, QEMU iothreads, `call_rcu`,
worker threads, and AP CPU TCG threads.

Remaining gap: SCP-Firmware still has symbol/source mapping only in the
current `service-model` SCP strategy, and the RSE local MHU frames are not yet
faithfully bridged to the AP-visible AP-RSE mailbox protocol. The RSE UART
still lacks the FVP marker `SCMI Comms subscribed to power state
notifications`, so the next AP-RSE mailbox task is functional request/response
bridging, not another missing local MHU identification register.

## 2026-05-24 AP-RSE Bridge And IRQ Fan-out

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-rse-mhu-irq-map-20260524-v1/`
- `build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-irq-map-20260524-v1/`

The AP-RSE secure mailbox frames now use directional bridge pairs:
`ap_s_to_rse` for AP PBX to RSE MHU2 receiver, and `rse_to_ap_s` for RSE MHU2
sender to AP MBX. The RSE `RemotePass` also exposes the full 160-line NVIC
external IRQ fan-out, with TF-M-visible receiver IRQs wired to their generated
platform numbers:

```text
CMU_MHU0_Receiver_IRQn = 41
CMU_MHU2_Receiver_IRQn = 45
SI_CL0_RSE_CMU_MHU_Receiver_IRQn = 139
```

Validation:

```bash
luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua
git -C tools/qbox diff --check
cmake --build tools/qbox/build --target platforms-vp --parallel 4
```

Runtime command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
timeout 120s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --ignore-fail-patterns \
  --runner-timeout 105 \
  --port-timeout 8 \
  --gdb-timeout 6 \
  --sample-delay 85 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-rse-mhu-irq-map-20260524-v1
```

MHU trace proof:

```text
platform.host_ap_rse_mhu_pbx event=postbox-doorbell-write pair=ap_s_to_rse channel=127 value=0x4d2
platform.rse_mhu2_receiver_s event=doorbell-signal pair=ap_s_to_rse channel=127 value=0x4d2
platform.rse_mhu2_receiver_s event=doorbell-clear pair=ap_s_to_rse channel=127 mask=0xffffffff
platform.rse_mhu2_sender_s event=postbox-doorbell-write pair=rse_to_ap_s channel=127 value=0x4d2
platform.host_ap_rse_mhu_mbx event=doorbell-signal pair=rse_to_ap_s channel=127 value=0x4d2
```

GDB result:

- TF-M/RSE later sample is in the runtime wait path:
  `__tfm_arch_thread_fn_call_veneer()` /
  `psa_wait_thread_fn_call(signal_mask=0xffffffff, timeout=0)`.
- AP TF-A BL2 no longer waits in `mhu_v3_x_doorbell_read`.
- AP progresses through BL31 and OP-TEE initialization. The secure console
  reaches OP-TEE SP loading for the SE Proxy partition.
- The current sampled AP blocker is still before Linux execution:
  CPU0 is in `plat_pfdi_pe_init()` at `drivers/arm/pfdi/pfdi_mod.c:142`,
  polling a secondary-core PFDI result that is still `PFDI_NOT_RUN`.
- `linux-ap.gdb` attaches through the same AP CPU0 port, but in this sample it
  sees the BL31 PC rather than a Linux kernel PC.

QBox host debug was rechecked with:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
timeout 90s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --host-sample \
  --ignore-fail-patterns \
  --runner-timeout 20 \
  --port-timeout 5 \
  --gdb-timeout 5 \
  --sample-delay 3 \
  --host-sample-seconds 3 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-irq-map-20260524-v1
```

The host-GDB wrapper captured `sc_core::sc_start()`, RPC server/client threads,
QEMU iothread/call_rcu/worker threads, and AP `CPU */TCG` threads. Direct host
attach remains subject to Linux `ptrace_scope`; use `--host-sample` or
`--host-gdb-script` for reproducible QBox host inspection.

## 2026-05-25 Short All-Layer GDB Refresh

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-current-all-debug-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-tfm-partition-panic-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-tfm-its-init-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-current-storage-safe-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-current-storage-safe-linux-tail-20260525-v1/`

The current reusable debug setup is still:

- QBox host: launch under GDB with `--host-sample` or pass
  `--host-gdb-script`; direct attach is subject to host ptrace policy.
- TF-M/RSE: live remote target on `platform.rse_cpu_pass.cpu_0.gdb_port`,
  helper default `12340`.
- AP firmware/Linux: live remote target on `platform.ap_cpu_0.gdb_port`,
  helper default `12341`. The same port is used with TF-A, OP-TEE, U-Boot, and
  Linux symbol scripts; the sampled execution level determines which script
  resolves symbols.
- SCP-Firmware: `gdb/scp-firmware-symbols.gdb` resolves
  `rdaspen-si0-bl2.elf`, but the current `service-model` SCP strategy has no
  live SCP CPU GDB target.

Tooling and symbols were available in the current workspace:

- `gdb` and `gdb-multiarch` are installed.
- `tools/qbox/build/platforms-vp` is non-stripped.
- TF-M, SCP-Firmware, TF-A, OP-TEE, U-Boot, Linux `vmlinux`, and SI CL1 Zephyr
  symbol paths are recorded in each bundle's `progress-report.md`.

Storage-unsafe comparison command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
timeout 160s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-all-debug-20260525-v1 \
  --launch \
  --sample-only \
  --sample-delay 105 \
  --runner-timeout 122 \
  --port-timeout 10 \
  --gdb-timeout 6 \
  --host-sample \
  --host-sample-seconds 3 \
  --ignore-fail-patterns \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

With `QBOX_RDASPEN_BOOT_FLASH_DMI=true`, the current run reproduces the known
storage-DMI problem rather than the current boot-progress point:

```text
Creating an empty ITS flash layout.
Partition initialization FAILED in 0x31047cc5
```

The focused partition panic trace identifies the failing TF-M partition:

```text
TRACE psa_panic entry pc=0x31040350 lr=0x310407e1
sp = 0x310056b0 <tfm_sp_its_stack+1712>
pid = 0x101
entry = 0x31047cc5
```

`pid=0x101` is `TFM_SP_ITS`. The ITS init trace narrows the failure to storage
erase/layout creation:

```text
tfm_its_init()
its_flash_fs_prepare() -> -132 / PSA_ERROR_GENERIC_ERROR
its_flash_fs_wipe_all() status check -> -146 / PSA_ERROR_STORAGE_FAILURE
psa_panic()
```

Storage-safe command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
timeout 160s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-storage-safe-20260525-v1 \
  --launch \
  --sample-only \
  --sample-delay 105 \
  --runner-timeout 122 \
  --port-timeout 10 \
  --gdb-timeout 6 \
  --host-sample \
  --host-sample-seconds 3 \
  --ignore-fail-patterns \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

This is the useful short progress configuration. The 105-second sample shows:

- TF-M/RSE is in the runtime wait path:
  `__tfm_arch_thread_fn_call_veneer()` on `idle_sp_stack`.
- RSE logs include the FVP-comparable marker
  `SCMI Comms subscribed to power state notifications`.
- AP has progressed past BL31 primary and secondary PFDI checks into OP-TEE
  secure-world initialization and Secure Partition loading.
- QBox host GDB wrapper captured `sc_start()`, RPC, QEMU iothread/call_rcu,
  worker, and AP CPU TCG threads.
- SCP-Firmware remains symbol-only because no live SCP CPU exists in
  `service-model`.

Linux-tail command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
timeout 210s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-storage-safe-linux-tail-20260525-v1 \
  --launch \
  --sample-only \
  --sample-delay 145 \
  --runner-timeout 165 \
  --port-timeout 10 \
  --gdb-timeout 8 \
  --ignore-fail-patterns \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

At 145 seconds, the primary console has reached U-Boot and the AP GDB sample is
still before Linux kernel entry:

```text
U-Boot 2026.01-rc4 ... arm_fvp
Model: RD-Aspen
Net: eth0: virtio-net#0
EFI: MM partition ID 0x8006
```

The AP GDB target reports CPU#0 at `pc=0x400a0c90`, with secondary CPUs halted
at `0xf1d0`. `linux-ap.gdb` can attach to the AP port, but the sampled PC is
not in Linux `vmlinux` yet. The secure console is in the OP-TEE / trusted
services handoff around SE Proxy, SMM Gateway, and EFI MM communication, with:

```text
E/SEPROXY: psa_fwu_query:62 failed to psa_call: -135
E/SMMGW: open_session:90 sp_msg_send_direct_req(): error -4
EFI: MM partition ID 0x8006
```

Current short-timeout conclusion:

- QBox host GDB, TF-M/RSE GDB, AP GDB, Linux symbol scripts, SCP-Firmware
  symbol scripts, and SI CL1 Zephyr symbol scripts are generated and usable.
- Use `QBOX_RDASPEN_BOOT_FLASH_DMI=false` for storage-safe progress probes.
- With storage-safe settings, RSE runtime reaches SCMI subscription and
  measured-boot markers, AP reaches U-Boot/EFI MM, and Linux has not started in
  the 145-second short GDB sample.
- With boot-flash DMI enabled, the run stops earlier in TF-M ITS with
  `PSA_ERROR_STORAGE_FAILURE`; keep that path only for boot-flash DMI
  debugging.

## 2026-05-25 Login Keepalive All-Target Probe

Artifact:
`build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1/`

Command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
QBOX_RDASPEN_MHU_TRACE=true \
QBOX_RDASPEN_MHU_TRACE_LIMIT=16000 \
timeout 340s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-login-keepalive-all-targets-20260525-v1 \
  --launch \
  --sample-only \
  --sample-delay 220 \
  --runner-timeout 260 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --host-sample \
  --host-sample-seconds 2 \
  --post-login-probe \
  --keep-running-after-pass \
  --copy-writable-flash \
  --ignore-fail-patterns \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- The generated bundle includes QBox host, TF-M/RSE, AP TF-A BL2/BL31,
  AP OP-TEE, AP U-Boot, Linux/AP, TS SE-Proxy/SMM Gateway, SCP-Firmware, and
  SI CL1 Zephyr symbol/source scripts.
- `probes/linux-later.txt` resolves CPU0 to Linux `d_alloc_parallel+336` and
  CPUs 1-3 to `cpu_do_idle()` through the AP QEMU GDB target.
- `probes/tfm-s-later.txt` resolves RSE runtime to
  `__tfm_arch_thread_fn_call_veneer()` -> `psa_wait_thread_fn_call()`.
- `probes/ap-secure-services-later.txt` loads the per-run SE-Proxy and SMM
  Gateway bases; at this late sample the AP is already executing Linux, so the
  secure-partition view intentionally reports the Linux PC.
- `probes/scp-symbols.txt` loads `rdaspen-si0-bl2.elf` and source maps, but
  live SCP CPU stepping is still unavailable in `scp-strategy=service-model`.
- QBox host was sampled by launching `platforms-vp` under GDB. The host log
  records SystemC `SC_START`, QEMU iothread/call_rcu threads,
  `char_backend_file` polling, and AP CPU TCG threads without changing host
  `ptrace_scope`.
- The run's primary console completed the FIFO post-login probe:
  `systemctl is-system-running` returned `running`, `systemctl --failed`
  listed zero failed units, and `/proc/interrupts` showed GICv3, PL011,
  SMMUv3, virtio, RTC, arch timer, and MHU interrupt lines.

## 2026-05-25 Short All-Debug Recheck

Artifact:
`build/qbox-fvp-rd-aspen/gdb-all-debug-short-20260525-v1/`

Command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
timeout 120s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --ignore-fail-patterns \
  --runner-timeout 80 \
  --port-timeout 5 \
  --gdb-timeout 5 \
  --sample-delay 45 \
  --host-sample \
  --host-sample-seconds 2 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-all-debug-short-20260525-v1 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- RSE/TF-M GDB port `12340` and AP/Linux GDB port `12341` opened.
- `tfm_later_probe_rc`, `tfm_s_later_probe_rc`, `linux_later_probe_rc`,
  AP TF-A/OP-TEE/U-Boot probes, SCP-Firmware symbol probe, and SI CL1 Zephyr
  symbol probe all returned 0.
- QBox host GDB captured a `platforms-vp` thread/backtrace sample through the
  host-GDB launch path; `host_gdb_sample_rc` is 1 because the helper interrupts
  and kills the bounded sample, while `host_gdb_sample_backtrace_captured=true`
  confirms the requested backtrace was recorded.
- TF-M/RSE sampled in TF-M BL2 `nor_cfi_reg_read()` from the CFI flash driver
  while processing AP BL2 image validation. The RSE UART log had reached SI
  CL1 and SI CL0 load, SI ATU programming, RSE-to-SCP SCMI initialization, and
  AP BL2 primary/secondary slot reporting.
- AP CPU0 was still at TF-A BL2 entry PC `0x82000`; Linux symbols attach to
  the AP GDB target, but Linux had not started in this 45-second sample.
- SCP-Firmware remains symbol/source-only in the current
  `scp-strategy=service-model` path. `gdb/scp-firmware-symbols.gdb` loads
  `rdaspen-si0-bl2.elf` and resolves entry `0x120000000`; live SCP stepping
  requires replacing or augmenting the service model with an executable SCP CPU
  target.

## 2026-05-25 FWU/PS Trace And Host Sample Refresh

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-t061-fwu-query-trace-20260525-v4/`
- `build/qbox-fvp-rd-aspen/gdb-t061-host-sample-20260525-v1/`

FWU/PS trace command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
timeout 250s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --tfm-fwu-query-trace \
  --secure-service-probe \
  --secure-service-probe-timeout 5 \
  --copy-writable-flash \
  --ignore-fail-patterns \
  --runner-timeout 190 \
  --trace-timeout 120 \
  --port-timeout 6 \
  --gdb-timeout 5 \
  --sample-delay 2 \
  --rse-port 12368 \
  --ap-port 12369 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-t061-fwu-query-trace-20260525-v4 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- RSE/TF-M and AP/Linux GDB ports opened on `12368` and `12369`.
- `probes/tfm-fwu-query-trace-gdb.log` hit `fwu_bootloader_init` at
  `pc=0x31044f90`; the longer FWU query breakpoints did not fire before the
  120-second trace cap.
- `probes/tfm-s-later.txt` sampled TF-M/RSE inside the ITS flash path:
  `tfm_its_remove()` -> `its_flash_fs_delete_idx()` ->
  `its_flash_fs_dblock_compact_block()` ->
  `cfi_strataflashj3_program()` -> `nor_send_cmd_byte()`.
- `probes/ap-secure-services-later.txt` sampled SE-Proxy waiting in
  `secure_storage_ipc_set()` for a TF-M Protected Storage SET response. The
  decoded PSA call uses handle `0x40000101` and type `1001`.
- `mhuv3-analysis.txt` records AP secure-service channel-1 requests/responses
  `13/12`, paired `12`, missing `1`; the single missing request is the
  in-flight `0x80060d01` at the bounded sample point.
- Secure-console logs still show `psa_fwu_query` returning `-135` and later
  `secure_storage_ipc_remove` returning `-140`; secure services are therefore
  still a fidelity gap, not a passed validation.

Host sample command:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-delay 25 \
  --host-sample \
  --host-sample-seconds 2 \
  --ignore-fail-patterns \
  --runner-timeout 60 \
  --port-timeout 6 \
  --gdb-timeout 5 \
  --rse-port 12370 \
  --ap-port 12371 \
  --out-dir build/qbox-fvp-rd-aspen/gdb-t061-host-sample-20260525-v1 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- The host-GDB launch path captured a `platforms-vp` backtrace; the helper
  reports `host_gdb_sample_backtrace_captured: True`.
- `host-gdb-run/qbox-platform.log` records `SystemC : SC_START`,
  `sc_core::sc_start()`, RPC server/client threads, QEMU iothread/call_rcu
  threads, and AP CPU TCG threads.
- Direct host attach still fails with `ptrace: Inappropriate ioctl for device`;
  for repeatable QBox host inspection, launch under GDB with `--host-sample`.

Current conclusion: the requested GDB environment is now usable for QBox host,
TF-M/RSE, AP firmware/Linux, and Trusted Services secure-partition sampling
with short file-backed runs. SCP-Firmware remains symbol/source-only in the
current service-model configuration because there is no live SCP CPU GDB
target yet.

## 2026-05-25 After MHU Pair Fix

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-t061-sfcp-atu-trace-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-t061-after-mhu-pair-fix-20260525-v1/`
- `build/qbox-fvp-rd-aspen/rse-t061-mhu-pair-fix-20260525-v1/`

The SFCP/FWU trace showed the first FWU query failing before ATU allocation:
`sfcp_protocol_pointer_access_deserialize_msg()` saw `msg_len=0x39` and
returned `-135`. MHU trace showed the cause was pair cross-talk from an
unmatched named AP-SI/PFDI PBX into the AP-to-RSE pair. The MHU model now
requires an exact peer match for non-empty pair names.

Post-fix command:

```bash
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
QBOX_RDASPEN_MHU_TRACE=true \
QBOX_RDASPEN_MHU_TRACE_LIMIT=8000 \
timeout 210s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --out-dir build/qbox-fvp-rd-aspen/gdb-t061-after-mhu-pair-fix-20260525-v1 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic \
  --rse-port 12382 \
  --ap-port 12383 \
  --runner-timeout 170 \
  --port-timeout 12 \
  --gdb-timeout 8 \
  --sample-delay 120 \
  --copy-writable-flash \
  --ignore-fail-patterns
```

Result:

- RSE/TF-M GDB port `12382` and AP/Linux GDB port `12383` opened.
- TF-M, AP/Linux, AP TF-A BL2/BL31, AP OP-TEE, AP U-Boot,
  SCP-Firmware symbol, and SI CL1 Zephyr symbol probes returned 0.
- SCP-Firmware remains symbol/source-only with `scp-strategy=service-model`;
  no live SCP CPU target is instantiated yet.
- The previous secure-console `psa_fwu_query: -135` failure disappears in the
  post-fix runtime.
- TF-M/RSE now samples in the ITS flash delete path:
  `tfm_its_remove()` -> `its_flash_fs_file_delete()` ->
  `cfi_strataflashj3_erase()` -> `nor_send_cmd_byte()`.
- AP SE-Proxy samples in `secure_storage_ipc_set(uid=8, data_length=156)`,
  waiting in `mhu_v3_x_doorbell_read()` for an RSE response.
- The generated MHU analysis records AP secure-service requests/responses
  `17/16`, paired `16`, missing `1`; the missing transaction `0x80061101` is
  the in-flight request truncated by the bounded timeout.

Current conclusion: GDB can now inspect QBox host, TF-M/RSE, AP
firmware/Linux, and Trusted Services state at the current secure-service
blocker. The blocker moved past the FWU-query deserialization failure and is
now the later secure-storage exchange between AP SE-Proxy and TF-M ITS/PS.

## 2026-05-25 Marker-Gated Secure Variable Samples

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-postdelay-20260525-v1/`

The first marker-gated run waited for U-Boot to print
`Error: "db" not defined`, then sampled TF-M/RSE, AP firmware/Linux,
Trusted Services secure partitions, SCP-Firmware symbols, and SI CL1 Zephyr
symbols:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
QBOX_RDASPEN_MHU_TRACE=true \
QBOX_RDASPEN_MHU_TRACE_LIMIT=36000 \
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --out-dir build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-20260525-v1 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic \
  --rse-port 12388 \
  --ap-port 12389 \
  --runner-timeout 470 \
  --port-timeout 12 \
  --gdb-timeout 15 \
  --sample-delay 420 \
  --sample-marker 'Error: "db" not defined' \
  --copy-writable-flash \
  --ignore-fail-patterns
```

Result:

- The marker was found after 196.064 seconds.
- U-Boot reached authenticated variable enrollment: PK and KEK succeeded, then
  the `db` variable was not defined yet and the `db` payload was read.
- TF-M/RSE sampled in the SFCP pointer-access path:
  `comms_atu_alloc_region()` -> `setup_region_for_host_buf()` ->
  `atu_rse_map_addr_automatically()` -> `atu_rse_set_bus_attributes()`.
- AP SE-Proxy sampled in `secure_storage_ipc_remove()` with PSA call type
  `1004`, waiting in `mhu_v3_x_doorbell_read()` for the RSE response.
- Linux symbols attached through the AP GDB target, but the AP CPU was still
  executing secure-partition code, so Linux had not started in this sample.
- SCP-Firmware and SI CL1 Zephyr symbols loaded; live SCP stepping remains
  unavailable with `scp-strategy=service-model`.
- MHU analysis paired 104 of 105 AP secure-service channel-1 requests; the
  only missing request, `0x80066901`, was the in-flight transaction at the
  bounded sample point.

The second run exercised the new post-marker delay option:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
QBOX_RDASPEN_MHU_TRACE=true \
QBOX_RDASPEN_MHU_TRACE_LIMIT=42000 \
timeout 400s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --out-dir build/qbox-fvp-rd-aspen/gdb-t061-db-enroll-marker-postdelay-20260525-v1 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic \
  --rse-port 12390 \
  --ap-port 12391 \
  --runner-timeout 330 \
  --port-timeout 10 \
  --gdb-timeout 10 \
  --sample-delay 300 \
  --sample-marker 'Error: "db" not defined' \
  --sample-marker-post-delay 25 \
  --copy-writable-flash \
  --ignore-fail-patterns
```

Result:

- The `db` marker was not reached before the 300-second sample cap in this
  run; the primary UART was at U-Boot `FWU: System booting in Regular State`.
- AP SE-Proxy was still waiting in `mhu_v3_x_doorbell_read()`; AP firmware,
  OP-TEE, U-Boot, SCP-Firmware, and SI CL1 symbol probes attached.
- MHU analysis paired 69 of 70 AP secure-service channel-1 requests; the only
  missing request, `0x80064601`, was the in-flight transaction at the bounded
  sample point.
- TF-M/RSE GDB probes timed out at the 10-second per-probe cap in this later
  run, so use the first marker run for the precise TF-M/RSE stack at the `db`
  enrollment point.

Current conclusion: the reusable GDB setup can inspect QBox host, TF-M/RSE,
AP secure partition and firmware symbols, AP/Linux target state, and
SCP-Firmware symbols from file-backed runs. The current secure-variable gap is
not basic AP-RSE doorbell routing; the bounded samples show in-flight
SE-Proxy/RSE secure-storage transactions around U-Boot variable enrollment.

## 2026-05-25 FWU Prelogin Short Sample

Artifacts:

- `build/qbox-fvp-rd-aspen/rse-t073-fwu-capsule-probe-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-fwu-prelogin-short-20260525-v1/`

The runtime helper now has a file-backed FWU probe:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_RSE_LOCAL_CRYPTO=true \
QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --timeout 480 \
  --fwu-probe \
  --ignore-fail-patterns \
  --out-dir build/qbox-fvp-rd-aspen/rse-t073-fwu-capsule-probe-<run-id> \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

The probe injects the documented capsule-on-disk Linux commands only after
the primary UART reaches the login prompt. The short 2026-05-25 run was
stopped after the logs stayed unchanged for roughly 180 seconds. It reached
RSE measured boot and AP secure firmware but not Linux login, so no capsule
copy or reboot was triggered. `result.json` records
`blocker=qbox_fwu_probe_incomplete`, `fwu_requested=true`,
`sent_login=false`, and `sent_probe=false`.

The matching GDB sample used short all-target probes:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
timeout 180s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-delay 80 \
  --runner-timeout 120 \
  --port-timeout 6 \
  --gdb-timeout 6 \
  --host-sample \
  --host-sample-seconds 2 \
  --ignore-fail-patterns \
  --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-prelogin-short-<run-id> \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- RSE/TF-M and AP/Linux GDB ports opened.
- TF-M runtime sampled at `__tfm_arch_thread_fn_call_veneer`.
- AP CPU0 sampled in TF-A BL31 `pfdi_cpu_self_test_result()` under
  `runtime_svc_init()`.
- OP-TEE symbol view sampled `fdt_get_property_namelen_()` while walking the
  secure DT.
- Linux symbols attached through the AP target, but the kernel had not
  started in this bounded sample.
- SCP-Firmware and SI CL1 symbols loaded; live SCP stepping remains unavailable
  while `scp-strategy=service-model` is active.

## 2026-05-25 Current All-Layer GDB Recheck

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-current-setup-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-current-short-20260525-v4/`
- `build/qbox-fvp-rd-aspen/gdb-linux-marker-20260525-v1/`

The setup-only helper generated source-mapped scripts for QBox host, TF-M/RSE,
AP TF-A/OP-TEE/U-Boot/Linux, SCP-Firmware, and SI CL1 Zephyr:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-setup-20260525-v1
```

The short live recheck used isolated runtime inputs to avoid collisions with
other QBox runs:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2223-:22 \
timeout 160s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-delay 65 \
  --runner-timeout 95 \
  --port-timeout 8 \
  --gdb-timeout 6 \
  --host-sample \
  --host-sample-seconds 2 \
  --copy-writable-flash \
  --ignore-fail-patterns \
  --out-dir build/qbox-fvp-rd-aspen/gdb-current-short-20260525-v4 \
  --rootfs build/qbox-fvp-rd-aspen/gdb-current-short-20260525-v3/rootfs-debug.wic
```

Result:

- RSE/TF-M GDB port `12340` and AP/Linux CPU0 GDB port `12341` opened.
- QBox host GDB captured a SystemC/QEMU thread sample through
  `gdb/qbox-host-sample.gdb`; the host trace includes `sc_core::sc_start()`,
  QEMU iothread, TCG CPU threads, and `QemuCpu::wait_for_work()`.
- TF-M/RSE sampled in TF-M storage code:
  `nor_send_cmd_byte()` -> `cfi_strataflashj3_erase()` ->
  `Driver_FLASH0_EraseSector()` -> `its_flash_nor_erase()` ->
  `tfm_its_init()`.
- AP CPU0 sampled before Linux in TF-A BL2 `mhu_v3_x_doorbell_read()`.
  CPU1-CPU3 were still halted at the BL2 entry/holding point.
- `linux-ap.gdb` attached successfully to the AP GDB target, but the sampled
  PC was still pre-Linux firmware code.
- SCP-Firmware symbols loaded with entry `0x120000000`; live SCP stepping is
  still unavailable while the platform uses `scp-strategy=service-model`.

The Linux-marker run waited for `Linux version` with a bounded 240-second cap:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2223-:22 \
timeout 330s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-marker 'Linux version' \
  --sample-marker-post-delay 3 \
  --sample-delay 240 \
  --runner-timeout 275 \
  --port-timeout 8 \
  --gdb-timeout 6 \
  --copy-writable-flash \
  --ignore-fail-patterns \
  --out-dir build/qbox-fvp-rd-aspen/gdb-linux-marker-20260525-v1 \
  --rootfs build/qbox-fvp-rd-aspen/gdb-current-short-20260525-v3/rootfs-debug.wic
```

Result:

- The marker was not reached in 240.076 seconds; `progress-report.md` records
  `sample_marker_found: False`.
- AP GDB was still attachable. The AP secure-service symbol view resolved CPU0
  to SE-Proxy `mhu_v3_x_doorbell_read()` with `channel=127`, matching the
  secure-storage transaction wait visible in the secure console.
- The Linux symbol script attached, but the PC was still in secure partition
  address space (`0x4006bc90`), so this run proves the Linux debug target
  wiring but not Linux kernel execution.
- TF-M GDB attach timed out at the 6-second per-probe cap in this later state.
- SCP-Firmware and SI CL1 symbol-only probes still returned 0.

Current conclusion: the GDB environment is reusable and file-backed for QBox
host, TF-M/RSE, AP firmware/Linux target state, AP secure-service symbol state,
SCP-Firmware symbols, and SI CL1 symbols. The current 240-second Linux-marker
run is blocked before Linux by secure-world U-Boot/SE-Proxy storage traffic,
not by missing GDB wiring.

## 2026-05-25 FWU Start/Staging GDB Trace

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-fwu-start-trace-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260525-v1/`

The helper now emits `gdb/tfm-fwu-start-trace.gdb` and accepts
`--tfm-fwu-start-trace`. The trace script breaks on `tfm_fwu_start()`,
`fwu_bootloader_get_image_info()`, `fwu_bootloader_staging_area_init()`,
`flash_area_open()`, flash erase/write entry points when symbols are present,
`Driver_FLASH0_EraseSector()`, `Driver_FLASH1_EraseSector()`, and
`psa_panic()`.

The FWU run used a bounded trace around the capsule-copy and reboot path:

```bash
QBOX_RDASPEN_MHU_TRACE=false \
QBOX_RDASPEN_NETDEV=type=user,hostfwd=tcp::2236-:22 \
timeout 760s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-fwu-start-trace-20260525-v1 \
  --launch \
  --sample-only \
  --fwu-probe \
  --keep-running-after-pass \
  --ignore-fail-patterns \
  --rse-port 12630 \
  --ap-port 12631 \
  --runner-timeout 640 \
  --trace-timeout 620 \
  --gdb-timeout 6 \
  --port-timeout 8 \
  --sample-delay 1 \
  --tfm-fwu-start-trace
```

Result:

- RSE/TF-M and AP/Linux GDB ports opened and all later GDB probes returned 0.
- Linux reached login, the post-login probe completed, the FWU probe mounted
  `/boot` and `/mnt`, copied `fw.cap` into `EFI/UpdateCapsule`, emitted
  `__QBOX_FWU_REBOOT_REQUESTED__`, and reached `systemd-shutdown[1]:
  Rebooting.`.
- The trace did not hit `tfm_fwu_start()` within the 620-second trace window.
  `probes/tfm-fwu-start-trace.txt` records `timed_out_after=620s`, and
  `probes/tfm-fwu-start-trace-gdb.log` shows the FWU/staging breakpoints were
  installed.
- No `FWU: Updating`, `FWU_DENIED`, `Trial State`, `FIP_B`, or RSE
  `Attempting to boot image 1` marker appears in this run before the helper
  terminates the platform.
- The latest TF-M sample resolves to
  `__tfm_arch_thread_fn_call_veneer()` below `psa_wait_thread_fn_call()`,
  while the Linux sample resolves to `cpu_do_idle()`, confirming both live GDB
  targets were attachable after the first Linux boot.
- SCP-Firmware remains symbol/source-only in `scp-strategy=service-model`;
  `probes/scp-symbols.txt` loads `rdaspen-si0-bl2.elf` and resolves entry
  `0x120000000`.

A separate short host-GDB sample was taken to prove QBox/SystemC host
debugging without waiting for the full FWU flow:

```bash
timeout 150s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-qbox-host-sample-20260525-v1 \
  --launch \
  --sample-only \
  --sample-delay 1 \
  --host-sample \
  --host-sample-seconds 2 \
  --runner-timeout 35 \
  --gdb-timeout 5 \
  --port-timeout 5 \
  --rse-port 12640 \
  --ap-port 12641 \
  --ignore-fail-patterns
```

Result:

- `progress-report.md` records `host_gdb_sample_backtrace_captured: True`.
- The QBox host backtrace includes `sc_core::sc_start()`, `sc_main()`, the
  QEMU iothread, QEMU call_rcu threads, four AP `CPU */TCG` threads, and
  `QemuCpu::wait_for_work()`.
- The short sample also proves early TF-M, AP, SCP symbol, and SI CL1 symbol
  probe wiring: RSE sampled in BL1_1 `nor_cfi_reg_read()`, AP CPU0 sampled at
  TF-A BL2 `bl2_entrypoint`, and SCP/SI symbol probes returned 0.

Current conclusion: all requested GDB entry points are prepared and exercised
where the current QBox model exposes a CPU. QBox host, TF-M/RSE, AP firmware,
and Linux share file-backed scripts and proof logs. SCP-Firmware has source
and symbol inspection only until the current `service-model` SCP endpoint is
replaced or augmented with a live SCP CPU model and `gdb_port`.

## 2026-05-25 Short-Timeout Current Progress

The helper now supports pass-through writable image paths for replaying exact
flash/OTP/capsule inputs and `--trace-after-sample` for attaching TF-M FWU
breakpoint scripts only after a marker is reached. Use marker-gated samples
with short caps instead of waiting for a full FWU run:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_MHU_TRACE=false \
timeout 300s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-marker "Booting bootflow 'virtio-blk#1.bootdev.part_1' with script" \
  --sample-delay 220 \
  --runner-timeout 260 \
  --gdb-timeout 5 \
  --port-timeout 6 \
  --copy-writable-flash \
  --ignore-fail-patterns
```

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-efi-mm-ap-flash-strata-20260525-v1/`
- `build/qbox-fvp-rd-aspen/login-ap-flash-strata-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-bootflow-ap-flash-strata-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-qbox-host-current-20260525-v1/`

Result:

- `gdb-efi-mm-ap-flash-strata-20260525-v1` reached
  `EFI: MM partition ID` in 131.540 seconds. AP CPU0 resolved through the
  Trusted Services overlay to SE-Proxy
  `secure_storage_ipc_set()` waiting in `mhu_v3_x_doorbell_read()`. RSE/TF-M
  resolved to TF-M ITS/PS flash writes through `Driver_FLASH0_ProgramData()`.
- The non-GDB runtime `login-ap-flash-strata-20260525-v1` reached
  `FWU: ABI version 1.0 detected`, U-Boot key enrollment, and then timed out
  before Linux login at the 240-second cap.
- `gdb-bootflow-ap-flash-strata-20260525-v1` did not reach the later bootflow
  marker by 220 seconds. The sampled state was still SE-Proxy secure-storage
  set for dbx key enrollment, with `data_length=2391`, while RSE/TF-M was in
  `Driver_FLASH0_EraseSector()` via the CFI byte-program erase loop.
- `gdb-qbox-host-current-20260525-v1` captured QBox host GDB evidence with
  `host_gdb_sample_backtrace_captured: True`; the host view includes
  SystemC `SC_START`, QEMU iothreads, AP TCG CPU threads, and
  `QemuCpu::wait_for_work()`.
- A follow-up non-GDB run,
  `build/qbox-fvp-rd-aspen/rse-t064-db-nogdb-20260525-v1/`, proves the same
  secure-variable path is not functionally stuck: PK, KEK, `db`, and `dbx`
  enrollment all complete, and the primary console reaches
  `FWU: ExitBootServices: Booting in regular state` before the short Linux
  login cap expires.
- A file-backed FVP comparison with verbose runfvp output,
  `build/fvp-boot-logs/critical-verbose-rse-blocker-20260525-v1/`, reaches
  the RSE runtime, SCP initialization, AP secure console output, Linux
  kernel driver probes, rootfs mount, and systemd startup within an 80-second
  critical-marker cap. It does not reach the Linux login marker before that
  cap, but it confirms the FVP path is past the secure-variable and TF-M
  runtime stages where QBox GDB sampling is slow.

Current conclusion: the short-timeout GDB environment can inspect QBox host,
TF-M/RSE, AP firmware/Linux target state, Trusted Services overlays,
SCP-Firmware symbols, and SI CL1 symbols. With fresh writable flash copies,
marker-gated GDB samples can catch in-flight SE-Proxy secure-storage requests
while TF-M ITS/PS performs Strata CFI byte-program/erase traffic on
`Driver_FLASH0`. That is now classified as a source-level sampling and
flash-traffic latency issue, not proof that U-Boot secure-variable enrollment
is functionally blocked, because the non-GDB T064 run completes PK/KEK/db/dbx
enrollment and reaches `ExitBootServices`.

## 2026-05-25 User-Requested All-Target GDB Recheck

The user requested a fresh GDB-backed progress check with short timeouts for
QBox, TF-M, SCP-Firmware, and Linux. The current helper and active
`scp-strategy=service-model` path were reused:

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=false \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
timeout 105s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --launch \
  --sample-only \
  --sample-delay 35 \
  --runner-timeout 55 \
  --port-timeout 5 \
  --gdb-timeout 5 \
  --host-sample \
  --host-sample-seconds 2 \
  --ignore-fail-patterns \
  --out-dir build/qbox-fvp-rd-aspen/gdb-user-request-all-targets-20260525-v1 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-user-request-all-targets-20260525-v1/`

Result:

- RSE/TF-M GDB port `12340` and AP/Linux CPU0 GDB port `12341` both opened.
- QBox host GDB captured a foreground `platforms-vp` thread/backtrace sample.
  The host view includes `sc_main()`, `sc_core::sc_start()`,
  QEMU `qemu-iothread`, AP `CPU */TCG` threads, and
  `QemuCpu::wait_for_work()`.
- At the 35-second sample, RSE/TF-M is in BL2 image loading:
  `nor_cfi_reg_read()` -> `cfi_strataflashj3_read()` ->
  `Driver_FLASH0_ReadData()` ->
  `boot_decrypt_and_copy_image_to_sram()`.
- The AP/Linux GDB script attaches successfully, but all AP CPU threads are
  still at `0x82000`; the TF-A BL2 symbol view resolves CPU0 to
  `bl2_entrypoint()`. Linux has not started in this short sample.
- SCP-Firmware symbol/source loading works for
  `rdaspen-si0-bl2.elf`, entry `0x120000000`; no live SCP CPU GDB port is
  instantiated under the current service-model path.

## 2026-05-25 EFI Marker After DMI Invalidation Recheck

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-efi-after-dmi-inval-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-efi-after-dmi-inval-20260525-v1/mhuv3-trace-summary.txt`

The follow-up run used the same marker-gated GDB setup after tightening the
Strata flash DMI invalidation behavior. The change invalidates an active
read-only DMI grant only when a CFI command changes flash command state, and
does not broadcast another full-device invalidation for the following program
data byte once DMI has already been revoked.

```bash
QBOX_RDASPEN_ENABLE_AP_CPUS=true \
QBOX_RDASPEN_ATU_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI=true \
QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES='0x7000:0x260000' \
QBOX_RDASPEN_HOST_MEMORY_DMI=true \
QBOX_RDASPEN_AP_FLASH_DMI_RANGES='0x7000:0x240000' \
QBOX_RDASPEN_RSE_DTCM_DMI=true \
QBOX_RDASPEN_RSE_ITCM_DMI=true \
QBOX_RDASPEN_RSE_VM_DMI=true \
QBOX_RDASPEN_MHU_TRACE=true \
QBOX_RDASPEN_MHU_TRACE_LIMIT=6000 \
timeout 280s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-efi-after-dmi-inval-20260525-v1 \
  --launch \
  --sample-only \
  --sample-marker 'EFI: MM partition ID' \
  --sample-marker-post-delay 15 \
  --sample-delay 170 \
  --runner-timeout 210 \
  --trace-timeout 80 \
  --gdb-timeout 6 \
  --port-timeout 8 \
  --host-sample \
  --host-sample-seconds 2 \
  --ignore-fail-patterns \
  --copy-writable-flash \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic
```

Result:

- The `EFI: MM partition ID` marker was reached after 113.028 seconds. This is
  not an improvement over the prior 101.526-second marker run and should be
  treated as run-to-run noise rather than a solved bottleneck.
- RSE/TF-M GDB port `12340` and AP/Linux CPU0 GDB port `12341` opened; the
  QBox host GDB sample captured `platforms-vp` thread/backtrace state.
- AP CPU0 still sampled in Trusted Services SE-Proxy
  `secure_storage_ipc_remove()` -> `__psa_call(type=1004)` ->
  `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read()`.
- RSE/TF-M still sampled in `tfm_its_remove()` below ITS flash filesystem
  delete/compact, programming Strata flash through
  `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()` ->
  `nor_send_cmd_byte()`.
- The AP/Linux GDB script attaches and exposes the AP CPU threads, but the
  sampled PC remains in secure-service code. Linux has not started at this
  EFI marker.
- SCP-Firmware symbols load for `rdaspen-si0-bl2.elf`, entry `0x120000000`;
  live SCP stepping remains unavailable under `scp-strategy=service-model`.
- MHU trace analysis reports 15 AP-to-RSE secure doorbell requests on channel
  1 with prefix `0x800`, 14 matched RSE-to-AP responses, and one in-flight
  missing response at the sample point. Several matched responses take around
  3.0 to 3.9 simulated seconds, matching the TF-M ITS flash writeback GDB
  stack.

FVP comparison:

- Arm Zena CSS release notes document the first-boot
  `secure_storage_ipc_remove: ... -140` messages as expected
  `PSA_ERROR_DOES_NOT_EXIST` behavior while SMM Gateway removes variable
  indexes before creating them.
- The file-backed FVP comparison in
  `build/fvp-boot-logs/critical-verbose-rse-blocker-20260525-v1/` reaches
  `EFI: MM partition ID`, the same `-140` secure-storage messages,
  `Linux version`, rootfs mount, and systemd startup within the short
  critical-marker window. Therefore the current QBox pause is not the expected
  first-boot `-140` condition alone; it is the much slower QBox/RSE TF-M ITS
  flash writeback path.

Current conclusion: the GDB environment now gives a repeatable all-layer view:
QBox host, RSE/TF-M, AP firmware/Linux target attachment, Trusted Services
overlays, SCP-Firmware symbols, and MHU trace pairing. The Strata DMI
invalidation cleanup is correct and tested, but it does not materially move
the EFI-marker bottleneck. The next implementation target is reducing or
batching the TF-M ITS/PS Strata CFI byte-program/delete/compact path without
breaking CFI command semantics or flash persistence evidence.

## 2026-05-25 SE-Proxy Panic Decode

Artifacts:

- `build/qbox-fvp-rd-aspen/rse-t065-secure-service-probe-20260525-v1/`
- `build/fvp-boot-logs/rse-secure-service-probe-20260525-v1/`
- `build/fvp-boot-logs/rse-secure-service-ps-probe-20260525-v1/`

The post-login secure-service probe reaches Linux, loads the expected drivers,
and then fails the PSA user-space tests with bounded timeouts:
`psa-iat-api-test`, `psa-its-api-test`, and `psa-ps-api-test` all return
`124` after `libpsats` reports `Failed to open rpc session`.

The secure console shows why the later Linux-side RPC open fails. SE-Proxy is
loaded at `0x40031000`, then OP-TEE reports a user-mode data abort at
`0x400473d8` with `x0 = 0`, followed by `SP panicked with code 0xdeadbeef`.
Decoding the SP stack against
`build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/ts-sp-se-proxy/1.3.0+git/build/se-proxy_46bb39d1-b4d9-45b5-88ff-040027dab249`
maps the fault to `update_agent_discover()`:

```text
0x400473d8 - 0x40031000 = 0x163d8
0x163d8: update_agent_discover
trusted-services/components/service/fwu/common/update_agent_interface.c:12
```

The confirming GDB check was:

```bash
gdb-multiarch -batch \
  -ex 'set pagination off' \
  -ex 'set debuginfod enabled off' \
  -ex 'set substitute-path /usr/src/debug/ts-sp-se-proxy/1.3.0+git-r0/trusted-services /build/arm/arm-auto-solutions/build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/ts-sp-se-proxy/1.3.0+git/git/trusted-services' \
  -ex 'file /build/arm/arm-auto-solutions/build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/ts-sp-se-proxy/1.3.0+git/build/se-proxy_46bb39d1-b4d9-45b5-88ff-040027dab249' \
  -ex 'info line *0x163d8' \
  -ex 'info symbol 0x163d8' \
  -ex 'info line *0x16a4c' \
  -ex 'info symbol 0x16a4c' \
  -ex quit
```

It resolves:

- `0x163d8` to `update_agent_discover + 20`, line 12:
  `if (!update_agent->interface->discover)`.
- `0x16a4c` to `discover_handler + 72`, line 106:
  `update_agent_discover(this_instance->update_agent, &discovery_result)`.

This means `this_instance->update_agent` is null in the SE-Proxy FWU provider
when the FWU discovery request is serviced. After the panic, OP-TEE reports
`ffa_handle_sp_direct_req:942 SP is busy`, SMM Gateway calls return `-4`, and
normal-world PSA tests cannot open their RPC session.

FVP comparison matters here: the FVP secure console also prints first-boot
SE-Proxy secure-storage errors such as `-140`, `-133`, and `-135`, but it does
not panic. In the same FVP probe, `psa-iat-api-test` returns `0`,
`psa-its-api-test` returns `0`, and the PS suite progresses through test 409
under the bounded log window. Therefore the current QBox post-login
secure-service failure is not explained by the expected first-boot missing
UEFI variables alone; QBox is reaching a distinct SE-Proxy FWU discovery panic
before the normal-world secure-service stack can operate reliably.

Current progression split:

- QBox host GDB: usable through the foreground host-GDB launch path; captures
  SystemC/QEMU threads and `QemuCpu::wait_for_work()` states.
- TF-M/RSE GDB: usable on port `12340`; at the EFI marker the sampled RSE is
  still in ITS delete/compact Strata flash writeback.
- AP/Linux GDB: usable on port `12341`; Linux reaches login in non-GDB
  runtime, but marker-gated GDB samples before Linux remain in AP secure-world
  SE-Proxy calls.
- SCP-Firmware: symbol/source inspection works for `rdaspen-si0-bl2.elf`;
  live SCP stepping remains unavailable while `scp-strategy=service-model`
  does not instantiate a real SCP CPU GDB server.

## 2026-05-25 Rebuilt Short GDB Recheck

Artifact:

- `build/qbox-fvp-rd-aspen/gdb-efi-marker-current-rebuilt-20260525-v3/`

After rebuilding `platforms-vp` from the current QBox tree, the short
file-backed GDB run used:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-efi-marker-current-rebuilt-20260525-v3 \
  --launch \
  --runner-timeout 140 \
  --sample-delay 130 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --sample-only \
  --sample-marker 'EFI: MM partition ID' \
  --sample-marker-post-delay 1 \
  --ignore-fail-patterns
```

The marker was not reached in the 130 second sample window:

```text
sample_marker_found: False
sample_wait_seconds: 130.039
runner_returncode: -15
```

The generated GDB environment still covered every requested debug layer:

- QBox host: `gdb/qbox-host-run.gdb`, `gdb/qbox-host.gdb`, and
  `gdb/qbox-host-sample.gdb` were generated. The rebuilt
  `tools/qbox/build/platforms-vp` is not stripped, but `sc_main` has no line
  debug information in this build configuration.
- TF-M/RSE: port `12340` was live. The sample stopped in
  `cfi_strataflashj3_read()` from TF-M BL2 while `boot_load_image_to_sram()`
  was copying an image through `Driver_FLASH0_ReadData()`.
- AP firmware/Linux: port `12341` was live. All four AP CPUs still sampled at
  `0x82000`; with TF-A BL2 symbols this is `bl2_entrypoint`, so Linux had not
  started.
- SCP-Firmware: live SCP GDB was still unavailable with
  `scp-strategy=service-model`, but `scp-firmware-symbols.gdb` loaded
  `rdaspen-si0-bl2.elf` and reported entry `0x120000000`.

The run produced no primary or secure console output and no MHU trace file,
which is consistent with the system still being before AP/secure-service MHU
traffic. This current rebuilt artifact therefore supersedes older pre-rebuild
runtime samples for the immediate progress question: under short FVP-like
timeouts the current QBox run is still in RSE TF-M BL2 flash image loading
before AP firmware executes.

## 2026-05-25 Range-Limited Flash DMI GDB Recheck

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-current-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-linux-marker-full-dmi-current-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-range-dmi-setup-current-20260525-v1/`
- `build/qbox-fvp-rd-aspen/gdb-efi-marker-range-dmi-option-current-20260525-v1/`

The current rebuilt QBox binary was then rerun with the storage-safe fast path:

```bash
python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-current-20260525-v1 \
  --launch \
  --runner-timeout 160 \
  --sample-delay 140 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --sample-only \
  --sample-marker 'Linux version' \
  --sample-marker-post-delay 1 \
  --ignore-fail-patterns \
  --copy-writable-flash \
  --range-limited-flash-dmi \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic \
  --rse-port 12720 \
  --ap-port 12721
```

This path enables ATU DMI, host-memory DMI, RSE boot-flash DMI limited to
`0x7000:0x260000`, and AP flash DMI limited to `0x7000:0x240000`. It moved the
short run past the default non-DMI BL2 flash-copy bottleneck. The RSE log
reached SI CL1, SI CL0, AP BL2, RSE runtime chainload, measured boot through
`BL_33`, and the primary console reached U-Boot `EFI: MM partition ID 0x8006`.

The Linux marker was still not reached within the 140 second sample window:

```text
sample_marker_found: False
sample_wait_seconds: 140.043
```

At that point, AP CPU0 was inside SE-Proxy secure-storage set handling:

```text
secure_storage_ipc_set()
__psa_call(type=1001)
rse_comms_platform_invoke()
mhu_adapter_send()
mhu_send_data(size=60)
mhu_v3_x_doorbell_read(channel=127)
```

RSE/TF-M was concurrently handling the MHU2 receiver interrupt in the SFCP
receive path:

```text
CMU_MHU2_Receiver_Handler()
tfm_multi_core_hal_receive()
sfcp_interrupt_handler()
sfcp_hal_receive_message()
mhu_receive_message(total_message_size=60)
mhu_get_num_mhu_channels()
mhu_v3_x_get_num_channel_implemented()
```

The MHU trace analyzer reported 21 AP-to-RSE requests, 20 matched responses,
and one in-flight request at the sample point. This is forward progress, not a
dead MHU channel, but the remaining secure-storage operations are still too
slow compared with FVP. The FVP comparison logs reach the same U-Boot
enrollment sequence, then `Linux version` on the primary console.

The new `--range-limited-flash-dmi` option was also launched directly as a
short marker check. It reached `EFI: MM partition ID` after 99.030 seconds,
opened both RSE/AP GDB ports, and recorded the expected DMI ranges in
`debug-env.json`. This verifies the helper option, not only the equivalent
manual environment prefix.

The full-device boot-flash DMI negative control remains unsafe even after the
DMI invalidation cleanup. With `QBOX_RDASPEN_BOOT_FLASH_DMI=true` and no
`QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES`, RSE/TF-M prints
`Creating an empty ITS flash layout.` then `Partition initialization FAILED in
0x31047cc5`, and the GDB sample stops in `tfm_hal_system_halt()`. Therefore the
reusable GDB helper now has an explicit `--range-limited-flash-dmi` option
rather than enabling full-device DMI by default.

## 2026-05-25 Strata No-Op Writeback GDB Recheck

Artifact:

- `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-noop-current-20260525-v1/`

The Strata flash model now avoids writeback when byte-programming does not
change the flash array, and writes only the changed subrange when a multi-byte
program operation mutates data. This preserves NOR bit-clear semantics and the
RD-Aspen `program_ff_sets_bits` compatibility path, but avoids repeated backing
file writes during TF-M `0xff` program loops after a sector has already been
erased.

The focused validation commands were:

```bash
git -C tools/qbox diff --check -- \
  systemc-components/strata_flash_j3/include/strata_flash_j3.h \
  tests/components/strata_flash_j3/strata_flash_j3-tests.cc
luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua
python3 -m py_compile \
  scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/analyze_qbox_mhu_trace.py
timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8
timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure
timeout 180s cmake --build tools/qbox/build --target platforms-vp --parallel 8
```

All commands passed. `strata_flash_j3-tests` includes
`NoopProgramSkipsBackingFileWrite`, which programs `0xff` over an already
erased byte while the configured backing file is intentionally shorter than the
flash array. The test expects no backing-file range error, proving the no-op
program path no longer touches the backing file.

The short runtime check used the reusable range-limited DMI GDB path:

```bash
timeout 180s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-noop-current-20260525-v1 \
  --launch \
  --runner-timeout 145 \
  --sample-delay 125 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --sample-only \
  --sample-marker 'Linux version' \
  --sample-marker-post-delay 1 \
  --ignore-fail-patterns \
  --copy-writable-flash \
  --range-limited-flash-dmi \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic \
  --rse-port 12750 \
  --ap-port 12751
```

The primary console reached U-Boot `EFI: MM partition ID 0x8006`, but
`Linux version` was not reached within 125.036 seconds. The GDB sample shows
that the active pause remains secure-storage writeback:

```text
AP CPU0:
secure_storage_ipc_set()
__psa_call(type=1001)
rse_comms_platform_invoke()
mhu_v3_x_doorbell_read(channel=127)

RSE/TF-M:
tfm_its_remove()
its_flash_fs_file_delete()
its_flash_fs_delete_idx()
its_flash_fs_dblock_compact_block()
its_flash_fs_block_to_block_move()
its_flash_nor_write()
Driver_FLASH0_ProgramData()
cfi_strataflashj3_program()
nor_byte_program()
nor_send_cmd_byte()
```

`scripts/analyze_qbox_mhu_trace.py` generated
`mhu-summary.txt` and reported 21 AP-to-RSE channel-1 requests, 20 matched
responses, and one in-flight request at the sample. The analyzer returns
non-zero for this incomplete in-flight pair, but the latest matched responses
still complete, so the result remains slow secure-storage traffic rather than a
dead MHU route.

Current conclusion: the no-op backing-file optimization is valid and tested,
but the short GDB run still stops before Linux in the same RSE TF-M
ITS/secure-storage flash compaction path. The next performance/fidelity step
must reduce the number of firmware-visible byte-program transactions or model a
more faithful/faster Strata buffered-program path; backing-file write
suppression alone is not sufficient to reach Linux under the bounded sample.

## 2026-05-25 Strata Flash Stats And FVP Reference Recheck

Artifacts:

- `build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-flash-stats-20260525-v1/`
- `build/fvp-boot-logs/rd-aspen-verbose-short-20260525-v1/`

The GDB helper now supports `--flash-stats`, which configures the RSE/AP
`strata_flash_j3` instances to write periodic JSON counter snapshots into the
run directory. This keeps the all-target GDB workflow file-backed while adding
transaction counts for CFI commands, byte-program operations, compatibility
sector erases, and backing-file writeback.

Focused validation:

```bash
python3 -m py_compile scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py scripts/run_qbox_fvp_rd_aspen_rse.py scripts/analyze_qbox_mhu_trace.py
luac -p tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua
rg -n '[ \t]+$' \
  tools/qbox/systemc-components/strata_flash_j3/include/strata_flash_j3.h \
  tools/qbox/tests/components/strata_flash_j3/strata_flash_j3-tests.cc \
  tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua \
  scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py
git -C tools/qbox diff --check
timeout 120s cmake --build tools/qbox/build --target strata_flash_j3-tests --parallel 8
timeout 60s ctest --test-dir tools/qbox/build -R '^strata_flash_j3-tests$' --output-on-failure
timeout 180s cmake --build tools/qbox/build --target platforms-vp --parallel 8
```

The first `luac` pass briefly hit Lua's 200-local-variable limit after adding
three new local flash-stat settings. The fix follows the existing file pattern
for some platform knobs and exposes those settings as globals. The corrected
`luac -p` pass succeeds.

Runtime command:

```bash
timeout 180s python3 scripts/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-linux-marker-range-dmi-flash-stats-20260525-v1 \
  --launch \
  --runner-timeout 145 \
  --sample-delay 125 \
  --port-timeout 8 \
  --gdb-timeout 8 \
  --sample-only \
  --sample-marker 'Linux version' \
  --sample-marker-post-delay 1 \
  --ignore-fail-patterns \
  --copy-writable-flash \
  --range-limited-flash-dmi \
  --flash-stats \
  --flash-stats-interval 512 \
  --rootfs build/qbox-fvp-rd-aspen/rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic \
  --rse-port 12780 \
  --ap-port 12781
```

Result:

- RSE/AP GDB ports were live; SCP-Firmware symbols loaded, but the
  service-model SCP path still has no live SCP CPU GDB port.
- The primary console reached U-Boot `EFI: MM partition ID 0x8006`.
- `Linux version` was not reached within `125.037` seconds.
- AP CPU0 sampled in SE-Proxy
  `secure_storage_ipc_set()` -> `__psa_call(type=1001)` ->
  `rse_comms_platform_invoke()` -> `mhu_v3_x_doorbell_read(channel=127)`.
- RSE/TF-M sampled in ITS/PS flash writeback:
  `tfm_its_set()` -> `tfm_its_write_data_to_fs()` ->
  `its_flash_fs_block_to_block_move()` -> `its_flash_nor_write()` ->
  `Driver_FLASH0_ProgramData()` -> `cfi_strataflashj3_program()` ->
  `nor_byte_program()` -> `nor_poll_dws_byte()` -> `nor_cfi_reg_read()`.

The RSE Strata counter snapshot is the current quantitative bottleneck
evidence:

```text
read_accesses: 776455
write_accesses: 1480192
command_writes: 1233493
read_status_cmds: 493397
clear_status_cmds: 246699
word_program_cmds: 246699
program_ops: 246699
program_changed_bytes: 200425
program_noop_bytes: 46096
compat_ff_sector_erase_ops: 178
sector_erase_bytes: 729088
backing_write_ops: 200603
backing_write_bytes: 929513
```

The MHU trace analyzer produced `mhu-summary.txt`. It found 16 AP-to-RSE
channel-1 requests, 15 matched responses, and one in-flight request at the
sample. Several late matched responses are multi-second simulated-time
transactions, confirming slow secure-storage flash work rather than a dead MHU
route.

Fresh FVP reference command:

```bash
timeout 240s scripts/runfvp_log_boot.py \
  --runfvp-verbose \
  --timeout 180 \
  --require critical \
  --out-dir build/fvp-boot-logs/rd-aspen-verbose-short-20260525-v1
```

FVP did not reach the full login criterion before the 180-second cap, but it
did pass all non-primary critical consoles and reached Linux on the primary
console. The primary FVP log contains:

```text
U-Boot 2026.01-rc4
EFI: MM partition ID 0x8006
Booting Linux on physical CPU 0x0000000000
Linux version 6.18.5-rt3-yocto-preempt-rt
```

The FVP secure console shows the same expected first-boot SE-Proxy
`secure_storage_ipc_remove: ... -140` messages and then continues to secondary
CPU initialization and `tee_ta_close_session`. Therefore the current QBox gap is
not explained by the expected `-140` secure-storage messages. It is the
firmware-visible Strata CFI byte-program/status-poll transaction volume in the
RSE ITS/PS writeback window.
