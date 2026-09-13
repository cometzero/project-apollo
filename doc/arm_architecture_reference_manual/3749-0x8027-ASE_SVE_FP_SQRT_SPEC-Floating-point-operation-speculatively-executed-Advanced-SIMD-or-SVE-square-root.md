# ​0x8027, ASE_SVE_FP_SQRT_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE square-root

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8027--ASE-SVE-FP-SQRT-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-square-root>

##### `0x8027`, ASE\_SVE\_FP\_SQRT\_SPEC, Floating-point operation speculatively executed, Advanced SIMD or SVE square-root

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point square-root operation counted by [FP\_SQRT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8024--FP-SQRT-SPEC--Floating-point-operation-speculatively-executed--square-root?lang=en#event_fp_sqrt_spec) due to any of the following A64 instructions:

- Advanced SIMD: FSQRT.
- SVE: FSQRT.

It is IMPLEMENTATION DEFINED which floating-point square-root operations are counted in AArch32 state.
