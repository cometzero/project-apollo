# ​0x0024, STALL_BACKEND, No operation sent for execution due to the backend

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0024--STALL-BACKEND--No-operation-sent-for-execution-due-to-the-backend>

##### `0x0024`, STALL\_BACKEND, No operation sent for execution due to the backend

The counter counts each cycle counted by [CPU\_CYCLES](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0011--CPU-CYCLES--Cycle?lang=en#event_cpu_cycles) where Attributable instructions or operations for the PE are available to dispatch from the frontend to the backend, but no Attributable instruction or operation is sent for execution because the backend is unable to accept any of the instructions or operations available for the PE.

For example, the backend might be unable to accept operations because of a resource conflict or non-availability.

It is IMPLEMENTATION DEFINED whether the counter also counts each cycle counted by [CPU\_CYCLES](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0011--CPU-CYCLES--Cycle?lang=en#event_cpu_cycles) where no Attributable instructions or operations for the PE are available to dispatch from the frontend and the backend is unable to accept any instructions or operations for the PE.

The division between frontend and backend is IMPLEMENTATION DEFINED. For more information, see [STALL\_FRONTEND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0023--STALL-FRONTEND--No-operation-sent-for-execution-due-to-the-frontend?lang=en#event_stall_frontend). All [STALL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x003C--STALL--No-operation-sent-for-execution?lang=en#event_stall) events are counted at the same point in the pipeline.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts only if the stall condition is true for all the PEs in the multithreaded processor.

> #### Note
>
> In a single cycle, both the [STALL\_BACKEND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0024--STALL-BACKEND--No-operation-sent-for-execution-due-to-the-backend?lang=en#event_stall_backend) and [STALL\_FRONTEND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0023--STALL-FRONTEND--No-operation-sent-for-execution-due-to-the-frontend?lang=en#event_stall_frontend) events might be counted, if both the backend is unable to accept any operations and there are no operations available to issue from the frontend.

PMCEID1\_EL0[4] reads as 1 if this event is implemented and 0 otherwise.
