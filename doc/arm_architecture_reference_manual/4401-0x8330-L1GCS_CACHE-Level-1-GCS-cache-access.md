# ​0x8330, L1GCS_CACHE, Level 1 GCS cache access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8330--L1GCS-CACHE--Level-1-GCS-cache-access>

##### `0x8330`, L1GCS\_CACHE, Level 1 GCS cache access

The counter counts each GCS data read operation or GCS data write operation that causes a cache access to at least a Level 1 cache.

Each access to a cache line is counted including the multiple accesses caused by single instructions such as `GCSPUSHX` or `GCSPOPX`. Each access to other Level 1 memory structures, for example refill buffers, write buffers, and write-back buffers, is also counted.

Accesses to a Level 1 cache due to a GCS hardware prefetcher as well are counted.

When there are separate GCS caching structures implemented:

- It is IMPLEMENTATION DEFINED whether accesses that result from cache maintenance instructions are counted.
- Accesses that only update the cache status information for a cache entry without accessing the content of the cache entry are not counted.
