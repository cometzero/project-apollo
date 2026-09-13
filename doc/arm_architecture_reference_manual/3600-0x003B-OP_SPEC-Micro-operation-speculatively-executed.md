# ​0x003B, OP_SPEC, Micro-operation speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x003B--OP-SPEC--Micro-operation-speculatively-executed>

##### `0x003B`, OP\_SPEC, Micro-operation speculatively executed

The counter counts each operation [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) executed by the PE.

This includes operations that would not be executed in a Simple sequential execution of the program.

PMCEID1\_EL0[27] reads as 1 if this event is implemented and 0 otherwise.
