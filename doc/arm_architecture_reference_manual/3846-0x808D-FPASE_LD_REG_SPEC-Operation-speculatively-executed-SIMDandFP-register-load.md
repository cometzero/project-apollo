# ​0x808D, FPASE_LD_REG_SPEC, Operation speculatively executed, SIMD&FP register load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x808D--FPASE-LD-REG-SPEC--Operation-speculatively-executed--SIMD-FP-register-load>

##### `0x808D`, FPASE\_LD\_REG\_SPEC, Operation speculatively executed, SIMD&FP register load

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [FPASE\_LDST\_REG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x808C--FPASE-LDST-REG-SPEC--Operation-speculatively-executed--SIMD-FP-register-load-or-store?lang=en#event_fpase_ldst_reg_spec) due to any of the following A64 instructions:

- Scalar: LDP (SIMD&FP) or LDR (SIMD&FP).
- Advanced SIMD: LD1, LD1R, LDNP, LDP, LDR, or LDUR.
- When FEAT\_LRCPC3 is implemented, Advanced SIMD: LDAP1 or LDAPUR.

It is IMPLEMENTATION DEFINED which load operations are counted in AArch32 state.
