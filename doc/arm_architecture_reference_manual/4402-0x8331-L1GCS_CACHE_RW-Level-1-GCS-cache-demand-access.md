# ​0x8331, L1GCS_CACHE_RW, Level 1 GCS cache demand access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8331--L1GCS-CACHE-RW--Level-1-GCS-cache-demand-access>

##### `0x8331`, L1GCS\_CACHE\_RW, Level 1 GCS cache demand access

The counter counts each access counted by [L1GCS\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8330--L1GCS-CACHE--Level-1-GCS-cache-access?lang=en#event_l1gcs_cache) that is due to a demand Memory-read operation or demand Memory-write operation.

This includes accesses made by Speculatively executed instructions.

Arm recommends that this event is implemented if event [L1GCS\_CACHE\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8332--L1GCS-CACHE-HWPRF--Level-1-GCS-cache-hardware-prefetch?lang=en#event_l1gcs_cache_hwprf) is implemented.
