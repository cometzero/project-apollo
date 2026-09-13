# ​0x8036, SVE_FP_RECPE_SPEC, Floating-point operation speculatively executed, SVE reciprocal estimate

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8036--SVE-FP-RECPE-SPEC--Floating-point-operation-speculatively-executed--SVE-reciprocal-estimate>

##### `0x8036`, SVE\_FP\_RECPE\_SPEC, Floating-point operation speculatively executed, SVE reciprocal estimate

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point reciprocal estimate operation counted by [ASE\_SVE\_FP\_RECPE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8037--ASE-SVE-FP-RECPE-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-reciprocal-estimate?lang=en#event_ase_sve_fp_recpe_spec) due to any of the following instructions:

- SVE: FRECPE or FRSQRTE.
