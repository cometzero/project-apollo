# ​0x8061, SVE_PERM_IGRANULE_SPEC, Operation speculatively executed, SVE intra-granule permute

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8061--SVE-PERM-IGRANULE-SPEC--Operation-speculatively-executed--SVE-intra-granule-permute>

##### `0x8061`, SVE\_PERM\_IGRANULE\_SPEC, Operation speculatively executed, SVE intra-granule permute

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) vector or predicate permute operation within a 128-bit vector granule or 16-bit predicate granule due to any of the following instructions:

- SVE: REVB, REVH, REVW, TRN1 (vectors), or TRN2 (vectors).
- SVE2: REVD.
