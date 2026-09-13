# ​0x837D, SE_INT_DOT_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD integer dot product

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x837D--SE-INT-DOT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer-dot-product>

##### `0x837D`, SE\_INT\_DOT\_SPEC, Operation speculatively executed, Advanced SIMD, SVE, or SME SIMD integer dot product

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer dot product operation counted by [SE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8379--SE-INT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer--data-processing?lang=en#event_se_int_spec) due to any of the following A64 instructions:

- When FEAT\_DotProd is implemented, Advanced SIMD: SDOT or UDOT.
- When FEAT\_I8MM is implemented, Advanced SIMD: SUDOT or USDOT.
- SVE: SDOT, SUDOT, UDOT, or USDOT.
- SVE2: CDOT, SDOT, or UDOT.
- SME2: SDOT, SUDOT, SUVDOT, SVDOT, UDOT, USDOT, USVDOT, or UVDOT.

That is, each operation counted by [ASE\_INT\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F9--ASE-INT-DOT-SPEC--Operation-speculatively-executed--Advanced-SIMD-integer-dot-product?lang=en#event_ase_int_dot_spec), [SVE\_INT\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80FA--SVE-INT-DOT-SPEC--Integer-operation-speculatively-executed--SVE-dot-product?lang=en#event_sve_int_dot_spec), or [SME\_INT\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x837C--SME-INT-DOT-SPEC--Operation-speculatively-executed--SME-integer-dot-product?lang=en#event_sme_int_dot_spec).
