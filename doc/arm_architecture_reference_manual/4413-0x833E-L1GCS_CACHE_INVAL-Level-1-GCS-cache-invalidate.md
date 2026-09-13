# ​0x833E, L1GCS_CACHE_INVAL, Level 1 GCS cache invalidate

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x833E--L1GCS-CACHE-INVAL--Level-1-GCS-cache-invalidate>

##### `0x833E`, L1GCS\_CACHE\_INVAL, Level 1 GCS cache invalidate

The counter counts each invalidation of a cache line in a Level 1 GCS cache.

For example:

- Invalidation of a cache line because of a `GCSB` effect.
- Transfer of ownership of a cache line to another cache because of a coherency or refill request.

The counter does not count events if a cache refill of the Level 1 cache invalidates a line in the Level 1 cache.

> #### Note
>
> Software that uses this event must know whether the Level 1 cache is shared with other PEs. This event does not follow the general rule of Level 1 cache events of only counting Attributable events.
