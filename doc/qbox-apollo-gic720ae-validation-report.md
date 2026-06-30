# Apollo QBox GIC-720AE Implementation And Validation Report

Date: 2026-06-30

## Scope

This work implements the QBox side of the Apollo FVP GIC-720AE plan without
changing Apollo software sources. AP TF-A/OP-TEE/U-Boot/Linux, SI CL0
SCP-firmware, SI CL1 Zephyr, and RSE TF-M are used as read-only software
contracts for QBox model behavior and validation.

## Implementation Summary

| Area | Result |
| --- | --- |
| QEMU GICv3 | Added opt-in GICv4.1, DirectLPI, RVPEID, Valid+Dirty, and VPEID feature reporting through immutable QOM properties. Generic defaults remain unchanged. |
| QEMU ITS | Added opt-in GICv4.1 VMAPP/SVPET reporting and Apollo-compatible collection table entry sizing so Linux observes 32768 interrupt collections. |
| QBox wrappers | Exposed the new QEMU GIC/ITS properties as CCI parameters in `arm_gicv3` and `arm_gicv3_its`. |
| Apollo Lua | Enabled the opt-in AP GIC/ITS properties for full-system and direct AP paths, kept direct AP at 960 SPIs, and replaced `RGIC2LGIC_MESSREG` with `gic720ae_messreg`. |
| SystemC/TLM | Hardened `gicx00_multiview` register behavior and added the named `gic720ae_messreg` sideband model. |
| Validation tooling | Added `scripts/test/compare_qbox_fvp_gic_logs.py` and unit tests for FVP-vs-QBox GIC log parity. |

## Validation Matrix

| Gate | Command/evidence | Result |
| --- | --- | --- |
| Failing-first parity gate | `.omo/evidence/apollo-fvp-gic720ae-qbox/T1-red.json` | Passed: old QBox log fails on missing DirectLPI/GICv4.1/ITS parity markers. |
| Parser self check | `.omo/evidence/apollo-fvp-gic720ae-qbox/T1-self-pass.json` | Passed. |
| Python/static checks | `.omo/evidence/apollo-fvp-gic720ae-qbox/C002-focused-build-tests.log` | Passed. |
| Focused QBox build/tests | `arm_gicv3`, `arm_gicv3_its`, `gicx00_multiview-tests`, `gic720ae_messreg-tests`, `apollo_fvp_full_system` | Passed. |
| Component tests | `ctest -R 'gicx00_multiview|gic720ae_messreg|zena_fmu'` | Passed. |
| Direct AP boot | `build/qbox-apollo-fvp/gic720ae-direct/result.json` | Passed with post-login probe and GIC markers. |
| Full-system boot | `build/qbox-apollo-fvp/gic720ae-full/result.json` | Passed with RSE, SI CL0, SI CL1, AP firmware, Linux, maps/interrupts, and post-login marker groups. |
| GIC parity | `build/qbox-apollo-fvp/gic720ae-full/gic-parity.json` | Passed: QBox matches FVP for 960 SPIs, DirectLPI, GICv4.1 mode, 32768 collections, and DirectLPI VPE invalidation. |
| Coverage audit | `build/qbox-apollo-fvp/gic720ae-full/full-coverage-audit.json` | Passed. |

## Runtime GIC Evidence

The full-system primary console reports:

```text
GICv3: 960 SPIs implemented
GICv3 features: 16 PPIs, DirectLPI
GICv4 features: DirectLPI RVPEID Valid+Dirty
ITS@0x0000000020840000: Using GICv4.1 mode 00000000 00000001
ITS@0x0000000020840000: allocated 32768 Interrupt Collections
ITS: Using DirectLPI for VPE invalidation
apollo-fvp login:
```

The full-system SI CL0 log preserves the existing SCP-firmware multiview marker:

```text
GIC-multiview configured successfully
```

## Remaining Fidelity Gaps

| Gap | Status |
| --- | --- |
| Monolithic physical GIC-720AE with shared view state | Deferred. Current design remains QEMU GIC/ITS plus SystemC integration surfaces. |
| AXI5-Stream timing and complete SPI Collator semantics | Deferred beyond `gic720ae_messreg` deterministic storage and access checks. |
| Wake Request, Q-channel, P-channel behavior | Deferred. |
| FuSa injection, internal safety/RAS signaling | Deferred. |
| Full AP 16-core equivalence | Deferred; active Apollo QBox boot remains the configured 4-core path. |

## Evidence Files

- `.omo/evidence/apollo-fvp-gic720ae-qbox/C002-focused-build-tests.log`
- `.omo/evidence/apollo-fvp-gic720ae-qbox/F3-runtime.log`
- `build/qbox-apollo-fvp/gic720ae-direct/result.json`
- `build/qbox-apollo-fvp/gic720ae-full/result.json`
- `build/qbox-apollo-fvp/gic720ae-full/gic-parity.json`
- `build/qbox-apollo-fvp/gic720ae-full/full-coverage-audit.json`
