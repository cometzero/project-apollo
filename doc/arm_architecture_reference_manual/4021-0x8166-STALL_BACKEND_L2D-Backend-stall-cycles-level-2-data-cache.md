# ​0x8166, STALL_BACKEND_L2D, Backend stall cycles, level 2 data cache

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8166--STALL-BACKEND-L2D--Backend-stall-cycles--level-2-data-cache>

##### `0x8166`, STALL\_BACKEND\_L2D, Backend stall cycles, level 2 data cache

The counter counts each cycle counted by [STALL\_BACKEND\_MEMBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8164--STALL-BACKEND-MEMBOUND--Backend-stall-cycles--memory-bound?lang=en#event_stall_backend_membound) when there is a demand data miss in the second level of data or unified cache.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when there is a demand data miss in the second level of data or unified cache for any PE in the multithreaded processor.

The counter does not count the cycle if there is a demand data miss in the last level of data or unified cache within the PE clock domain, meaning the [STALL\_BACKEND\_MEM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4005--STALL-BACKEND-MEM--Memory-stall-cycles?lang=en#event_stall_backend_mem) event counts the cycle.
