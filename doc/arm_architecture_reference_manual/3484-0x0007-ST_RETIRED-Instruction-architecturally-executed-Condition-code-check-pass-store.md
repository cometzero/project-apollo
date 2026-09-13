# ​0x0007, ST_RETIRED, Instruction architecturally executed, Condition code check pass, store

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0007--ST-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--store>

##### `0x0007`, ST\_RETIRED, Instruction architecturally executed, Condition code check pass, store

The counter counts each architecturally-executed [memory-writing instruction](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_writing_instructions) counted by [INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed?lang=en#event_inst_retired).

The counter does not count a Store-Exclusive instruction that fails.

PMCEID0\_EL0[7] reads as 1 if this event is implemented and 0 otherwise.
