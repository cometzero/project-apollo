# ​0x8030, FP_ADDSUB_SPEC, Floating-point operation speculatively executed, add or subtract

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8030--FP-ADDSUB-SPEC--Floating-point-operation-speculatively-executed--add-or-subtract>

##### `0x8030`, FP\_ADDSUB\_SPEC, Floating-point operation speculatively executed, add or subtract

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point add or subtract operation counted by [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec) due to any of the following A64 instructions:

- Scalar: FADD or FSUB.
- Advanced SIMD: FABD, FADD, or FSUB.
- SVE: FABD, FADD, FSUB, or FSUBR.
- SVE2: BFADD or BFSUB.
- SME2: BFADD, BFSUB, FADD, or FSUB.

It is IMPLEMENTATION DEFINED which floating-point add or subtract operations are counted in AArch32 state.
