# ​0x8350, STALL_BACKEND_L1GCS, Backend stall cycles, Level 1 GCS cache

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8350--STALL-BACKEND-L1GCS--Backend-stall-cycles--Level-1-GCS-cache>

##### `0x8350`, STALL\_BACKEND\_L1GCS, Backend stall cycles, Level 1 GCS cache

The counter counts each cycle counted by [STALL\_BACKEND\_MEMBOUND](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8164--STALL-BACKEND-MEMBOUND--Backend-stall-cycles--memory-bound?lang=en#event_stall_backend_membound) when there is a demand data miss in a first level cache.

The demand data miss must be due to either GCS data read operation or GCS data write operation.

The counter does not count the cycle if any of the following are true:

- The [STALL\_BACKEND\_L2D](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8166--STALL-BACKEND-L2D--Backend-stall-cycles--level-2-data-cache?lang=en#event_stall_backend_l2d) event is implemented and there is a demand data miss in the second level of data or unified cache, meaning the [STALL\_BACKEND\_L2D](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8166--STALL-BACKEND-L2D--Backend-stall-cycles--level-2-data-cache?lang=en#event_stall_backend_l2d) event counts the cycle.
- There is a demand data miss in the last level of data or unified cache within the PE clock domain, meaning the [STALL\_BACKEND\_MEM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4005--STALL-BACKEND-MEM--Memory-stall-cycles?lang=en#event_stall_backend_mem) event counts the cycle.

Implementation of this optional event requires that the first level cache is implemented within the PE clock domain and is not the last level cache within the PE clock domain.

Implementation of this optional event requires implementing [L1GCS\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8330--L1GCS-CACHE--Level-1-GCS-cache-access?lang=en#event_l1gcs_cache) event.

For a multithreaded processor implementation, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT is 1, then the counter counts when there is a demand data miss in a first level cache for any PE in the multithreaded processor.

> #### Note
>
> It is possible that both the events [STALL\_BACKEND\_L1GCS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8350--STALL-BACKEND-L1GCS--Backend-stall-cycles--Level-1-GCS-cache?lang=en#event_stall_backend_l1gcs) and [STALL\_BACKEND\_L1D](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8165--STALL-BACKEND-L1D--Backend-stall-cycles--level-1-data-cache?lang=en#event_stall_backend_l1d) events may be counted on a same cycle.
