# ​0x8162, STALL_FRONTEND_FLUSH, Frontend stall cycles, flush recovery

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8162--STALL-FRONTEND-FLUSH--Frontend-stall-cycles--flush-recovery>

##### `0x8162`, STALL\_FRONTEND\_FLUSH, Frontend stall cycles, flush recovery

The counter counts each cycle counted by [STALL\_FRONTEND\_CPUBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8160--STALL-FRONTEND-CPUBOUND--Frontend-stall-cycles--processor-bound?lang=en#event_stall_frontend_cpubound) when the frontend is recovering from a pipeline flush.

The situations where the frontend is flushed are IMPLEMENTATION DEFINED. For example, the frontend might be flushed on a branch misprediction or on a Context synchronization event.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when the frontend is recovering from a pipeline flush for any PE in the multithreaded processor.
