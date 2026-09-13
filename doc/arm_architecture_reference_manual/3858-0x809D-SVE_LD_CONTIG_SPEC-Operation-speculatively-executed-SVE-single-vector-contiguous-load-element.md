# ​0x809D, SVE_LD_CONTIG_SPEC, Operation speculatively executed, SVE single vector contiguous load element

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x809D--SVE-LD-CONTIG-SPEC--Operation-speculatively-executed--SVE-single-vector-contiguous-load-element>

##### `0x809D`, SVE\_LD\_CONTIG\_SPEC, Operation speculatively executed, SVE single vector contiguous load element

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [SVE\_LDST\_CONTIG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x809C--SVE-LDST-CONTIG-SPEC--Operation-speculatively-executed--SVE-contiguous-load--store--or-prefetch-element?lang=en#event_sve_ldst_contig_spec) due to any of:

- A predicated single vector contiguous load instruction operating on the SVE registers.
- An SVE load and replicate `LD1R` or `LD1RQ` instruction.

When FEAT\_SME is implemented, this includes the following instructions:

- SME: `LD1B`, `LD1D`, `LD1H`, `LD1Q`, `LD1W`, `LDNT1B`, `LDNT1D`, or `LDNT1H`.
