# ​0x8161, STALL_FRONTEND_FLOW, Frontend stall cycles, flow control

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8161--STALL-FRONTEND-FLOW--Frontend-stall-cycles--flow-control>

##### `0x8161`, STALL\_FRONTEND\_FLOW, Frontend stall cycles, flow control

The counter counts each cycle counted by [STALL\_FRONTEND\_CPUBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8160--STALL-FRONTEND-CPUBOUND--Frontend-stall-cycles--processor-bound?lang=en#event_stall_frontend_cpubound) when the frontend is stalled on unavailability of prediction flow resources.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when the frontend is stalled on unavailability of prediction flow resources for any PE in the multithreaded processor.

> #### Note
>
> This event is not counting stalls due to mispredictions, but rather stalls when the frontend is unable to make a prediction.
