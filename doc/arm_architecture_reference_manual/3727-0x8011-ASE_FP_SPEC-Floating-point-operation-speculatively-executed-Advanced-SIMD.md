# ​0x8011, ASE_FP_SPEC, Floating-point operation speculatively executed, Advanced SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8011--ASE-FP-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD>

##### `0x8011`, ASE\_FP\_SPEC, Floating-point operation speculatively executed, Advanced SIMD

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point operation counted by [ASE\_SVE\_FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8013--ASE-SVE-FP-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE?lang=en#event_ase_sve_fp_spec) due to an A64 Advanced SIMD instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD floating-point operations are counted in AArch32 state.
