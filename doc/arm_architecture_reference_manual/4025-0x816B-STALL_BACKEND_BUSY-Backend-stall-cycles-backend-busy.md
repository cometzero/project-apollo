# ​0x816B, STALL_BACKEND_BUSY, Backend stall cycles, backend busy

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x816B--STALL-BACKEND-BUSY--Backend-stall-cycles--backend-busy>

##### `0x816B`, STALL\_BACKEND\_BUSY, Backend stall cycles, backend busy

The counter counts each cycle counted by [STALL\_BACKEND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0024--STALL-BACKEND--No-operation-sent-for-execution-due-to-the-backend?lang=en#event_stall_backend) when operations are available from the frontend but the backend is not able to accept an operation because an execution unit is busy.

For example a complex operation unit such as a divider is executing a previous operation and cannot accept a new operation.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when operations are available from the frontend but the backend is not able to accept an operation because an execution unit is busy for any PE in the multithreaded processor.
