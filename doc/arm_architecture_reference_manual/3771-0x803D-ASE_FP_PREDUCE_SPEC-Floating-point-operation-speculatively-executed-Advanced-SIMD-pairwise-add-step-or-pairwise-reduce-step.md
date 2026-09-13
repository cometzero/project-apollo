# ​0x803D, ASE_FP_PREDUCE_SPEC, Floating-point operation speculatively executed, Advanced SIMD pairwise add step or pairwise reduce step

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x803D--ASE-FP-PREDUCE-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-pairwise-add-step-or-pairwise-reduce-step>

##### `0x803D`, ASE\_FP\_PREDUCE\_SPEC, Floating-point operation speculatively executed, Advanced SIMD pairwise add step or pairwise reduce step

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point pairwise add step or pairwise reduce step operation counted by [ASE\_FP\_VREDUCE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8431--ASE-FP-VREDUCE-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-pairwise-or-reduction?lang=en#event_ase_fp_vreduce_spec) due to any of the following A64 instructions:

- Advanced SIMD: FADDP, FMAXNMP, FMAXP, FMINNMP, or FMINP.

It is IMPLEMENTATION DEFINED which floating-point pairwise add step or pairwise reduce step operations are counted in AArch32 state.
