# ​0x80F9, ASE_INT_DOT_SPEC, Operation speculatively executed, Advanced SIMD integer dot-product

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80F9--ASE-INT-DOT-SPEC--Operation-speculatively-executed--Advanced-SIMD-integer-dot-product>

##### `0x80F9`, ASE\_INT\_DOT\_SPEC, Operation speculatively executed, Advanced SIMD integer dot-product

The counter counts each integer dot product operation counted by [ASE\_SVE\_INT\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80FB--ASE-SVE-INT-DOT-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-dot-product?lang=en#event_ase_sve_int_dot_spec) due to any of the following A64 instructions:

- When FEAT\_DotProd is implemented, Advanced SIMD: SDOT or UDOT.
- When FEAT\_I8MM is implemented, Advanced SIMD: SUDOT (by element) or USDOT.

It is IMPLEMENTATION DEFINED which integer dot product operations are counted in AArch32 state.
