# QBox MHU-320AE SystemC Tasks and Verification Criteria

작성일: 2026-06-09

상태: 완료

## Task Board

| ID | Task | 완료 기준 | 상태 |
| --- | --- | --- | --- |
| MHU320-SYS-001 | Baseline/source inventory | MHU docs, DTS, Lua, existing tests 확인 | 완료 |
| MHU320-SYS-010 | Spec/design/plan 문서 | 4개 문서 추가 | 완료 |
| MHU320-SYS-020 | Component scaffold | `mhu320ae` dynamic module build target 존재 | 완료 |
| MHU320-SYS-030 | Register frame model | PBX/MBX DBCH register unit test pass | 완료 |
| MHU320-SYS-040 | SCMI/PFDI/doorbell hooks | SCMI, PFDI, reset, bridge tests pass | 완료 |
| MHU320-SYS-050 | Platform default switch | Apollo/RD-Aspen boot-critical MHU uses `mhu320ae` | 완료 |
| MHU320-SYS-060 | Static/build validation | syntax, map, build, ctest pass | 완료 |
| MHU320-SYS-070 | Runtime validation | Apollo live CL0/CL1 full-system boot pass | 완료 |
| MHU320-SYS-080 | Commit/push/shutdown | atomic commits pushed, host powered off | 진행 중 |

## Detailed Tasks

### MHU320-SYS-001: Baseline/source inventory

Evidence:

- `doc/arm_zena_css_dev_guide/08-fixed-virtual-platform.md` lists
  Arm MHU-320AE in the Safety Island block.
- `tools/qbox/platforms/fvp-rd-aspen/fvp-rd-aspen-primary-compute.dts` exposes
  `arm,mhuv3` nodes at `0x40020000`, `0x40050000`, `0x400b0000`, `0x400e0000`.
- `tools/qbox/platforms/apollo/apollo-qvp.lua` exposes live CL1 local MHU frames
  at `0x39000000`, `0x39040000`, and `0x39200000`.
- `tools/qbox/systemc-components/mhuv3_stub/` contains the existing validated
  PBX/MBX frame model and service hooks.

### MHU320-SYS-020: Component scaffold

Files:

- `tools/qbox/systemc-components/mhu320ae/CMakeLists.txt`
- `tools/qbox/systemc-components/mhu320ae/include/mhu320ae.h`
- `tools/qbox/systemc-components/mhu320ae/src/mhu320ae.cc`
- `tools/qbox/systemc-components/CMakeLists.txt`

Verification:

```bash
cmake --build tools/qbox/build --target mhu320ae --parallel 8
```

### MHU320-SYS-030: Register frame model

Files:

- `tools/qbox/tests/components/mhu320ae/mhu320ae-tests.cc`
- `tools/qbox/tests/components/mhu320ae/CMakeLists.txt`
- `tools/qbox/tests/components/CMakeLists.txt`

Required tests:

- PBX/MBX `DBCH_CFG0`, feature, IIDR, AIDR reads.
- PBX status, interrupt status, interrupt enable, combined summary.
- MBX default mask, mask clear, receiver clear, combined summary.
- Configured 32-channel CL1 window and out-of-range channel behavior.

Verification:

```bash
ctest --test-dir tools/qbox/build -R 'mhu320ae' --output-on-failure
```

### MHU320-SYS-040: SCMI/PFDI/doorbell hooks

Required tests:

- SCMI Power Domain protocol version response and ACK bit signal.
- SCMI Power Domain state set/get and reset signal behavior.
- SCMI System Power reset pulse.
- PFDI monitor version response on configured channel base.
- Direct-boot compatibility opt-in behavior.
- Doorbell bridge pair isolation.
- AP/SI CL1 HIPC resource table seed, RPMsg name-service, synthetic TX done.

### MHU320-SYS-050: Platform default switch

Files:

- `tools/qbox/platforms/fvp-rd-aspen/conf.lua`
- `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`
- `tools/qbox/platforms/apollo/apollo-qvp.lua`
- `tools/qbox/platforms/apollo/apollo-si-cl1.lua`
- `scripts/run/run_qbox_fvp_rd_aspen_linux.py`
- `scripts/run/run_qbox_fvp_rd_aspen_rse.py`
- `scripts/run/run_qbox_apollo_fvp_si_cl1.py`

Verification:

```bash
./scripts/test/validate_qbox_fvp_rd_aspen_map.py
```

### MHU320-SYS-060: Static/build validation

Commands:

```bash
python3 -m py_compile scripts/*/*.py
bash -n run_qbox.sh scripts/run/run_qbox_apollo_fvp_full_tmux.sh
git -C tools/qbox diff --check
git diff --check
cmake --build tools/qbox/build \
  --target mhu320ae mhu320ae-tests platforms-vp --parallel 8
ctest --test-dir tools/qbox/build -R 'mhu320ae' --output-on-failure
```

### MHU320-SYS-070: Runtime validation

Command:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build --timeout 900 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/mhu320ae-live-verify-$(date +%Y%m%d-%H%M%S)
```

Pass criteria:

- RSE boot markers pass.
- Safety Island CL0 boot markers pass.
- Safety Island CL1 Zephyr, PFDI, HIPC/RPMsg/network markers pass.
- TF-A BL2/BL31, OP-TEE, U-Boot markers pass.
- Linux login and root shell markers pass.
- Post-login probe completes with expected module and interface evidence.

### MHU320-SYS-080: Commit/push/shutdown

Use `$commit-atomic` rules:

- Conventional Commit.
- English commit message.
- `git commit -s`.
- Nested `tools/qbox` commit first, root commit second.
- Push both current branches to GitHub remotes.
- Run `sudo poweroff` only after commits and pushes succeed.

## Verification Evidence

2026-06-09 실행 결과:

| Check | Result | Evidence |
| --- | --- | --- |
| Shell syntax | pass | `bash -n run_qbox.sh scripts/run/run_qbox_apollo_fvp_full_tmux.sh` |
| Python syntax | pass | `python3 -m py_compile ...` for changed QBox runners and validators |
| Diff whitespace | pass | `git diff --check`, `git -C tools/qbox diff --check` |
| Map validation | pass | `build/qbox-fvp-rd-aspen/map-validation.json` |
| QBox build | pass | `cmake --build tools/qbox/build --target mhu320ae mhu320ae-tests platforms-vp --parallel 8` |
| Component tests | pass | `ctest --test-dir tools/qbox/build -R 'mhu320ae' --output-on-failure` |
| CL1 isolated boot | pass | `build/qbox-apollo-fvp/mhu320ae-si-cl1-20260609-063830/result.json` |
| Apollo full-system boot | pass | `build/qbox-apollo-fvp/mhu320ae-live-verify-20260609-063846/result.json` |

Full-system result highlights:

- `passed: true`
- `verdict: pass`
- `mhu_backend: systemc-mhu320ae`
- `smmu_backend: systemc-mmu720ae`
- `completion_gates.G4: pass`
- RSE, SI CL0, SI CL1, AP firmware, Linux login, root shell, RPMsg/HIPC
  post-login markers all pass.
- `rse_start_to_login_prompt_s`: `46.714`

Coverage audit note:

- `mhuv3_scmi_transport` and RSE fidelity labels pass with
  `mhuv3 = systemc-mhu320ae`.
- The existing coverage audit command returned exit code 1 because unrelated
  RAS FFH and SMMU runtime log patterns were absent from the selected primary
  console log. This is not an MHU-320AE regression and the full-system gate
  result remains pass.
