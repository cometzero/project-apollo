# ​0x809E, SVE_ST_CONTIG_SPEC, Operation speculatively executed, SVE contiguous store element

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x809E--SVE-ST-CONTIG-SPEC--Operation-speculatively-executed--SVE-contiguous-store-element>

##### `0x809E`, SVE\_ST\_CONTIG\_SPEC, Operation speculatively executed, SVE contiguous store element

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that writes to memory counted by [SVE\_LDST\_CONTIG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x809C--SVE-LDST-CONTIG-SPEC--Operation-speculatively-executed--SVE-contiguous-load--store--or-prefetch-element?lang=en#event_sve_ldst_contig_spec) due to any of:

- A predicated single vector contiguous store instruction operating on the SVE registers.

When FEAT\_SME is implemented, this includes the following instructions:

- SME: `ST1B`, `ST1D`, `ST1H`, `ST1Q`, `ST1W`, `STNT1B`, `STNT1D`, `STNT1H`, and `STNT1Q`.
