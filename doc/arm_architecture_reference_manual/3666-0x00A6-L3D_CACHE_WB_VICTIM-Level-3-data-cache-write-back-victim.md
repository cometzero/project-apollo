# ​0x00A6, L3D_CACHE_WB_VICTIM, Level 3 data cache write-back, victim

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x00A6--L3D-CACHE-WB-VICTIM--Level-3-data-cache-write-back--victim>

##### `0x00A6`, L3D\_CACHE\_WB\_VICTIM, Level 3 data cache write-back, victim

The counter counts each write-back counted by [L3D\_CACHE\_WB](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x002C--L3D-CACHE-WB--Level-3-data-cache-write-back?lang=en#event_l3d_cache_wb) that occurs because of a capacity eviction due to a line being allocated into the cache..

It is IMPLEMENTATION DEFINED whether this includes capacity evictions due to an agent other the PE counting the event. For example, a stashing request from outside of the PE, or an allocation due to another PE that shares the cache.

In all cases, the event is counted only if the eviction is also an [L3D\_CACHE\_WB](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x002C--L3D-CACHE-WB--Level-3-data-cache-write-back?lang=en#event_l3d_cache_wb) event. This means that, if the cache is shared, the eviction is counted only if it is attributable to the PE counting the event, as defined by [L3D\_CACHE\_WB](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x002C--L3D-CACHE-WB--Level-3-data-cache-write-back?lang=en#event_l3d_cache_wb).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
