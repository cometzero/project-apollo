# ​0x8186, UOP_RETIRED, Micro-operation architecturally executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8186--UOP-RETIRED--Micro-operation-architecturally-executed>

##### `0x8186`, UOP\_RETIRED, Micro-operation architecturally executed

The counter counts each micro-operation that would be executed in a Simple sequential execution of the program.

Unlike [OP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x003A--OP-RETIRED--Micro-operation-architecturally-executed?lang=en#event_op_retired), this event is not linked to the definition of [OP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x003B--OP-SPEC--Micro-operation-speculatively-executed?lang=en#event_op_spec), meaning it counts micro-operations that are created from other operations after those operations are counted by [OP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x003B--OP-SPEC--Micro-operation-speculatively-executed?lang=en#event_op_spec).
