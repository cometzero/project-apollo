# ​0x802F, ASE_SVE_FP_MUL_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802F--ASE-SVE-FP-MUL-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-multiply>

##### `0x802F`, ASE\_SVE\_FP\_MUL\_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE multiply

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point fused multiply-add or multiply-subtract operation counted by [FP\_MUL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802C--FP-MUL-SPEC--Floating-point-operation-speculatively-executed--multiply?lang=en#event_fp_mul_spec) due to any of the following A64 instructions:

- Advanced SIMD: FMUL or FMULX.
- SVE: FMUL, FMULX, or FTSMUL.
- SVE2: BFMUL.

It is IMPLEMENTATION DEFINED which floating-point fused multiply-add or multiply-subtract operations are counted in AArch32 state.
