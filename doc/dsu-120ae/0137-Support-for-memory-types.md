# Support for memory types

Source: <https://developer.arm.com/documentation/107721/0001/AXI-manager-interface/Support-for-memory-types>

### Support for memory types

The cores in the DSU-120AE DynamIQ™ cluster simplify the coherency logic by downgrading some memory types.

Normal memory that is marked as both Inner Write-Back Cacheable and Outer Write-Back Cacheable is cached in the core data caches and the L3 cache.

All other Normal memory types are treated as Non-cacheable and are sent on the requester interface as Normal Non-cacheable.
