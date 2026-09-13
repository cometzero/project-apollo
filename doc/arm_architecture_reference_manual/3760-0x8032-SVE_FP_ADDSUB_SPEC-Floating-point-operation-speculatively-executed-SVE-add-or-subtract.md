# ​0x8032, SVE_FP_ADDSUB_SPEC, Floating-point operation speculatively executed, SVE add or subtract

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8032--SVE-FP-ADDSUB-SPEC--Floating-point-operation-speculatively-executed--SVE-add-or-subtract>

##### `0x8032`, SVE\_FP\_ADDSUB\_SPEC, Floating-point operation speculatively executed, SVE add or subtract

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point add or subtract operation counted by [ASE\_SVE\_FP\_ADDSUB\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8033--ASE-SVE-FP-ADDSUB-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-add-or-subtract?lang=en#event_ase_sve_fp_addsub_spec) due to any of the following instructions:

- SVE: FABD, FADD, FSUB, or FSUBR.
- SVE2: BFADD or BFSUB.
