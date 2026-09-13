# ​0x808C, FPASE_LDST_REG_SPEC, Operation speculatively executed, SIMD&FP register load or store

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x808C--FPASE-LDST-REG-SPEC--Operation-speculatively-executed--SIMD-FP-register-load-or-store>

##### `0x808C`, FPASE\_LDST\_REG\_SPEC, Operation speculatively executed, SIMD&FP register load or store

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from or writes to memory due to any of the following A64 instructions:

- Scalar: LDP (SIMD&FP), LDR (SIMD&FP), STP (SIMD&FP), or STR (SIMD&FP).
- Advanced SIMD: LD1, LD1R, LDNP, LDP, LDR, LDUR, ST1, STNP, STP, STR, or STUR.
- When FEAT\_LRCPC3 is implemented, Advanced SIMD: LDAP1, LDAPUR, STL1, or STLUR.

It is IMPLEMENTATION DEFINED which load and store operations are counted in AArch32 state.
