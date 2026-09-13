# ​0x8311, ISNP_HIT_NEAR_RETIRED, Instruction architecturally executed, instruction fetch snoop hit in near cache

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8311--ISNP-HIT-NEAR-RETIRED--Instruction-architecturally-executed--instruction-fetch-snoop-hit-in-near-cache>

##### `0x8311`, ISNP\_HIT\_NEAR\_RETIRED, Instruction architecturally executed, instruction fetch snoop hit in near cache

The counter counts each [instruction architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) counted by [ISNP\_HIT\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8310--ISNP-HIT-RETIRED--Instruction-architecturally-executed--instruction-fetch-snoop-hit?lang=en#event_isnp_hit_retired) that hit outside of the cache hierarchy of this PE in the local PE cluster when fetched.
