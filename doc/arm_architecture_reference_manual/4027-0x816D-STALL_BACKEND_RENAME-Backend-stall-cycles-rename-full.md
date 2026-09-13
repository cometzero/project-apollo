# ​0x816D, STALL_BACKEND_RENAME, Backend stall cycles, rename full

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x816D--STALL-BACKEND-RENAME--Backend-stall-cycles--rename-full>

##### `0x816D`, STALL\_BACKEND\_RENAME, Backend stall cycles, rename full

The counter counts each cycle counted by [STALL\_BACKEND\_CPUBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x816A--STALL-BACKEND-CPUBOUND--Backend-stall-cycles--processor-bound?lang=en#event_stall_backend_cpubound) when operations are available from the frontend but at least one is not ready to be sent to the backend because no rename register is available.

If this event is implemented and counts such stalls then the [STALL\_FRONTEND\_RENAME](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8163--STALL-FRONTEND-RENAME--Frontend-stall-cycles--rename-full?lang=en#event_stall_frontend_rename) event counts as zero.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when operations are available from the frontend but at least one is not ready to be sent to the backend because no rename register is available for any PE in the multithreaded processor.
