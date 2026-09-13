# ​0x0070, LD_SPEC, Operation speculatively executed, load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0070--LD-SPEC--Operation-speculatively-executed--load>

##### `0x0070`, LD\_SPEC, Operation speculatively executed, load

The counter counts each operation counted by [LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0072--LDST-SPEC--Operation-speculatively-executed--load-or-store?lang=en#event_ldst_spec) that is a load operation.

Operations due to [Memory-reading instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions) are counted as load operations.

It is IMPLEMENTATION DEFINED whether operations due to the prefetch instructions counted by [PRF\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8087--PRF-SPEC--Operation-speculatively-executed--prefetch?lang=en#event_prf_spec) are counted as load operations:

- If operations due to the prefetch instructions are counted as load operations, then they are counted by [LD\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0070--LD-SPEC--Operation-speculatively-executed--load?lang=en#event_ld_spec).
- Otherwise, if operations due to the prefetch instructions are not counted as load operations by [LD\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0070--LD-SPEC--Operation-speculatively-executed--load?lang=en#event_ld_spec), then it is further IMPLEMENTATION DEFINED which one of the following applies:
  - They are counted as data-processing operations.
  - They are counted by [LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0072--LDST-SPEC--Operation-speculatively-executed--load-or-store?lang=en#event_ldst_spec).

Arm recommends that if a prefetch operation is not implemented as a NOP and the [PRF\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8087--PRF-SPEC--Operation-speculatively-executed--prefetch?lang=en#event_prf_spec) event is not implemented, then the operation is counted as a load operation.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
