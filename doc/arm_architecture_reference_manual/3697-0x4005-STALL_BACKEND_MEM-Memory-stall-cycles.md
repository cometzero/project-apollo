# ​0x4005, STALL_BACKEND_MEM, Memory stall cycles

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4005--STALL-BACKEND-MEM--Memory-stall-cycles>

##### `0x4005`, STALL\_BACKEND\_MEM, Memory stall cycles

The counter counts each cycle counted by [STALL\_BACKEND\_MEMBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8164--STALL-BACKEND-MEMBOUND--Backend-stall-cycles--memory-bound?lang=en#event_stall_backend_membound) when there is a demand data miss in the last level of data or unified cache within the PE clock domain.

If Armv8.7 is implemented, the counter also counts backend stall cycles when a non-cacheable data access is in progress.

If Armv8.7 is not implemented, it is IMPLEMENTATION DEFINED whether the counter counts backend stall cycles when a non-cacheable data access is in progress.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when there is a demand data miss in the last level of data or unified cache within the PE clock domain for any PE in the multithreaded processor.

PMCEID0\_EL0[37] reads as 1 if this event is implemented and 0 otherwise.
