# ​0x816F, STALL_BACKEND_MEMCPYSET, Backend stall cycles, Memory Copy or Set operation

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x816F--STALL-BACKEND-MEMCPYSET--Backend-stall-cycles--Memory-Copy-or-Set-operation>

##### `0x816F`, STALL\_BACKEND\_MEMCPYSET, Backend stall cycles, Memory Copy or Set operation

The counter counts each cycle counted by [STALL\_BACKEND\_MEMBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8164--STALL-BACKEND-MEMBOUND--Backend-stall-cycles--memory-bound?lang=en#event_stall_backend_membound) when the backend is processing an Memory Copy or Set instruction.

The Memory Copy instructions are CPY and CPYF. The Memory Set instructions are SET and SETG.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when the backend is processing an Memory Copy or Set instruction for any PE in the multithreaded processor.
