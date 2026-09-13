# ​0x80DF, ST_FIXED_BYTES_SPEC, Non-scalable store bytes speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DF--ST-FIXED-BYTES-SPEC--Non-scalable-store-bytes-speculatively-executed>

##### `0x80DF`, ST\_FIXED\_BYTES\_SPEC, Non-scalable store bytes speculatively executed

The counter counts each speculatively written byte counted by [LDST\_FIXED\_BYTES\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DB--LDST-FIXED-BYTES-SPEC--Non-scalable-load-and-store-bytes-speculatively-executed?lang=en#event_ldst_fixed_bytes_spec).

For each instruction, the counter is incremented by the number of bytes transferred per register multiplied by the number of registers transferred. That is, the counter is incremented by:

- Half the value that the [LDST\_FIXED\_BYTES\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DB--LDST-FIXED-BYTES-SPEC--Non-scalable-load-and-store-bytes-speculatively-executed?lang=en#event_ldst_fixed_bytes_spec) event counts if the operation is a swap, or compare and swap operation.
- The same as for [LDST\_FIXED\_BYTES\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DB--LDST-FIXED-BYTES-SPEC--Non-scalable-load-and-store-bytes-speculatively-executed?lang=en#event_ldst_fixed_bytes_spec) if the operation is any other store operation, including an atomic store operation.
