# ​0x80A1, SVE_LDNT_CONTIG_SPEC, Operation speculatively executed, SVE non-temporal contiguous load element

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A1--SVE-LDNT-CONTIG-SPEC--Operation-speculatively-executed--SVE-non-temporal-contiguous-load-element>

##### `0x80A1`, SVE\_LDNT\_CONTIG\_SPEC, Operation speculatively executed, SVE non-temporal contiguous load element

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory with a non-temporal hint counted by [SVE\_LDSTNT\_CONTIG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A0--SVE-LDSTNT-CONTIG-SPEC--Operation-speculatively-executed--SVE-non-temporal-contiguous-load-or-store-element?lang=en#event_sve_ldstnt_contig_spec) due to an SVE non-temporal contiguous element load instruction.

When FEAT\_SME is implemented, this includes operations due to SME non-temporal contiguous element load instructions operating on the SVE registers.
