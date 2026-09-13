# ​0x8364, SME_INT16_SPEC, Operation speculatively executed, SME 16-bit integer, data-processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8364--SME-INT16-SPEC--Operation-speculatively-executed--SME-16-bit-integer--data-processing>

##### `0x8364`, SME\_INT16\_SPEC, Operation speculatively executed, SME 16-bit integer, data-processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 16-bit integer data-processing operation counted by [SME\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8378--SME-INT-SPEC--Operation-speculatively-executed--SME-integer--data-processing?lang=en#event_sme_int_spec) due to an instruction which reads from or writes to any part of the ZA array.

This event counts based on the largest type read or written by an operation.
