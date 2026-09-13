# ​0x8354, SVE_CMP_IGRANULE_SPEC, Operation speculatively executed, SVE in-granule compare

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8354--SVE-CMP-IGRANULE-SPEC--Operation-speculatively-executed--SVE-in-granule-compare>

##### `0x8354`, SVE\_CMP\_IGRANULE\_SPEC, Operation speculatively executed, SVE in-granule compare

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) SVE in-granule comparison operation counted by [SVE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8056--SVE-SPEC--Operation-speculatively-executed--SVE-data-processing?lang=en#event_sve_spec) due to an instruction that detects or counts matching elements between segments in vectors.

This includes operations which are due to the following instructions:

- SVE: `MATCH`, `NMATCH`, or `HISTSEG`.
