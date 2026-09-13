# ​0x802D, ASE_FP_MUL_SPEC, Floating-point operation speculatively executed, Advanced SIMD multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802D--ASE-FP-MUL-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-multiply>

##### `0x802D`, ASE\_FP\_MUL\_SPEC, Floating-point operation speculatively executed, Advanced SIMD multiply

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point multiply operation counted by [ASE\_SVE\_FP\_MUL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802F--ASE-SVE-FP-MUL-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-multiply?lang=en#event_ase_sve_fp_mul_spec) due to any of the following A64 instructions:

- Advanced SIMD: FMUL or FMULX.

It is IMPLEMENTATION DEFINED which floating-point multiply operations are counted in AArch32 state.
