# ​0x8353, SE_FP_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD floating-point, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8353--SE-FP-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-floating-point--data-processing>

##### `0x8353`, SE\_FP\_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD floating-point, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point data-processing operation counted by [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec) due to an A64 Advanced SIMD, SVE, or SME operation.

That is, each operation counted by [ASE\_FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8011--ASE-FP-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD?lang=en#event_ase_fp_spec), [SVE\_FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8012--SVE-FP-SPEC--Floating-point-operation-speculatively-executed--SVE?lang=en#event_sve_fp_spec), or [SME\_FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8352--SME-FP-SPEC--Operation-speculatively-executed--SME-floating-point--data-processing?lang=en#event_sme_fp_spec).

It is IMPLEMENTATION DEFINED which floating-point data-processing operations are counted in AArch32 state.
