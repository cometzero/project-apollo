# ​0x8351, STALL_BACKEND_GCSTLB, Backend stall cycles, GCS TLB

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8351--STALL-BACKEND-GCSTLB--Backend-stall-cycles--GCS-TLB>

##### `0x8351`, STALL\_BACKEND\_GCSTLB, Backend stall cycles, GCS TLB

The counter counts each cycle counted by [STALL\_BACKEND\_MEMBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8164--STALL-BACKEND-MEMBOUND--Backend-stall-cycles--memory-bound?lang=en#event_stall_backend_membound) when there is a demand data miss in a TLB.

The demand data miss must be due to translation of a GCS data read operation or GCS data write operation.

Implementation of this optional event requires implementing [L1GCS\_TLB](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8340--L1GCS-TLB--Level-1-GCS-TLB-access?lang=en#event_l1gcs_tlb) event.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when there is a demand data miss in a TLB for any PE in the multithreaded processor.
