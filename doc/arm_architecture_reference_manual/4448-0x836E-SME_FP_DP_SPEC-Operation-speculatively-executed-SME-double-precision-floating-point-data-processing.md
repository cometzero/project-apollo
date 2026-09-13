# ​0x836E, SME_FP_DP_SPEC, Operation speculatively executed, SME double-precision floating-point, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x836E--SME-FP-DP-SPEC--Operation-speculatively-executed--SME-double-precision-floating-point--data-processing>

##### `0x836E`, SME\_FP\_DP\_SPEC, Operation speculatively executed, SME double-precision floating-point, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) double-precision floating-point data-processing operation counted by [SME\_FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8352--SME-FP-SPEC--Operation-speculatively-executed--SME-floating-point--data-processing?lang=en#event_sme_fp_spec) due to an instruction which reads from or writes to any part of the ZA array.

This event counts based on the largest type read or written by an operation.
