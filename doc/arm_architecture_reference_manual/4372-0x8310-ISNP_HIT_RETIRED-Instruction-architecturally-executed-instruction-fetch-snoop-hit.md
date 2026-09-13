# ​0x8310, ISNP_HIT_RETIRED, Instruction architecturally executed, instruction fetch snoop hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8310--ISNP-HIT-RETIRED--Instruction-architecturally-executed--instruction-fetch-snoop-hit>

##### `0x8310`, ISNP\_HIT\_RETIRED, Instruction architecturally executed, instruction fetch snoop hit

The counter counts each [instruction architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) counted by [INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed?lang=en#event_inst_retired) that hit in an instruction cache outside the cache hierarchy of this PE when fetched.
