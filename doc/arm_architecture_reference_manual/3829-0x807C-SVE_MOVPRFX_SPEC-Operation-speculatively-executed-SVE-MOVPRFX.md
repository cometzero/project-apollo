# ​0x807C, SVE_MOVPRFX_SPEC, Operation speculatively executed, SVE MOVPRFX

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x807C--SVE-MOVPRFX-SPEC--Operation-speculatively-executed--SVE-MOVPRFX>

##### `0x807C`, SVE\_MOVPRFX\_SPEC, Operation speculatively executed, SVE MOVPRFX

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation due to any of the following instructions:

- SVE: MOVPRFX.

The instruction is counted whether or not it is fused with the prefixed instruction.
