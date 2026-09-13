# ​0x0023, STALL_FRONTEND, No operation sent for execution due to the frontend

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0023--STALL-FRONTEND--No-operation-sent-for-execution-due-to-the-frontend>

##### `0x0023`, STALL\_FRONTEND, No operation sent for execution due to the frontend

The counter counts each cycle counted by [CPU\_CYCLES](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0011--CPU-CYCLES--Cycle?lang=en#event_cpu_cycles) where no Attributable instruction or operation was sent for execution and there was no Attributable instruction or operation available to dispatch for the PE from the frontend.

The division between frontend and backend is IMPLEMENTATION DEFINED. All [STALL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x003C--STALL--No-operation-sent-for-execution?lang=en#event_stall) events are counted at the same point in the pipeline.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts only if the stall condition is true for all the PEs in the multithreaded processor.

> #### Note
>
> - For a simplified pipeline model of Fetch-Decode-Issue-Execute-Retire, Arm recommends that the events are counted when instructions are dispatched from Decode to Issue.
> - In a single cycle, both the [STALL\_BACKEND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0024--STALL-BACKEND--No-operation-sent-for-execution-due-to-the-backend?lang=en#event_stall_backend) and [STALL\_FRONTEND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0023--STALL-FRONTEND--No-operation-sent-for-execution-due-to-the-frontend?lang=en#event_stall_frontend) events might be counted, if both the backend is unable to accept any operations and there are no operations available to issue from the frontend.

PMCEID1\_EL0[3] reads as 1 if this event is implemented and 0 otherwise.
