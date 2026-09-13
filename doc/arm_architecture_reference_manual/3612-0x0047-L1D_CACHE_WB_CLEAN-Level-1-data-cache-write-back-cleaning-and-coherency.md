# ​0x0047, L1D_CACHE_WB_CLEAN, Level 1 data cache write-back, cleaning and coherency

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0047--L1D-CACHE-WB-CLEAN--Level-1-data-cache-write-back--cleaning-and-coherency>

##### `0x0047`, L1D\_CACHE\_WB\_CLEAN, Level 1 data cache write-back, cleaning and coherency

The counter counts each write-back counted by [L1D\_CACHE\_WB](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0015--L1D-CACHE-WB--Level-1-data-cache-write-back?lang=en#event_l1d_cache_wb) that occurs because of a coherency operation made by another PE or, optionally, the execution of a cache maintenance instruction..

It is IMPLEMENTATION DEFINED whether the transfer of a dirty cache line from the Level 1 data cache of this PE to the data cache of another PE due to a hardware coherency operation is counted when the dirty cache line is not also written back to a Level 2 cache or memory.

In all cases, the event is counted only if the write-back is also an [L1D\_CACHE\_WB](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0015--L1D-CACHE-WB--Level-1-data-cache-write-back?lang=en#event_l1d_cache_wb) event. This means that, if the cache is shared, the write-back is counted only if it is attributable to the PE counting the event, as defined by [L1D\_CACHE\_WB](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0015--L1D-CACHE-WB--Level-1-data-cache-write-back?lang=en#event_l1d_cache_wb).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
