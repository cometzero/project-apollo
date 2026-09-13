# ​0x80AA, SVE_ST_MULTI_SPEC, Operation speculatively executed, SVE contiguous store multiple vector

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80AA--SVE-ST-MULTI-SPEC--Operation-speculatively-executed--SVE-contiguous-store-multiple-vector>

##### `0x80AA`, SVE\_ST\_MULTI\_SPEC, Operation speculatively executed, SVE contiguous store multiple vector

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that writes to memory counted by [SVE\_LDST\_MULTI\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A8--SVE-LDST-MULTI-SPEC--Operation-speculatively-executed--SVE-contiguous-load-or-store-multiple-vector?lang=en#event_sve_ldst_multi_spec) due to an SVE multiple vector contiguous structure store instruction.

When FEAT\_SME is implemented, this includes operations due to SME multiple vector contiguous store instructions operating on the SVE registers.
