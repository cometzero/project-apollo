# ​0x8320, L1D_CACHE_REFILL_PERCYC, Level 1 data or unified cache refills in progress

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8320--L1D-CACHE-REFILL-PERCYC--Level-1-data-or-unified-cache-refills-in-progress>

##### `0x8320`, L1D\_CACHE\_REFILL\_PERCYC, Level 1 data or unified cache refills in progress

The counter increments by the number of Level 1 data or unified cache refills counted by [L1D\_CACHE\_REFILL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0003--L1D-CACHE-REFILL--Level-1-data-cache-refill?lang=en#event_l1d_cache_refill) in progress on each [Processor cycle](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacgcfhh).

The ratio [L1D\_CACHE\_REFILL\_PERCYC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8320--L1D-CACHE-REFILL-PERCYC--Level-1-data-or-unified-cache-refills-in-progress?lang=en#event_l1d_cache_refill_percyc) ÷ [L1D\_CACHE\_REFILL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0003--L1D-CACHE-REFILL--Level-1-data-cache-refill?lang=en#event_l1d_cache_refill) is the mean duration of Level 1 data or unified cache refills in [Processor cycles](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacgcfhh).
