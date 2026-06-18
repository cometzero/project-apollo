# Apollo QBox AP 9.1.1 Memory Map 구현 종료 리포트

작성일: 2026-06-14

## 요약

T15 범위에서는 Apollo QBox AP programmer model 9.1.1 gap 작업의 최종
종료 상태를 갱신했다. T14의 live CL0/CL1 full-system runtime과 full
coverage gate는 현재 통과 상태다.

이 리포트는 새 구현을 full FVP-equivalent model로 선언하지 않는다. AP
SID는 `host_scr` 모델로 노출됐고, high DRAM은 현재 FVP boot bank1 base로 되돌렸다.
AP secure watchdog control/refresh, AP secure timer frame, RGIC2LGIC_MESSREG는
명시적 `placeholder`이고, APP subsystem FMU는 firmware-derived NI-710AE cluster subwindow만
`zena_fmu` partial model로 다룬다.

현재 증거 기준의 결론은 다음과 같다.

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| Direct AP Linux runtime | 성공 | `build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime/result.json`의 `passed: true`, `post_login_probe: true`, `probe_complete: true` |
| Full-system runtime | 성공 | `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/result.json`의 `passed: true`, `verdict: pass`, `completion_gates.G4: pass` |
| AP map audit | 성공 | `build/qbox-apollo-fvp/ap-map-9-1-1/ap-map-audit.json`의 `passed: true`, `missing_required_now: []` |
| Full coverage audit | 성공 | `build/qbox-apollo-fvp/ap-map-9-1-1/full-coverage-audit.json`의 `passed: true`, `ap_9_1_1_memory_map.status: pass`, `checks[].name=runtime_result_passed/status: pass` |

## 변경 파일 요약

이번 T15 refresh는 종료 리포트와 task-local evidence만 갱신한다. 아래
목록은 T1-T14에서 이미 완료된 구현/문서 범위를 high level로 요약한
것이다.

| 범위 | 파일 |
| --- | --- |
| AP map audit / full coverage audit | `scripts/test/audit_qbox_apollo_ap_memory_map.py`, `scripts/test/audit_qbox_apollo_fvp_full_coverage.py` |
| QBox Apollo AP map wiring | `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`, `tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`, `tools/qbox-platform/platforms/apollo/hw-block/primary_compute.lua`, `tools/qbox-platform/platforms/apollo/apollo-fvp-primary-compute.dts` |
| Component regression | `tools/qbox/tests/components/host_scr/host_scr-tests.cc` |
| Project documentation | `doc/apollo-qbox-hardware-ko.md`, `doc/qbox-apollo-fvp-map-analysis.md`, `doc/apollo-qbox-full-model/coverage-ledger.md` |
| T15 closeout | `doc/apollo-qbox-ap-map-9-1-1-closeout-ko.md` |

## 실행 명령과 결과 경로

### Direct AP Linux runtime

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --skip-build \
  --timeout 300 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime
```

결과:

- Result JSON: `build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime/result.json`
- Summary: `build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime/summary.txt`
- Log: `build/qbox-apollo-fvp/ap-map-9-1-1/direct-runtime/qbox-apollo-fvp.log`
- 판정: `passed: true`, `apollo-fvp login:` 관측, post-login probe 완료.

### Full-system runtime

```bash
env QBOX_RDASPEN_NETDEV=type=user \
  python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build \
  --timeout 180 \
  --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime
```

결과:

- Result JSON: `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/result.json`
- Summary: `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/summary.txt`
- 주요 로그:
  - `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/qbox-platform.log`
  - `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/qbox-rse.log`
  - `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/qbox-safety-island-cl0.log`
  - `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/qbox-safety-island-cl1.log`
  - `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/qbox-secure-console.log`
  - `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/qbox-primary-console.log`
- 판정: `passed: true`, `verdict: pass`, child return code 0.
- Probe: `post_login_probe.complete: true`, `done_marker: true`.
- Live SI: `safety_island_mode: live-cl0-cl1`, service-model fallback 없음.

### AP map audit

```bash
python3 scripts/test/audit_qbox_apollo_ap_memory_map.py \
  --output build/qbox-apollo-fvp/ap-map-9-1-1/ap-map-audit.json
```

결과:

- Audit JSON: `build/qbox-apollo-fvp/ap-map-9-1-1/ap-map-audit.json`
- 판정: `passed: true`
- `required_now_row_count: 19`
- `deferred_epic_row_count: 19`
- `missing_required_now: []`

### Full coverage audit

```bash
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/result.json \
  --output build/qbox-apollo-fvp/ap-map-9-1-1/full-coverage-audit.json
```

결과:

- Audit JSON: `build/qbox-apollo-fvp/ap-map-9-1-1/full-coverage-audit.json`
- 전체 판정: `passed: true`
- AP 9.1.1 map section: `status: pass`, `audit_passed: true`
- Runtime gate: `checks[]`의 `runtime_result_passed.status: pass`,
  `gate:G4.status: pass`
- UART/log gate: RSE, SI CL0, SI CL1, secure console, primary console 로그
  존재 확인.

## AP 9.1.1 Coverage 상태

| AP 9.1.1 row | QBox instance / backing | 상태 | 주의 |
| --- | --- | --- | --- |
| High DRAM | direct `ram_1`, `host_ap_dram2` @ `0x20000000000` | `partial` | 현재 Arm Zena CSS FVP boot artifact와 맞춘 2 GiB bank1 backing이다. AP 9.1.1의 `0x880000000` high DRAM row는 full programmer-model parity 항목으로 남긴다. |
| AP SID | `ap_sid` / `host_scr` | `covered` | `0x1a4a0000..0x1a4affff` AP System ID register window가 AP logical view에 노출된다. |
| AP secure watchdog control/refresh | `ap_secure_wdog`, `ap_secure_wdog_refresh` / `gs_memory` | `explicit_placeholder` | `0x1a460000..0x1a46ffff` control frame과 `0x1a470000..0x1a47ffff` refresh frame decode만 보존한다. watchdog side effect, interrupt/reset 동작, access-control fidelity는 full model debt다. |
| AP secure timer frame | `ap_secure_timer_frame` / `gs_memory` | `explicit_placeholder` | `0x1a820000..0x1a82ffff` decode window만 보존한다. secure generic timer side effect 또는 PPI 동작의 full model이 아니다. |
| RGIC2LGIC_MESSREG | `ap_rgic2lgic_messreg` / `gs_memory` | `explicit_placeholder` | `0x5fff0000..0x5fffffff` 64 KiB window만 보존한다. remote/local GIC message semantics는 deferred work다. |
| APP subsystem FMU | `ap_cl0_ni710ae_fmu..ap_cl3_ni710ae_fmu` / `zena_fmu` | `partial_model` | `0x1d000000..0x1defffff` aggregate row 중 firmware-derived NI-710AE cluster FMU subwindow만 모델링한다. 남은 aggregate/reserved 영역을 broad memory blob으로 처리하지 않는다. |

## 해결된 디버깅 항목

T14 최종 통과 전에 두 문제가 해결됐다. 둘 다 현재 blocker가 아니다.

- Lua local variable limit: `rse.lua` 확장 과정에서 발생한 local variable
  limit 문제는 구조 조정 뒤 사라졌다. 현재
  `build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/qbox-platform.log`에는
  `too many local variables` 또는 `local variable` 실패 marker가 없다.
- Linux external abort: 이전에는 full-system 경로가 `0x20000000000`
  handoff를 쓰는데 QBox backing이 `0x880000000`에만 있어 Linux
  synchronous external abort가 발생했다. 현재는 `host_ap_dram2`와
  direct `ram_1`을 FVP 현재 bank1인 `0x20000000000`에 다시 두고,
  `scripts/run/run_qbox_apollo_fvp_full.py`의 high-DRAM handoff
  patch/rebuild tweak을 제거했다.

## Placeholder와 Deferred Epics

명시 placeholder:

- AP secure watchdog control/refresh: `ap_secure_wdog`,
  `ap_secure_wdog_refresh`, `gs_memory`, `0x1a460000..0x1a46ffff` and
  `0x1a470000..0x1a47ffff`
- AP secure timer frame: `ap_secure_timer_frame`, `gs_memory`,
  `0x1a820000..0x1a82ffff`
- RGIC2LGIC_MESSREG: `ap_rgic2lgic_messreg`, `gs_memory`,
  `0x5fff0000..0x5fffffff`

Partial model:

- APP subsystem FMU: `zena_fmu` 기반 AP CL0..CL3 NI-710AE FMU subwindow만
  모델링한다.
- High DRAM: 현재 FVP boot bank1인 `0x20000000000`에 2 GiB backing을 둔다.
  AP 9.1.1 base `0x880000000`은 deferred programmer-model parity다.

Deferred epics:

- System NoC0/1/2/3 GPV
- CMN GPV
- PCIe NI-710AE Memory space1, PCIe CTRL/PHY
- Debug Memory Map
- Memory controller control memory map
- AP Memory Expansion 1/2
- STM
- Cluster management domain memory map
- SMD AP_EXP_I_1 NoC config space

이 항목들은 full FVP-equivalent model로 완료됐다고 보고하면 안 된다.

## 최종 판정

T14 full-system runtime artifact는 pass다. 현재
`build/qbox-apollo-fvp/ap-map-9-1-1/full-runtime/result.json`은
`passed: true`와 `verdict: pass`를 기록한다. 또한
`build/qbox-apollo-fvp/ap-map-9-1-1/full-coverage-audit.json`은 full runtime
gate와 AP 9.1.1 memory map section을 모두 pass로 기록한다.

현재 남은 항목은 runtime blocker가 아니라 fidelity scope다. AP secure
watchdog control/refresh, AP secure timer frame, RGIC2LGIC_MESSREG, high
DRAM 전체 용량, APP subsystem FMU aggregate 영역, deferred
NoC/CMN/PCIe/debug/memory-controller 계열은 별도 epic에서 full model 여부를
다뤄야 한다.

## 관련 문서

- `doc/apollo-qbox-hardware-ko.md`
- `doc/qbox-apollo-fvp-map-analysis.md`
- `doc/apollo-qbox-full-model/coverage-ledger.md`
- `.omo/plans/ap-ap-system-memory-map-qbox-gap.md`
