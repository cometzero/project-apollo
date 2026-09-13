# ​0x80A2, SVE_STNT_CONTIG_SPEC, Operation speculatively executed, SVE non-temporal contiguous store element

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A2--SVE-STNT-CONTIG-SPEC--Operation-speculatively-executed--SVE-non-temporal-contiguous-store-element>

##### `0x80A2`, SVE\_STNT\_CONTIG\_SPEC, Operation speculatively executed, SVE non-temporal contiguous store element

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that writes to memory with a non-temporal hint counted by [SVE\_LDSTNT\_CONTIG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A0--SVE-LDSTNT-CONTIG-SPEC--Operation-speculatively-executed--SVE-non-temporal-contiguous-load-or-store-element?lang=en#event_sve_ldstnt_contig_spec) due to an SVE non-temporal contiguous element store instruction.

When FEAT\_SME is implemented, this includes operations due to SME non-temporal contiguous element store instructions operating on the SVE registers.
