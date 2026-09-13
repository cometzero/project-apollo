# ​0x8058, NONFP_SPEC, Non-floating-point operation speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8058--NONFP-SPEC--Non-floating-point-operation-speculatively-executed>

##### `0x8058`, NONFP\_SPEC, Non-floating-point operation speculatively executed

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) data-processing operation due to any of:

- A scalar instruction that would be counted by the [DP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0073--DP-SPEC--Operation-speculatively-executed--integer-data-processing?lang=en#event_dp_spec) event.
- An A64 Advanced SIMD data processing instruction defined in the section [Data processing - SIMD and floating-point](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point?lang=en#cegjeiei) that would not be counted by [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec).
- An SVE instruction with vector source or destination registers that would not be counted by [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec).
- An SME instruction that would not be counted by [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec).

It is IMPLEMENTATION DEFINED which non-floating-point data-processing operations are counted in AArch32 state.
