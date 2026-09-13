# ​0x8322, L3D_CACHE_REFILL_PERCYC, Level 3 data or unified cache refills in progress

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8322--L3D-CACHE-REFILL-PERCYC--Level-3-data-or-unified-cache-refills-in-progress>

##### `0x8322`, L3D\_CACHE\_REFILL\_PERCYC, Level 3 data or unified cache refills in progress

The counter increments by the number of Level 3 data or unified cache refills counted by [L3D\_CACHE\_REFILL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x002A--L3D-CACHE-REFILL--Level-3-data-cache-refill?lang=en#event_l3d_cache_refill) in progress on each [Processor cycle](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacgcfhh).

The ratio [L3D\_CACHE\_REFILL\_PERCYC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8322--L3D-CACHE-REFILL-PERCYC--Level-3-data-or-unified-cache-refills-in-progress?lang=en#event_l3d_cache_refill_percyc) ÷ [L3D\_CACHE\_REFILL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x002A--L3D-CACHE-REFILL--Level-3-data-cache-refill?lang=en#event_l3d_cache_refill) is the mean duration of Level 3 data or unified cache refills in [Processor cycles](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacgcfhh).
