# ​0x8384, SME_PRED2_SPEC, Operation speculatively executed, SME 2D predicated

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8384--SME-PRED2-SPEC--Operation-speculatively-executed--SME-2D-predicated>

##### `0x8384`, SME\_PRED2\_SPEC, Operation speculatively executed, SME 2D predicated

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 2D operation which targets the ZA array counted by [SVE\_PRED\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8074--SVE-PRED-SPEC--Operation-speculatively-executed--SIMD-predicated?lang=en#event_sve_pred_spec) due to an SME instruction with a Governing predicate operand that determines the Active elements.
