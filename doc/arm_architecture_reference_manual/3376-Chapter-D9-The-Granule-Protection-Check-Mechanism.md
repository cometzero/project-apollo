# ​Chapter D9 The Granule Protection Check Mechanism

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism>

### Chapter D9 The Granule Protection Check Mechanism

Any access, after all enabled translation stages, targets a *physical address* (PA) in one of the four physical address spaces. This chapter describes the *Granule Protection Check* (GPC) mechanism by which accesses to those PA spaces are checked. The GPC mechanism is added by the *Realm Management Extension* (RME) and includes the following:

- Mechanism to determine the protection information for a particular PA and PA space.
- Allocation and invalidation behavior for TLBs, data caches, and instruction caches.
- Configuration registers and descriptor formats for PA space protection information.

This chapter contains the following sections:

- [GPC behavior overview](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism/-D9-1-GPC-behavior-overview?lang=en#mdsec_gpc_behavior_overview)
- [GPC bypass windows](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism/-D9-2-GPC-bypass-windows?lang=en#mdsec_gpc_bypass_windows)
- [Granular Data Isolation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism/-D9-3-Granular-Data-Isolation?lang=en#mdsec_granular_data_isolation)
- [GPC faults](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism/-D9-4-GPC-faults?lang=en#mdsec_gpc_faults)
- [GPT caching and invalidation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism/-D9-5-GPT-caching-and-invalidation?lang=en#mdsec_gpt_caching_and_invalidation)
- [GPT formats](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism/-D9-6-GPT-formats?lang=en#mdsec_gpt_formats)
- [GPT lookup process](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism/-D9-7-GPT-lookup-process?lang=en#mdsec_gpt_lookup_process)
- [Explicit PAS control](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism/-D9-8-Explicit-PAS-control?lang=en#mdsec_explicit_pas_control)
