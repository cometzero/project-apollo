# ​0x80A9, SVE_LD_MULTI_SPEC, Operation speculatively executed, SVE contiguous load multiple vector

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A9--SVE-LD-MULTI-SPEC--Operation-speculatively-executed--SVE-contiguous-load-multiple-vector>

##### `0x80A9`, SVE\_LD\_MULTI\_SPEC, Operation speculatively executed, SVE contiguous load multiple vector

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [SVE\_LDST\_MULTI\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A8--SVE-LDST-MULTI-SPEC--Operation-speculatively-executed--SVE-contiguous-load-or-store-multiple-vector?lang=en#event_sve_ldst_multi_spec) due to an SVE multiple vector contiguous structure load instruction.

When FEAT\_SME is implemented, this includes operations due to SME multiple vector contiguous load instructions operating on the SVE registers.
