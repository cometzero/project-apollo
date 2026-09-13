# ​0x80FB, ASE_SVE_INT_DOT_SPEC, Integer operation speculatively executed, Advanced SIMD or SVE dot-product

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80FB--ASE-SVE-INT-DOT-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-dot-product>

##### `0x80FB`, ASE\_SVE\_INT\_DOT\_SPEC, Integer operation speculatively executed, Advanced SIMD or SVE dot-product

The counter counts each integer dot product operation counted by [INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8040--INT-SPEC--Integer-operation-speculatively-executed?lang=en#event_int_spec) due to any of the following A64 instructions:

- When FEAT\_DotProd is implemented, Advanced SIMD: SDOT or UDOT.
- When FEAT\_I8MM is implemented, Advanced SIMD: SUDOT (by element) or USDOT.
- SVE: SDOT, SUDOT, UDOT, or USDOT.
- SVE2: CDOT, SDOT, or UDOT.

It is IMPLEMENTATION DEFINED which integer dot product operations are counted in AArch32 state.
