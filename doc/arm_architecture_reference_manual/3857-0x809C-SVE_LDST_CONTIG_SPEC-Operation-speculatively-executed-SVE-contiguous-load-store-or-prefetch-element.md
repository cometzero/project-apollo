# ​0x809C, SVE_LDST_CONTIG_SPEC, Operation speculatively executed, SVE contiguous load, store, or prefetch element

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x809C--SVE-LDST-CONTIG-SPEC--Operation-speculatively-executed--SVE-contiguous-load--store--or-prefetch-element>

##### `0x809C`, SVE\_LDST\_CONTIG\_SPEC, Operation speculatively executed, SVE contiguous load, store, or prefetch element

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) SVE predictated single vector contiguous element load, store, or prefetch operation due to any of:

- A predicated single vector contiguous load or store instruction operating on the SVE registers.
- An SVE load and replicate `LD1R` or `LD1RQ` instruction.

When FEAT\_SME is implemented, this includes the following instructions:

- SME: `LD1B`, `LD1D`, `LD1H`, `LD1Q`, `LD1W`, `LDNT1B`, `LDNT1D`, `LDNT1H`, `LDNT1Q`, `ST1B`, `ST1D`, `ST1H`, `ST1Q`, `ST1W`, `STNT1B`, `STNT1D`, or `STNT1H`.
