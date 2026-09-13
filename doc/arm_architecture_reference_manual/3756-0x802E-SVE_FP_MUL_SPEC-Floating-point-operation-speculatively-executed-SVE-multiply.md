# ​0x802E, SVE_FP_MUL_SPEC, Floating-point operation speculatively executed, SVE multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802E--SVE-FP-MUL-SPEC--Floating-point-operation-speculatively-executed--SVE-multiply>

##### `0x802E`, SVE\_FP\_MUL\_SPEC, Floating-point operation speculatively executed, SVE multiply

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point multiply operation counted by [ASE\_SVE\_FP\_MUL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802F--ASE-SVE-FP-MUL-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-multiply?lang=en#event_ase_sve_fp_mul_spec) due to any of the following instructions:

- SVE: FMUL, FMULX, or FTSMUL.
- SVE2: BFMUL.
