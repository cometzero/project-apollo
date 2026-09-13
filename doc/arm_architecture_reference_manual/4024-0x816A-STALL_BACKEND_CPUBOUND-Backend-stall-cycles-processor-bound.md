# ​0x816A, STALL_BACKEND_CPUBOUND, Backend stall cycles, processor bound

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x816A--STALL-BACKEND-CPUBOUND--Backend-stall-cycles--processor-bound>

##### `0x816A`, STALL\_BACKEND\_CPUBOUND, Backend stall cycles, processor bound

The counter counts each cycle counted by [STALL\_BACKEND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0024--STALL-BACKEND--No-operation-sent-for-execution-due-to-the-backend?lang=en#event_stall_backend) when the backend is stalled on a processor resource, not including memory.

The counter counts each stall that occurs when a backend processor resource is busy. This includes the stalls counted by [STALL\_BACKEND\_RENAME](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x816D--STALL-BACKEND-RENAME--Backend-stall-cycles--rename-full?lang=en#event_stall_backend_rename), and any other IMPLEMENTATION DEFINED processor resource stalls.

It does not include stalls that are counted by [STALL\_BACKEND\_MEMBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8164--STALL-BACKEND-MEMBOUND--Backend-stall-cycles--memory-bound?lang=en#event_stall_backend_membound), although both events might count on the same cycle counted by [STALL\_BACKEND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0024--STALL-BACKEND--No-operation-sent-for-execution-due-to-the-backend?lang=en#event_stall_backend) if there are both memory and processor-resource stall conditions active.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when the backend is stalled on a processor resource, not including memory for any PE in the multithreaded processor.
