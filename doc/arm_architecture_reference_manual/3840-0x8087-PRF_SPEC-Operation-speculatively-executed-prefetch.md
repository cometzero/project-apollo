# ​0x8087, PRF_SPEC, Operation speculatively executed, prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8087--PRF-SPEC--Operation-speculatively-executed--prefetch>

##### `0x8087`, PRF\_SPEC, Operation speculatively executed, prefetch

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) prefetch operation due to any of the following A64 instructions:

- Scalar: PRFM, PRFUM, or RPRFM.
- SVE: PRFB, PRFD, PRFH, or PRFW.

It is IMPLEMENTATION DEFINED which prefetch operations are counted in AArch32 state.
