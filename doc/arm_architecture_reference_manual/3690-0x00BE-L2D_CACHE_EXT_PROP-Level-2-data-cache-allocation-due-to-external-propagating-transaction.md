# ​0x00BE, L2D_CACHE_EXT_PROP, Level 2 data cache allocation due to external propagating transaction

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x00BE--L2D-CACHE-EXT-PROP--Level-2-data-cache-allocation-due-to-external-propagating-transaction>

##### `0x00BE`, L2D\_CACHE\_EXT\_PROP, Level 2 data cache allocation due to external propagating transaction

The counter counts each operation that writes into the level 2 data cache that is initiated by an external propagating transaction.

These are allocations of cache lines in the Level 2 data cache that are not refills counted by [L2D\_CACHE\_REFILL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0017--L2D-CACHE-REFILL--Level-2-data-cache-refill?lang=en#event_l2d_cache_refill). This includes allocations triggered by:

- A memory update on another PE with an associated store shared hint.
- A stashing memory update from a device.
