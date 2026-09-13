# ​0x8159, STALL_FRONTEND_L1I, Frontend stall cycles, level 1 instruction cache

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8159--STALL-FRONTEND-L1I--Frontend-stall-cycles--level-1-instruction-cache>

##### `0x8159`, STALL\_FRONTEND\_L1I, Frontend stall cycles, level 1 instruction cache

The counter counts each cycle counted by [STALL\_FRONTEND\_MEMBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8158--STALL-FRONTEND-MEMBOUND--Frontend-stall-cycles--memory-bound?lang=en#event_stall_frontend_membound) when there is a demand instruction miss in the first level of instruction cache.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when there is a demand instruction miss in the first level of instruction cache for any PE in the multithreaded processor.

The counter does not count the cycle if any of the following are true:

- The [STALL\_FRONTEND\_L2I](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x815A--STALL-FRONTEND-L2I--Frontend-stall-cycles--level-2-instruction-cache?lang=en#event_stall_frontend_l2i) event is implemented and there is a demand instruction miss in the second level of instruction cache, meaning the [STALL\_FRONTEND\_L2I](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x815A--STALL-FRONTEND-L2I--Frontend-stall-cycles--level-2-instruction-cache?lang=en#event_stall_frontend_l2i) event counts the cycle.
- There is a demand instruction miss in the last level of instruction cache within the PE clock domain, meaning the [STALL\_FRONTEND\_MEM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x815B--STALL-FRONTEND-MEM--Frontend-stall-cycles--last-level-PE-cache-or-memory?lang=en#event_stall_frontend_mem) event counts the cycle.
