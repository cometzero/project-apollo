# ​0x815B, STALL_FRONTEND_MEM, Frontend stall cycles, last level PE cache or memory

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x815B--STALL-FRONTEND-MEM--Frontend-stall-cycles--last-level-PE-cache-or-memory>

##### `0x815B`, STALL\_FRONTEND\_MEM, Frontend stall cycles, last level PE cache or memory

The counter counts each cycle counted by [STALL\_FRONTEND\_MEMBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8158--STALL-FRONTEND-MEMBOUND--Frontend-stall-cycles--memory-bound?lang=en#event_stall_frontend_membound) when there is a demand instruction miss in the last level of instruction or unified cache within the PE clock domain or a non-cacheable instruction fetch in progress.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when there is a demand instruction miss in the last level of instruction or unified cache within the PE clock domain or a non-cacheable instruction fetch in progress for any PE in the multithreaded processor.
