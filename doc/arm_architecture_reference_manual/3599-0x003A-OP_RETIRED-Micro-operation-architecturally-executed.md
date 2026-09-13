# ​0x003A, OP_RETIRED, Micro-operation architecturally executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x003A--OP-RETIRED--Micro-operation-architecturally-executed>

##### `0x003A`, OP\_RETIRED, Micro-operation architecturally executed

The counter counts each operation counted by [OP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x003B--OP-SPEC--Micro-operation-speculatively-executed?lang=en#event_op_spec) that would be executed in a Simple sequential execution of the program.

PMCEID1\_EL0[26] reads as 1 if this event is implemented and 0 otherwise.
