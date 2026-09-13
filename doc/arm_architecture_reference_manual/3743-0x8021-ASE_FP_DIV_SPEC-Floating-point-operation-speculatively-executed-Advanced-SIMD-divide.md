# ​0x8021, ASE_FP_DIV_SPEC, Floating-point operation speculatively executed, Advanced SIMD divide

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8021--ASE-FP-DIV-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-divide>

##### `0x8021`, ASE\_FP\_DIV\_SPEC, Floating-point operation speculatively executed, Advanced SIMD divide

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point divide operation counted by [ASE\_SVE\_FP\_DIV\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8023--ASE-SVE-FP-DIV-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-divide?lang=en#event_ase_sve_fp_div_spec) due to any of the following A64 instructions:

- Advanced SIMD: FDIV.

It is IMPLEMENTATION DEFINED which floating-point divide operations are counted in AArch32 state.
