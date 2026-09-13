# ​0x8368, SME_INT32_SPEC, Operation speculatively executed, SME 32-bit integer, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8368--SME-INT32-SPEC--Operation-speculatively-executed--SME-32-bit-integer--data-processing>

##### `0x8368`, SME\_INT32\_SPEC, Operation speculatively executed, SME 32-bit integer, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 32-bit integer data-processing operation counted by [SME\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8378--SME-INT-SPEC--Operation-speculatively-executed--SME-integer--data-processing?lang=en#event_sme_int_spec) due to an instruction which reads from or writes to any part of the ZA array.

This event counts based on the largest type read or written by an operation.
