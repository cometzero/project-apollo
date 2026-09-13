# ​0x8023, ASE_SVE_FP_DIV_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE divide

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8023--ASE-SVE-FP-DIV-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-divide>

##### `0x8023`, ASE\_SVE\_FP\_DIV\_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE divide

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point divide operation counted by [FP\_DIV\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8020--FP-DIV-SPEC--Floating-point-operation-speculatively-executed--divide?lang=en#event_fp_div_spec) due to any of the following A64 instructions:

- Advanced SIMD: FDIV.
- SVE: FDIV or FDIVR.

It is IMPLEMENTATION DEFINED which floating-point divide operations are counted in AArch32 state.
