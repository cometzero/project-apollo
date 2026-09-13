# ​0x837C, SME_INT_DOT_SPEC, Operation speculatively executed, SME integer dot product

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x837C--SME-INT-DOT-SPEC--Operation-speculatively-executed--SME-integer-dot-product>

##### `0x837C`, SME\_INT\_DOT\_SPEC, Operation speculatively executed, SME integer dot product

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer dot product operation counted by [SE\_INT\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x837D--SE-INT-DOT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer-dot-product?lang=en#event_se_int_dot_spec) due to any of the following instructions:

- SME2: SDOT, SUDOT, SUVDOT, SVDOT, UDOT, USDOT, USVDOT, or UVDOT.
