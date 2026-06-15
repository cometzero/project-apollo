# Apollo AP 9.1.1 Memory Map QBox Gap Plan

## TL;DR
> Summary:      Bring the QBox Apollo AP-visible memory map closer to Arm Zena CSS programmer model section 9.1.1 without expanding into full NoC/CMN/PCIe/debug/memory-controller parity. The plan adds a static AP map coverage gate, migrates high DRAM to the 9.1.1 range, and implements the approved P1 AP register/model gaps with boot-backed evidence.
> Deliverables:
> - AP 9.1.1 static coverage audit that compares the documented AP map against QBox Lua/SystemC coverage.
> - High DRAM migration to the 9.1.1 range `0x08_8000_0000..0x0d_ffff_ffff` for both direct AP Linux and Apollo full-system QBox paths.
> - Explicit AP SID, AP secure timer frame, RGIC2LGIC message register, and APP subsystem FMU coverage.
> - Updated QBox Apollo hardware/map docs and coverage ledger entries.
> - Direct AP Linux and Apollo full-system runtime verification with generated evidence.
> Effort:       Large
> Risk:         Medium - address-map migrations can affect firmware/DT artifacts and AP boot handoff.

## Scope
### Must have
- Add or extend a repo-local audit script that treats `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:75` section 9.1.1 as the authoritative AP system memory map.
- Audit current QBox AP coverage from:
  - `tools/qbox/platforms/apollo/hw-block/rse.lua:418` AP base constants.
  - `tools/qbox/platforms/apollo/hw-block/rse.lua:1127` AP SRAM/DRAM/peripheral object ownership.
  - `tools/qbox/platforms/apollo/hw-block/rse.lua:1701` AP ATU/MHU/System Management Domain windows.
  - `tools/qbox/platforms/apollo/hw-block/ap_compute.lua:3` AP logical view rebinding.
  - `tools/qbox/platforms/apollo/hw-block/ros.lua:3` RoS modeled/unmodeled peripheral list.
- Migrate high DRAM from the current QBox placements:
  - Direct boot: `tools/qbox/platforms/apollo/hw-block/primary_compute.lua:82` `ram_1` at `0x200000000`.
  - Direct boot DTS: `tools/qbox/platforms/apollo/apollo-fvp-primary-compute.dts:69` high memory node at `<0x2 0x00000000 ...>`.
  - Full-system: `tools/qbox/platforms/apollo/hw-block/rse.lua:446` `HOST_AP_DRAM2_BASE = 0x20000000000`.
  to the 9.1.1 high DRAM base `0x880000000` (`0x08_8000_0000`) with a size that preserves the current QBox 2 GiB backing unless all local artifacts and DTS evidence already require a larger backed range.
- Reuse `host_scr` for the AP SID window at `0x1a4a0000..0x1a4affff`; it already models SID offsets and PID/CID registers in `tools/qbox/systemc-components/host_scr/include/host_scr.h:20`.
- Add AP secure generic timer frame coverage at `0x1a820000..0x1a82ffff`, bound into the AP logical view alongside the existing control and non-secure count frames.
- Add an explicit RGIC2LGIC_MESSREG window at `0x5fff0000..0x5fffffff`.
- Model the APP subsystem FMU region `0x1d000000..0x1defffff` enough for firmware-visible NI-710AE/FMUs and fault-injection smoke checks, using existing `zena_fmu` behavior as the register-model basis.
- Keep all implementation changes in QBox-owned scripts, Lua platform files, SystemC component/test files, and project documentation.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not implement full 9.1.1 parity for System NoC GPV, CMN GPV, AP cluster management, memory controller control, PCIe CTRL/PHY, debug memory map, AP Memory Expansion 1/2, or STM in this plan.
- Do not replace the existing QEMU-backed AP CPU/GIC/SMMU boot path unless a test proves the address-map change requires a narrow wiring update.
- Do not hide missing parity by broadening `gs_memory` catch-all windows over undocumented ranges. Any placeholder must name the exact 9.1.1 row, access behavior, and replacement debt.
- Do not edit Yocto metadata, local build scripts, firmware sources, or generated `build/` outputs except as runtime evidence created by verification commands.
- Do not overwrite unrelated untracked `.omc/` or `.omo/` state outside this plan/draft path.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: tests-after + Python static coverage audit + QBox component tests + direct/full runtime QA.
- QA policy: every todo has agent-executed scenarios and must write evidence under `.omo/evidence/task-<N>-ap-ap-system-memory-map-qbox-gap.<ext>`.
- Evidence: runtime and audit artifacts live under `build/qbox-apollo-fvp/ap-map-9-1-1/`; task-local summaries live under `.omo/evidence/`.
- Required static commands:
  - `python3 -m py_compile scripts/audit_qbox_apollo_fvp_full_coverage.py`
  - `python3 -m py_compile scripts/audit_qbox_apollo_ap_memory_map.py`
  - `git -C tools/qbox diff --check`
- Required QBox build/test commands:
  - `cmake --build tools/qbox/build --target host_scr-tests zena_fmu-tests host_gtimer-tests platforms-vp --parallel 8`
  - `ctest --test-dir tools/qbox/build -R '(host_scr|zena_fmu|host_gtimer)' --output-on-failure`
- Required direct AP Linux command:
  - `python3 scripts/run_qbox_apollo_fvp_linux.py --build-only --out-dir build/qbox-apollo-fvp/ap-map-9-1-1/direct-build`
  - `python3 scripts/run_qbox_apollo_fvp_linux.py --skip-build --timeout 300 --post-login-probe --out-dir build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime`
- Required full-system command:
  - `env QBOX_RDASPEN_NETDEV=type=user python3 scripts/run_qbox_apollo_fvp_full.py --skip-build --timeout 180 --post-login-probe --si-mode live-cl0-cl1 --out-dir build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime`
- Required coverage commands:
  - `python3 scripts/audit_qbox_apollo_ap_memory_map.py --output build/qbox-apollo-fvp/ap-map-9-1-1/ap-map-audit.json`
  - `python3 scripts/audit_qbox_apollo_fvp_full_coverage.py --result-json build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/result.json --output build/qbox-apollo-fvp/ap-map-9-1-1/full-coverage-audit.json`

## Execution strategy
### Parallel execution waves
> Target 5-8 todos per wave. < 3 per wave (except the final) = under-splitting.
Wave 1 (no deps): T1, T2, T3, T4, T5
Wave 2 (after 1): T6, T7, T8, T9, T10
Wave 3 (after 2): T11, T12, T13
Wave 4 (after 3): T14, T15
Critical path: T1/T2/T3 -> T6, T4 -> T7, T5 -> T10, then T11 -> T13 -> T14/T15

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| T1 | none | T2, T3, T6, T11 | T4, T5 |
| T2 | T1 | T6, T8, T9, T10, T11, T13 | T3, T4, T5 |
| T3 | T1 | T6, T11 | T2, T4, T5 |
| T4 | none | T7 | T1, T2, T3, T5 |
| T5 | none | T10 | T1, T2, T3, T4 |
| T6 | T1, T2, T3 | T11, T13 | T7, T8, T9, T10 |
| T7 | T2, T4 | T11, T13 | T6, T8, T9, T10 |
| T8 | T2 | T11, T13 | T6, T7, T9, T10 |
| T9 | T2 | T11, T13 | T6, T7, T8, T10 |
| T10 | T2, T5 | T11, T13 | T6, T7, T8, T9 |
| T11 | T6, T7, T8, T9, T10 | T13, T14 | T12 |
| T12 | T1 | T13, T15 | T11 |
| T13 | T11, T12 | T14, T15 | none |
| T14 | T13 | final verification | T15 |
| T15 | T13 | final verification | T14 |

## Todos
> Implementation + Test = ONE todo. Never separate.

- [x] T1. Add AP 9.1.1 map fixture and parser
  What to do / Must NOT do:
  Create `scripts/audit_qbox_apollo_ap_memory_map.py` with a checked-in expected map table copied from `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:91`. Include every non-reserved 9.1.1 row, but initially classify only the approved scope rows as `required_now`: AP SID, AP secure timer frame, RGIC2LGIC_MESSREG, APP subsystem FMU, low/high DRAM, AP UART/watchdog/timer, AP GIC/SMMU/RoS currently covered rows. Mark NoC/CMN/PCIe/debug/memory-controller rows as `deferred_epic`, not failing.
  Parallelization: Can parallel Y | Wave 1 | Blocks T2/T3/T6/T11
  References: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:91`, `scripts/audit_qbox_apollo_fvp_full_coverage.py:1`
  Acceptance criteria (agent-executable): `python3 -m py_compile scripts/audit_qbox_apollo_ap_memory_map.py` passes and `.omo/evidence/task-1-ap-ap-system-memory-map-qbox-gap.json` records the expected map row count, required-now row names, and deferred row names.
  QA scenarios (name the exact tool + invocation): happy: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --list-expected --output .omo/evidence/task-1-ap-ap-system-memory-map-qbox-gap.json`; failure: temporarily run the script with `--require-row DOES_NOT_EXIST` and capture non-zero exit in `.omo/evidence/task-1-ap-ap-system-memory-map-qbox-gap-fail.txt`.
  Commit: Y | test(qbox): add Apollo AP map audit fixture | Files `scripts/audit_qbox_apollo_ap_memory_map.py`

- [x] T2. Teach the audit to extract current QBox AP map coverage
  What to do / Must NOT do:
  Extend the new audit to inspect Lua files directly and report current QBox coverage from AP owner objects. It must identify `host_ap_dram1`, `host_ap_dram2`, `ap_primary_uart`, `ap_secure_uart`, `ap_watchdog_0`, `ap_secure_wdog`, `ap_timer_mem`, `ap_gic`, `ap_gic_its`, `ap_smmu_0`, RoS virtio/RTC, `host_ap_atu`, AP MHU windows, and any newly added AP SID/FMUs/RGIC windows. Do not rely on comments only; match object names, module type, target socket address, and size.
  Parallelization: Can parallel Y | Wave 1 | Blocks T6/T11/T13
  References: `tools/qbox/platforms/apollo/hw-block/rse.lua:1127`, `tools/qbox/platforms/apollo/hw-block/rse.lua:1701`, `tools/qbox/platforms/apollo/hw-block/ros.lua:3`, `tools/qbox/platforms/apollo/hw-block/ap_compute.lua:63`
  Acceptance criteria (agent-executable): audit JSON contains `covered`, `partial`, `missing`, and `deferred_epic` classifications, and currently fails only the approved missing P1 rows before T6-T10.
  QA scenarios: happy: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --output .omo/evidence/task-2-ap-ap-system-memory-map-qbox-gap.json || test $? -eq 2`; failure: use `--expect-current-host-ap-dram2 0x880000000` before migration and record expected mismatch in `.omo/evidence/task-2-ap-ap-system-memory-map-qbox-gap-fail.txt`.
  Commit: Y | test(qbox): audit Apollo AP QBox coverage | Files `scripts/audit_qbox_apollo_ap_memory_map.py`

- [x] T3. Add high DRAM migration inventory checks
  What to do / Must NOT do:
  Add audit checks for all high-DRAM source locations: full-system constant, direct-boot Lua, direct-boot DTS, and generated DTB build path. The audit must fail if any source still uses `0x200000000`, `0x20000000000`, or DTS high memory cells `<0x2 0x00000000 ...>` after migration. It must require `0x880000000` / DTS cells `<0x8 0x80000000 ...>`.
  Parallelization: Can parallel Y | Wave 1 | Blocks T6/T11
  References: `tools/qbox/platforms/apollo/hw-block/rse.lua:446`, `tools/qbox/platforms/apollo/hw-block/primary_compute.lua:82`, `tools/qbox/platforms/apollo/apollo-fvp-primary-compute.dts:69`, `scripts/run_qbox_apollo_fvp_linux.py`
  Acceptance criteria (agent-executable): before migration, the check reports mismatches with exact file/line references; after T6 it passes.
  QA scenarios: happy/failure combined: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --check high-dram --output .omo/evidence/task-3-ap-ap-system-memory-map-qbox-gap.json || test $? -eq 2`.
  Commit: Y | test(qbox): gate Apollo high DRAM placement | Files `scripts/audit_qbox_apollo_ap_memory_map.py`

- [x] T4. Confirm AP SID reset profile and host_scr suitability
  What to do / Must NOT do:
  Reuse existing `host_scr` for AP SID unless a concrete register mismatch is found. Confirm that its SID offsets, read-only behavior, and PID/CID reset values cover the AP SID requirements. If the programmer model reset values conflict with current `host_scr` defaults, extend `host_scr` tests and document the Lua parameter values required by T7; do not fork a new component.
  Parallelization: Can parallel Y | Wave 1 | Blocks T7/T11
  References: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:108`, `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:19646`, `tools/qbox/systemc-components/host_scr/include/host_scr.h:23`, `tools/qbox/tests/components/host_scr/host_scr-tests.cc:112`, `tools/qbox/platforms/apollo/hw-block/rse.lua:1503`
  Acceptance criteria (agent-executable): `ctest --test-dir tools/qbox/build -R 'host_scr' --output-on-failure` passes and `.omo/evidence/task-4-ap-ap-system-memory-map-qbox-gap.json` records the AP SID parameter/reset profile to use in T7.
  QA scenarios: happy: `cmake --build tools/qbox/build --target host_scr-tests --parallel 8 && ctest --test-dir tools/qbox/build -R 'host_scr' --output-on-failure`; failure: add or run a host_scr negative test that proves unsupported offsets return the expected response and record `.omo/evidence/task-4-ap-ap-system-memory-map-qbox-gap-fail.txt`.
  Commit: Y | test(qbox): confirm Apollo AP SID profile | Files optional `tools/qbox/tests/components/host_scr/host_scr-tests.cc`

- [x] T5. Confirm FMU subwindow source of truth
  What to do / Must NOT do:
  Derive the first APP subsystem FMU coverage set from SCP-firmware and docs. Use the AP/NI-710AE entries in `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_fmu.c:201` and the mapped bases in `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_mmap.h:107`. Cross-check against SMD FMU windows in `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:316`. Do not infer a 15 MB monolithic FMU if firmware consumes 1 MB subwindows through ATW.
  Parallelization: Can parallel Y | Wave 1 | Blocks T10
  References: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:123`, `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:316`, `arm-zena-css/documentation/design/fmu.rst:17`, `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_fmu.c:201`
  Acceptance criteria (agent-executable): `.omo/evidence/task-5-ap-ap-system-memory-map-qbox-gap.json` lists AP_CL0..AP_CL3 NI710AE FMUs, their firmware bases, parent indices, and target AP 9.1.1 coverage row.
  QA scenarios: happy: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --collect-fmu-plan --output .omo/evidence/task-5-ap-ap-system-memory-map-qbox-gap.json`; failure: script exits non-zero if any AP_CLx_NI710AE_FMU entry lacks a base.
  Commit: Y | test(qbox): record Apollo AP FMU coverage plan | Files `scripts/audit_qbox_apollo_ap_memory_map.py`

- [x] T6. Migrate high DRAM to the 9.1.1 range
  What to do / Must NOT do:
  Change full-system and direct AP QBox high DRAM base to `0x880000000`. Preserve current 2 GiB backing size unless direct/full artifacts already require more; if a larger size is chosen, update the audit and DTS together. Update DTS high memory cells to `<0x8 0x80000000 0x0 0x80000000>` for the current 2 GiB backing. Rebuild/regenerate direct boot DTB through the runner; do not hand-edit generated `build/` files.
  Parallelization: Can parallel Y | Wave 2 | Blocks T11/T13
  References: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:143`, `tools/qbox/platforms/apollo/hw-block/rse.lua:446`, `tools/qbox/platforms/apollo/hw-block/primary_compute.lua:82`, `tools/qbox/platforms/apollo/apollo-fvp-primary-compute.dts:69`
  Acceptance criteria (agent-executable): `python3 scripts/audit_qbox_apollo_ap_memory_map.py --check high-dram --output .omo/evidence/task-6-ap-ap-system-memory-map-qbox-gap.json` passes and generated direct DTB is produced by `--build-only`.
  QA scenarios: happy: `python3 scripts/run_qbox_apollo_fvp_linux.py --build-only --out-dir build/qbox-apollo-fvp/ap-map-9-1-1/direct-build`; failure: `fdtdump build/qbox-apollo-fvp/ap-map-9-1-1/direct-build/apollo-fvp-primary-compute.dtb | grep -E '08 80 00 00|880000000'` or equivalent `dtc -I dtb -O dts` check recorded in `.omo/evidence/task-6-ap-ap-system-memory-map-qbox-gap-dtb.txt`.
  Commit: Y | fix(qbox): align Apollo high DRAM map | Files `tools/qbox/platforms/apollo/hw-block/rse.lua`, `tools/qbox/platforms/apollo/hw-block/primary_compute.lua`, `tools/qbox/platforms/apollo/apollo-fvp-primary-compute.dts`, `scripts/audit_qbox_apollo_ap_memory_map.py`

- [x] T7. Wire AP SID into full-system and direct-visible AP view
  What to do / Must NOT do:
  Add `ap_sid` in the same owner Lua file as the AP UART/watchdog/timer objects, using the `host_scr` profile proven in T4. Bind it into `ap_compute.enable_ap_view_router()` with `bind_ap_socket(platform.ap_sid, "target_socket")`. Ensure the new object does not overlap existing secure watchdog/timer/UART windows.
  Parallelization: Can parallel Y | Wave 2 | Blocks T11/T13 | Blocked by T2/T4
  References: `tools/qbox/platforms/apollo/hw-block/rse.lua:1455`, `tools/qbox/platforms/apollo/hw-block/rse.lua:1479`, `tools/qbox/platforms/apollo/hw-block/ap_compute.lua:76`, `tools/qbox/systemc-components/host_scr/include/host_scr.h:215`
  Acceptance criteria (agent-executable): `python3 scripts/audit_qbox_apollo_ap_memory_map.py --require-row SID --output .omo/evidence/task-7-ap-ap-system-memory-map-qbox-gap.json` reports `covered` by `ap_sid` and `ctest --test-dir tools/qbox/build -R 'host_scr' --output-on-failure` passes.
  QA scenarios: happy: `cmake --build tools/qbox/build --target host_scr-tests platforms-vp --parallel 8 && ctest --test-dir tools/qbox/build -R 'host_scr' --output-on-failure`; failure: audit with `--require-row SID --forbid-object ap_sid` exits non-zero and writes `.omo/evidence/task-7-ap-ap-system-memory-map-qbox-gap-fail.txt`.
  Commit: Y | feat(qbox): expose Apollo AP SID in QBox | Files `tools/qbox/platforms/apollo/hw-block/rse.lua`, `tools/qbox/platforms/apollo/hw-block/ap_compute.lua`

- [x] T8. Add AP secure timer frame coverage
  What to do / Must NOT do:
  Extend AP timer coverage for `0x1a820000..0x1a82ffff`. First try the existing `qemu_hexagon_qtimer` multi-view support by increasing `nr_views` and adding a second secure view if the Lua/device API supports named extra view sockets. If it supports only one `mem_view`, add a narrow `gs_memory` AP secure timer frame with RAZ/WI semantics, document it as a register-placeholder, and keep the non-secure timer behavior unchanged. Do not alter timer interrupt PPIs or AP architectural timer config.
  Parallelization: Can parallel Y | Wave 2 | Blocks T11/T13 | Blocked by T2
  References: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:110`, `tools/qbox/platforms/apollo/hw-block/rse.lua:1479`, `tools/qbox/qemu-components/timer/qemu_hexagon_qtimer/include/qemu_hexagon_qtimer.h:25`, `tools/qbox/platforms/apollo/hw-block/ap_compute.lua:80`
  Acceptance criteria (agent-executable): AP map audit reports both `AP0_REFCLK_CNTCTL`, `AP0_REFCLK_S_CNTBase1`, and `AP0_REFCLK_NS_CNTBase0` as covered/explicit-placeholder; `ctest --test-dir tools/qbox/build -R 'host_gtimer|router' --output-on-failure` passes if relevant.
  QA scenarios: happy: `cmake --build tools/qbox/build --target platforms-vp --parallel 8 && python3 scripts/audit_qbox_apollo_ap_memory_map.py --require-row AP0_REFCLK_S_CNTBase1 --output .omo/evidence/task-8-ap-ap-system-memory-map-qbox-gap.json`; failure: audit with the secure timer row removed from Lua must fail and be captured in `.omo/evidence/task-8-ap-ap-system-memory-map-qbox-gap-fail.txt`.
  Commit: Y | feat(qbox): cover Apollo AP secure timer frame | Files `tools/qbox/platforms/apollo/hw-block/rse.lua`, `tools/qbox/platforms/apollo/hw-block/ap_compute.lua`, optional docs/audit

- [x] T9. Add RGIC2LGIC_MESSREG AP window
  What to do / Must NOT do:
  Add a 64 KiB AP window at `0x5fff0000`. Because current boot flow has no known software consumer for remote-GIC message semantics, implement it as an explicit narrow register placeholder using `gs_memory` with `init_mem = true` unless an existing QBox GIC multiview or message-register component already exists. Name it `ap_rgic2lgic_messreg`, bind it to AP view, and record replacement debt for future GIC-720AE multichip parity.
  Parallelization: Can parallel Y | Wave 2 | Blocks T11/T13 | Blocked by T2
  References: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:133`, `hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/neoverse_rd/platform/rdv3/rdv3_bl31_setup.c:27`, `tools/qbox/systemc-components/gicx00_multiview/include/gicx00_multiview.h:20`
  Acceptance criteria (agent-executable): AP map audit reports `RGIC2LGIC_MESSREG` as `explicit_placeholder` with exact address/size and docs explain the missing message semantics.
  QA scenarios: happy: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --require-row RGIC2LGIC_MESSREG --output .omo/evidence/task-9-ap-ap-system-memory-map-qbox-gap.json`; failure: audit rejects any broad placeholder larger than 64 KiB and records `.omo/evidence/task-9-ap-ap-system-memory-map-qbox-gap-fail.txt`.
  Commit: Y | feat(qbox): add Apollo RGIC2LGIC window | Files `tools/qbox/platforms/apollo/hw-block/rse.lua`, `tools/qbox/platforms/apollo/hw-block/ap_compute.lua`, docs/audit

- [x] T10. Add APP subsystem FMU QBox coverage
  What to do / Must NOT do:
  Wire APP subsystem FMU coverage using `zena_fmu`. Add AP-side FMU objects for the NI-710AE cluster FMU subwindows derived in T5, and ensure the AP 9.1.1 region `0x1d000000..0x1defffff` is represented without claiming unimplemented reserved subranges as fully modeled. Use `zena_fmu` bank/record parameters for each active subwindow; add only narrow explicit placeholders for reserved/unimplemented FMU slices if needed for decode completeness. Do not collapse all 15 MB into a writable memory blob.
  Parallelization: Can parallel Y | Wave 2 | Blocks T11/T13 | Blocked by T2/T5
  References: `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:123`, `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:316`, `arm-zena-css/documentation/design/fmu.rst:245`, `tools/qbox/systemc-components/zena_fmu/include/zena_fmu.h:22`, `tools/qbox/tests/components/zena_fmu/zena_fmu-tests.cc:117`, `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_fmu.c:201`
  Acceptance criteria (agent-executable): `ctest --test-dir tools/qbox/build -R 'zena_fmu' --output-on-failure` passes, AP map audit reports FMU row as `partial_model` or `covered` with exact subwindow objects, and no object spans reserved ranges without placeholder classification.
  QA scenarios: happy: `cmake --build tools/qbox/build --target zena_fmu-tests platforms-vp --parallel 8 && ctest --test-dir tools/qbox/build -R 'zena_fmu' --output-on-failure`; failure: run audit with `--require-row 'FMU Region' --forbid-placeholder-only` to prove a pure `gs_memory` blob is rejected, capture `.omo/evidence/task-10-ap-ap-system-memory-map-qbox-gap-fail.txt`.
  Commit: Y | feat(qbox): model Apollo APP FMU windows | Files `tools/qbox/platforms/apollo/hw-block/rse.lua`, optional `tools/qbox/systemc-components/zena_fmu/*`, `tools/qbox/tests/components/zena_fmu/*`, audit/docs

- [x] T11. Integrate AP map audit with full coverage audit
  What to do / Must NOT do:
  Add a callout or data merge path so `scripts/audit_qbox_apollo_fvp_full_coverage.py` can include AP 9.1.1 memory-map coverage summary when an AP-map audit JSON is available. Preserve its existing runtime gate checks; do not make full runtime success depend on deferred epics.
  Parallelization: Can parallel N | Wave 3 | Blocks T13/T14
  References: `scripts/audit_qbox_apollo_fvp_full_coverage.py:1`, `scripts/audit_qbox_apollo_fvp_full_coverage.py:94`, `doc/apollo-qbox-full-model/coverage-ledger.md:1`
  Acceptance criteria (agent-executable): `python3 -m py_compile scripts/audit_qbox_apollo_fvp_full_coverage.py scripts/audit_qbox_apollo_ap_memory_map.py` passes and combined coverage JSON includes an `ap_9_1_1_memory_map` section.
  QA scenarios: happy: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --output build/qbox-apollo-fvp/ap-map-9-1-1/ap-map-audit.json && python3 scripts/audit_qbox_apollo_fvp_full_coverage.py --output .omo/evidence/task-11-ap-ap-system-memory-map-qbox-gap.json`; failure: pass a malformed AP-map JSON and assert the full audit reports `invalid_ap_map_audit` without crashing.
  Commit: Y | test(qbox): include AP map in full coverage audit | Files `scripts/audit_qbox_apollo_fvp_full_coverage.py`, `scripts/audit_qbox_apollo_ap_memory_map.py`

- [x] T12. Update project documentation and coverage ledger
  What to do / Must NOT do:
  Update the relevant docs to explain AP 9.1.1 coverage status, high DRAM migration, explicit placeholders, and deferred parity epics. Required docs: `doc/apollo-qbox-hardware-ko.md`, `doc/qbox-apollo-fvp-map-analysis.md`, and `doc/apollo-qbox-full-model/coverage-ledger.md`. Do not overstate placeholders as FVP-equivalent full models.
  Parallelization: Can parallel Y | Wave 3 | Blocks T13/T15
  References: `doc/apollo-qbox-hardware-ko.md`, `doc/qbox-apollo-fvp-map-analysis.md:61`, `doc/apollo-qbox-full-model/coverage-ledger.md:1`, `.omo/drafts/ap-ap-system-memory-map-qbox-gap.md`
  Acceptance criteria (agent-executable): docs mention `0x08_8000_0000`, `AP SID`, `RGIC2LGIC_MESSREG`, `APP subsystem FMU`, and deferred NoC/CMN/PCIe/debug/memory-controller epics.
  QA scenarios: happy: `rg -n '0x08_8000_0000|AP SID|RGIC2LGIC|APP subsystem FMU|deferred' doc/apollo-qbox-hardware-ko.md doc/qbox-apollo-fvp-map-analysis.md doc/apollo-qbox-full-model/coverage-ledger.md > .omo/evidence/task-12-ap-ap-system-memory-map-qbox-gap.txt`; failure: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --check-docs --output .omo/evidence/task-12-ap-ap-system-memory-map-qbox-gap.json` exits non-zero if a required term is absent.
  Commit: Y | docs(qbox): document Apollo AP map coverage | Files docs listed above

- [x] T13. Run direct AP Linux regression
  What to do / Must NOT do:
  Run direct AP Linux with the migrated high DRAM and new AP windows. Confirm the generated DTB advertises the new high DRAM range and Linux reaches login/probe. Do not accept `--build-only` as runtime success.
  Parallelization: Can parallel N | Wave 3 | Blocks T14/T15
  References: `scripts/run_qbox_apollo_fvp_linux.py --help`, `tools/qbox/platforms/apollo/apollo-fvp-primary-compute.dts:69`, `tools/qbox/platforms/apollo/hw-block/primary_compute.lua:82`
  Acceptance criteria (agent-executable): `build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime/result.json` exists, reports pass/login, and post-login probe log does not contain kernel panic, synchronous external abort, or memory node parse failure.
  QA scenarios: happy: `python3 scripts/run_qbox_apollo_fvp_linux.py --skip-build --timeout 300 --post-login-probe --out-dir build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime`; failure: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --check-runtime --result-json build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime/result.json --output .omo/evidence/task-13-ap-ap-system-memory-map-qbox-gap.json`.
  Commit: N | runtime evidence only | Files generated under `build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime`

- [x] T14. Run Apollo full-system regression and coverage gate
  What to do / Must NOT do:
  Run the full-system QBox path with live SI CL0/CL1 and post-login probes. Then run the AP-map audit and full coverage audit against the result. Do not use service-model mode for final acceptance unless live mode is blocked and explicitly recorded as a blocker.
  Parallelization: Can parallel Y | Wave 4 | Blocks final verification
  References: `scripts/run_qbox_apollo_fvp_full.py --help`, `scripts/audit_qbox_apollo_fvp_full_coverage.py:141`, `AGENTS.md` runtime validation ladder
  Acceptance criteria (agent-executable): full runtime `result.json` reports pass, per-UART logs exist for RSE/SI CL0/SI CL1/secure console/primary console, AP map audit passes required-now rows, and full coverage audit passes runtime gates.
  QA scenarios: happy: `env QBOX_RDASPEN_NETDEV=type=user python3 scripts/run_qbox_apollo_fvp_full.py --skip-build --timeout 180 --post-login-probe --si-mode live-cl0-cl1 --out-dir build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime`; coverage: `python3 scripts/audit_qbox_apollo_ap_memory_map.py --output build/qbox-apollo-fvp/ap-map-9-1-1/ap-map-audit.json && python3 scripts/audit_qbox_apollo_fvp_full_coverage.py --result-json build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/result.json --output build/qbox-apollo-fvp/ap-map-9-1-1/full-coverage-audit.json`.
  Commit: N | runtime evidence only | Files generated under `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime`

- [x] T15. Produce implementation closeout report
  What to do / Must NOT do:
  Add a short Korean closeout report under `doc/` with changed files, exact commands, runtime result paths, coverage status, and remaining deferred epics. Do not replace existing design docs; link to updated docs and generated evidence.
  Parallelization: Can parallel Y | Wave 4 | Blocks final verification
  References: `doc/qbox-apollo-fvp-map-analysis.md`, `doc/apollo-qbox-hardware-ko.md`, `build/qbox-apollo-fvp/ap-map-9-1-1/`
  Acceptance criteria (agent-executable): report exists and references direct/full runtime `result.json`, AP map audit JSON, full coverage audit JSON, and all P1 windows.
  QA scenarios: happy: `rg -n 'result.json|ap-map-audit.json|full-coverage-audit.json|AP SID|RGIC2LGIC|FMU|0x08_8000_0000' doc/*apollo* doc/qbox* > .omo/evidence/task-15-ap-ap-system-memory-map-qbox-gap.txt`; failure: doc check script from T12 rejects missing evidence links.
  Commit: Y | docs(qbox): report Apollo AP map validation | Files `doc/<new closeout report>.md`

## Final verification wave (after ALL todos)
> Runs in parallel. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [x] F1. Plan compliance audit
  Run `python3 scripts/audit_qbox_apollo_ap_memory_map.py --output build/qbox-apollo-fvp/ap-map-9-1-1/ap-map-audit.json` and verify all `required_now` rows are `covered`, `partial_model`, or `explicit_placeholder` as permitted by the todo that introduced them.
- [x] F2. Code quality review
  Run `git -C tools/qbox diff --check`, `python3 -m py_compile scripts/audit_qbox_apollo_fvp_full_coverage.py scripts/audit_qbox_apollo_ap_memory_map.py`, and the focused CTest command from the verification strategy.
- [x] F3. Real manual QA
  Agent-executed runtime QA only: run direct AP Linux and full-system commands from T13/T14. Inspect `result.json`, `summary.txt`, and UART logs; do not rely on terminal screen output.
- [x] F4. Scope fidelity
  Confirm no source changes touched Yocto metadata, firmware sources, local build scripts, generated build outputs outside evidence, or deferred NoC/CMN/PCIe/debug/memory-controller implementations.

## Commit strategy
- Prefer four atomic commits if this plan is executed:
  1. `test(qbox): add Apollo AP map audit`
  2. `fix(qbox): align Apollo high DRAM map`
  3. `feat(qbox): cover Apollo AP map gaps`
  4. `docs(qbox): document Apollo AP map coverage`
- Use `git commit -s` and include the plan footer in every commit body:
  `Plan: .omo/plans/ap-ap-system-memory-map-qbox-gap.md`
- Keep runtime evidence uncommitted unless the repository already tracks a specific report artifact under `doc/`.

## Success criteria
- AP 9.1.1 static audit exists and is repeatable.
- Direct and full QBox AP high DRAM placement matches `0x08_8000_0000` source and DT evidence.
- AP SID is modeled through `host_scr` and appears in AP view coverage.
- AP secure timer frame and RGIC2LGIC_MESSREG are explicit AP windows with documented behavior.
- APP subsystem FMU coverage is based on `zena_fmu`/firmware-derived subwindows, not a broad memory blob.
- Direct AP Linux reaches login/probe after the address-map migration.
- Apollo full-system QBox reaches the existing pass condition with RSE, SI CL0, SI CL1, TF-A/U-Boot/Linux logs present.
- Docs and coverage ledger identify implemented coverage, explicit placeholders, and deferred parity epics without overstating FVP equivalence.
