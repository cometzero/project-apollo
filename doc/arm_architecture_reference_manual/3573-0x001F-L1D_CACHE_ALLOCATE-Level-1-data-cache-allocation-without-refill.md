# ​0x001F, L1D_CACHE_ALLOCATE, Level 1 data cache allocation without refill

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001F--L1D-CACHE-ALLOCATE--Level-1-data-cache-allocation-without-refill>

##### `0x001F`, L1D\_CACHE\_ALLOCATE, Level 1 data cache allocation without refill

The counter counts each [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj) that writes an entire line into the Level 1 data or unified cache without fetching data from outside the Level 1 data or unified cache.

These are allocations of cache lines in the Level 1 data or unified cache that are not refills counted by [L1D\_CACHE\_REFILL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0003--L1D-CACHE-REFILL--Level-1-data-cache-refill?lang=en#event_l1d_cache_refill). For example:

- A write of an entire cache line from a coalescing write buffer.
- An operation such as `DC ZVA`.

The counter counts only [Memory-write operations](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj) Attributable to the PE counting the event, and, if the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT for the counter is 1, other PEs in the multithreaded implementation.

PMCEID0\_EL0[31] reads as 1 if this event is implemented and 0 otherwise.
