# ​0x00B9, L1D_CACHE_EXT_PROP, Level 1 data cache allocation due to external propagating transaction

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x00B9--L1D-CACHE-EXT-PROP--Level-1-data-cache-allocation-due-to-external-propagating-transaction>

##### `0x00B9`, L1D\_CACHE\_EXT\_PROP, Level 1 data cache allocation due to external propagating transaction

The counter counts each operation that writes into the level 1 data cache that is initiated by an external propagating transaction.

These are allocations of cache lines in the Level 1 data cache that are not refills counted by [L1D\_CACHE\_REFILL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0003--L1D-CACHE-REFILL--Level-1-data-cache-refill?lang=en#event_l1d_cache_refill). This includes allocations triggered by:

- A memory update on another PE with an associated store shared hint.
- A stashing memory update from a device.
