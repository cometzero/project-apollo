# ​0x80CD, LD_FIXED_OPS_SPEC, Non-scalable load element operations speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CD--LD-FIXED-OPS-SPEC--Non-scalable-load-element-operations-speculatively-executed>

##### `0x80CD`, LD\_FIXED\_OPS\_SPEC, Non-scalable load element operations speculatively executed

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) counted by [LDST\_FIXED\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CB--LDST-FIXED-OPS-SPEC--Non-scalable-load-or-store-element-operations-speculatively-executed?lang=en#event_ldst_fixed_ops_spec).

For each instruction, the counter is incremented by the number of operations specified by the instruction. That is, the counter is incremented by:

- Half the value that the [LDST\_FIXED\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CB--LDST-FIXED-OPS-SPEC--Non-scalable-load-or-store-element-operations-speculatively-executed?lang=en#event_ldst_fixed_ops_spec) event counts if the operation is a load atomic, compare and swap, or swap operation.
- The same as for [LDST\_FIXED\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CB--LDST-FIXED-OPS-SPEC--Non-scalable-load-or-store-element-operations-speculatively-executed?lang=en#event_ldst_fixed_ops_spec) if the operation is any other load operation.
