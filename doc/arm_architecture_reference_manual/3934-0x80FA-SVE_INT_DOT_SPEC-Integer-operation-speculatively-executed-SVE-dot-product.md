# ​0x80FA, SVE_INT_DOT_SPEC, Integer operation speculatively executed, SVE dot-product

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80FA--SVE-INT-DOT-SPEC--Integer-operation-speculatively-executed--SVE-dot-product>

##### `0x80FA`, SVE\_INT\_DOT\_SPEC, Integer operation speculatively executed, SVE dot-product

The counter counts each integer dot product operation counted by [ASE\_SVE\_INT\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80FB--ASE-SVE-INT-DOT-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-dot-product?lang=en#event_ase_sve_int_dot_spec) due to any of the following instructions:

- SVE: SDOT, SUDOT, UDOT, or USDOT.
- SVE2: CDOT, SDOT, or UDOT.
