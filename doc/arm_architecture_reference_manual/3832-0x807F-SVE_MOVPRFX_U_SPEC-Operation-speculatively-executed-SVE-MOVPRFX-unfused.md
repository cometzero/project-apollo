# ​0x807F, SVE_MOVPRFX_U_SPEC, Operation speculatively executed, SVE MOVPRFX unfused

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x807F--SVE-MOVPRFX-U-SPEC--Operation-speculatively-executed--SVE-MOVPRFX-unfused>

##### `0x807F`, SVE\_MOVPRFX\_U\_SPEC, Operation speculatively executed, SVE MOVPRFX unfused

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation counted by [SVE\_MOVPRFX\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x807C--SVE-MOVPRFX-SPEC--Operation-speculatively-executed--SVE-MOVPRFX?lang=en#event_sve_movprfx_spec) where the `MOVPRFX` is not fused with the prefixed instruction.
