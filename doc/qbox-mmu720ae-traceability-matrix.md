# QBox MMU-720AE Traceability Matrix

작성일: 2026-06-08

상태: 진행 중

이 문서는 `doc/qbox-mmu720ae-systemc-spec-ko.md`의 AC2와
`doc/qbox-mmu720ae-systemc-tasks-ko.md`의 `MMU720-SYS-002`를 위한 추적
문서다. 현재 구현은 QBox 부팅 경로에서 QEMU `arm_smmuv3` backend를 SystemC
`mmu720ae` backend로 대체하고, Linux probe에 필요한 register/queue surface와
Apollo full-system boot regression을 검증한 단계다. FVP parity 완료 상태는
아니다.

## 현재 구현 요약

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| SystemC component target | 완료 | `tools/qbox/systemc-components/mmu720ae/`, `mmu720ae.so` build |
| QEMU-free core | 완료 | `mmu720ae_core.{h,cc}`가 QEMU header/object를 포함하지 않음 |
| SMMUv3 ID/reset register | 부분 완료 | `IDR0/IDR1/IDR3/IDR5/IIDR/AIDR`, register tests pass |
| CR0/CR0ACK enable sequence | 부분 완료 | `mmu720ae-register-tests` pass |
| CMDQ producer/consumer probe behavior | 부분 완료 | `CMDQ_PROD` write advances `CMDQ_CONS`, queue tests pass |
| EVTQ/PRIQ full record engine | 부분 완료 | TBU translation fault EVTQ record write helper와 event count test 존재; PRI와 full fault class 미완료 |
| Combined IRQ | 부분 완료 | global error와 EVTQ pending IRQ 모델링, PRI/PMU/RAS 소스 미연동 |
| Apollo TBU sockets | 부분 완료 | 5개 socket 존재, SMMU disabled bypass, enabled no-silent-bypass, SID extension/default SID fallback test pass |
| STE/CD table walker | 미완료 | page-table walk 구현 없음 |
| Stage 1/2/nested translation | 미완료 | translation tests 없음 |
| TLB/uTLB/DMI invalidation | 부분 완료 | generation counter만 존재, translated DMI grant 없음 |
| RAS/PMU/SMD_CSR sideband | 미완료 | sideband API와 tests 없음 |
| Apollo platform replacement | 완료 | direct/full Lua 기본 backend `systemc-mmu720ae`; QEMU fallback 유지 |
| Apollo full-system boot | 진행 중 | 이전 pass: `build/qbox-apollo-fvp/default-accel-runtime-20260609-004435/result.json`; 최신 SystemC retry 3회는 `si_cl1:cpu0_oor`/AP UART 0바이트로 blocked |
| Direct AP Linux SMMU probe | 완료 | `build/qbox-fvp-rd-aspen/mmu720ae-smoke-default/result.json`, `smmu_v3=true` |
| FVP parity comparison | 미완료 | comparison script/report 없음 |

## Register And Feature Matrix

| Feature/Register | Source | Exposed Value/Behavior | Implementation | Test | Runtime Evidence | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| `compatible = "arm,smmu-v3"` | Apollo DTS/TF-A DTS | generic SMMUv3 driver binding | platform DTB/runtime artifact | direct boot dmesg | `qbox-fvp-rd-aspen/mmu720ae-smoke-default` | 완료 |
| Register base/size | Apollo DTS | `0x1c0000000`, `0x08000000` | `conf.lua`, `conf-rse.lua` | map validator | `map-validation.json` | 완료 |
| Combined IRQ | Apollo DTS | GIC SPI 65 | `irq_combined` socket | EVTQ pending and GERROR clear tests | full boot marker pass | 부분 |
| `IDR0.S1P` | SMMUv3/Linux expectation | set | `mmu720ae_core::idr0_value()` | `ResetProfileExposesImplementedProbeFeatures` | direct Linux probe | 부분 |
| `IDR0.ATS` | unsupported in current model | clear | `idr0_value()` | register test | direct Linux probe | 완료 |
| `IDR0.PRI` | unsupported in current model | clear | `idr0_value()` | register/queue tests | direct Linux probe | 완료 |
| `IDR0.MSI` | unsupported in current model | clear | `idr0_value()` | register test | direct Linux probe | 완료 |
| `IDR0.COHACC` | Linux/FVP visible capability | set | `idr0_value()` | register test | direct Linux probe | 부분 |
| `IDR1.SIDSIZE` | Apollo cfg2 profile | 8 bits | `idr1_value()` | register test | direct Linux probe | 부분 |
| `IDR1.SSIDSIZE` | current model no SSID | 0 | `idr1_value()` | register test | direct Linux probe | 완료 |
| `IDR1.CMDQS/EVTQS` | Linux queue allocation | 256 entries each | `idr1_value()` | register test | direct Linux probe allocates cmdq/evtq | 부분 |
| `IDR1.PRIQS` | PRI unsupported | 0 | `idr1_value()` | queue test masks PRI IRQ | direct Linux probe | 완료 |
| `IDR5.GRAN4K` | Linux translation granule | set | `idr5_value()` | register test | direct Linux probe | 부분 |
| `IDR5.OAS` | Apollo profile | 48-bit | `idr5_value()` | register test | direct Linux probe says oas 48-bit | 부분 |
| `CR0/CR0ACK` | Linux enable sequence | implemented bits mirror immediately | `write32(CR0)` | register test | direct/full boot | 부분 |
| `IRQ_CTRL/IRQ_CTRLACK` | Linux IRQ setup | EVTQ/GERROR bits mirror, PRI masked | `write32(IRQ_CTRL)` | queue test | direct/full boot | 부분 |
| `GBPA.UPDATE` | Linux global bypass setup | update bit clears immediately | `write32(GBPA)` | covered by boot only | direct/full boot | 부분 |
| `GERROR/GERRORN` | global error status | clear-on-GERRORN write | `write32(GERRORN)` | queue test | TBU enabled fault unit test | 부분 |
| `STRTAB_BASE/_CFG` | stream table setup | stores register values | default store path | register test covers base only | direct/full boot | 부분 |
| `CMDQ_BASE/PROD/CONS` | command queue | base stores, prod mirrors cons and bumps DMI generation | `write32(CMDQ_PROD)` | queue test | direct/full boot | 부분 |
| `EVTQ_BASE/PROD/CONS` | event queue | TBU translation fault record writes via `ptw_socket`, prod advances, pending IRQ clears on cons write | `build_translation_fault_event()`, `complete_event_queue_write()` | `EnabledSmmuWritesTranslationFaultEventRecord` | unit only | 부분 |
| `PRI queue` | disabled feature | ID exposes disabled, IRQ masked | register/IRQ mask | queue test | direct boot | 완료 |
| TBU disabled behavior | SMMU reset/disabled path | bypasses requester traffic | `tbu_b_transport()` | `DisabledSmmuBypassesRequesterTraffic` | not used by current full boot | 부분 |
| TBU enabled without walker | fidelity guard | command error, no downstream bypass, EVTQ record when configured, GERROR on event queue abort | `tbu_b_transport()` | `EnabledSmmuDoesNotSilentlyBypassWithoutWalker`, `EnabledSmmuWritesTranslationFaultEventRecord` | not used by current full boot | 부분 |
| TBU SID extension | SMMUv3 transaction attribute requirement | TLM extension SID overrides TBU default SID | `request_attrs_extension`, `request_sid_or_default()` | `Ace1UsesSidExtensionForFaultEvent` | unit only | 부분 |
| TBU default SID fallback | Zena CSS SMD_CSR reset-derived profile | ACE1 `0x00`, ACE2 `0x20`, LTI00 `0x40`, LTI01 `0x60`, LTI02 `0x80`; fallback counted only when SID extension missing | TBU CCI params, `record_tbu_request_sid()` | `Ace2SocketUsesDefaultSidForFaultEvent` | unit only | 부분 |
| MMU diagnostics counters | spec FR10 | command sync, event record, event queue abort, TBU request/fallback SID counters visible to tests | `mmu720ae_core` getters | `mmu720ae-queue-tests`, `mmu720ae-tbu-tests` | unit only | 부분 |

## Runtime Evidence

| Evidence | Command | Result |
| --- | --- | --- |
| Unit tests | `ctest --test-dir tools/qbox/build -R 'mmu720ae' --output-on-failure` | 3/3 pass; register, queue, TBU, EVTQ fault, SID extension/default fallback covered |
| Map validator | `./scripts/validate_qbox_fvp_rd_aspen_map.py` | pass, writes `build/qbox-fvp-rd-aspen/map-validation.json` |
| Full Apollo SystemC previous pass | `QBOX_RDASPEN_NETDEV=type=user python3 scripts/run_qbox_apollo_fvp_full.py --skip-build --si-mode live-cl0-cl1 --timeout 180 --post-login-probe --out-dir build/qbox-apollo-fvp/default-accel-runtime-20260609-004435` | `passed=true`, `verdict=pass`, `smmu_backend=systemc-mmu720ae`, `qbox_performance_preset=true`; superseded by newer retry evidence below |
| Full Apollo SystemC latest retries | same command shape with current `mmu720ae` build, out dirs `mmu720ae-sid-runtime-*` | 3/3 blocked at `si_cl1:cpu0_oor`; RSE reaches AP power-on, SI CL1/secure/AP UART logs are 0 bytes |
| Full Apollo QEMU fallback compare | `QBOX_RDASPEN_NETDEV=type=user python3 scripts/run_qbox_apollo_fvp_full.py --skip-build --si-mode live-cl0-cl1 --smmu-backend qemu-arm-smmuv3 --timeout 240 --post-login-probe --out-dir build/qbox-apollo-fvp/mmu720ae-qemu-backend-compare-20260609-010054` | `passed=true`, `verdict=pass`, confirms current local artifacts can boot with QEMU SMMU fallback |
| Direct AP probe | `python3 scripts/run_qbox_fvp_rd_aspen_linux.py --skip-build --skip-dtb --no-copy-disk --timeout 120 --post-login-probe --smmu-backend systemc-mmu720ae --netdev type=user --out-dir build/qbox-fvp-rd-aspen/mmu720ae-sid-direct-20260609-010221` | `passed=true`; Linux login, post-login probe, `arm-smmu-v3` probe, combined IRQ in `/proc/interrupts` observed |

## Remaining Mandatory Work

FVP-level parity cannot be claimed until the following are implemented and
verified:

1. STE/CD decode and AArch64 stage 1/2/nested table walker.
2. Event queue record packing beyond current TBU translation fault record and
   additional fault injection classes.
3. SSID/security/requester attributes beyond current SID extension, plus
   runtime SID proof for real QBox requesters.
4. Translated DMI grant/invalidation keyed by SID/SSID/security/generation.
5. RAS/PMU and Zena CSS SMD_CSR sideband state ownership.
6. FVP/QBox SMMU comparison script and mandatory comparison report.
7. Documentation closure in project roadmap/runbook after parity gates pass.
8. Full Apollo SystemC backend handoff regression investigation: current
   evidence shows AP CPU0 remains in hold-reset/zero UART in full-system runs,
   while direct AP-only SystemC and full-system QEMU SMMU fallback pass.
