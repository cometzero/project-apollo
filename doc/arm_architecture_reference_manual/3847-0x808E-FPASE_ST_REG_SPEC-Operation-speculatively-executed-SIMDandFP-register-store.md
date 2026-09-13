# ​0x808E, FPASE_ST_REG_SPEC, Operation speculatively executed, SIMD&FP register store

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x808E--FPASE-ST-REG-SPEC--Operation-speculatively-executed--SIMD-FP-register-store>

##### `0x808E`, FPASE\_ST\_REG\_SPEC, Operation speculatively executed, SIMD&FP register store

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that writes to memory counted by [FPASE\_LDST\_REG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x808C--FPASE-LDST-REG-SPEC--Operation-speculatively-executed--SIMD-FP-register-load-or-store?lang=en#event_fpase_ldst_reg_spec) due to any of the following A64 instructions:

- Scalar: STP (SIMD&FP) or STR (SIMD&FP).
- Advanced SIMD: ST1, STNP, STP, STR, or STUR.
- When FEAT\_LRCPC3 is implemented, Advanced SIMD: STL1 or STLUR.

It is IMPLEMENTATION DEFINED which store operations are counted in AArch32 state.
