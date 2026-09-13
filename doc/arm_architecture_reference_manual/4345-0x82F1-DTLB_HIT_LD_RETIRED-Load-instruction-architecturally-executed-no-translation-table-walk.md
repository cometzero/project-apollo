# ​0x82F1, DTLB_HIT_LD_RETIRED, Load instruction architecturally executed, no translation table walk

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82F1--DTLB-HIT-LD-RETIRED--Load-instruction-architecturally-executed--no-translation-table-walk>

##### `0x82F1`, DTLB\_HIT\_LD\_RETIRED, Load instruction architecturally executed, no translation table walk

The counter counts each [Memory-reading instruction](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions) [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) counted by [DTLB\_HIT\_LDST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82F3--DTLB-HIT-LDST-RETIRED--Load-or-store-instruction-architecturally-executed--no-translation-table-walk?lang=en#event_dtlb_hit_ldst_retired) that did not cause a refill of a data TLB involving at least one translation table walk access.
