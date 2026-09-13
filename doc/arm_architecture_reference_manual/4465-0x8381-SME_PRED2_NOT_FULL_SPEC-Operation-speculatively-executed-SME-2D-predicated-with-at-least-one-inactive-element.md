# ​0x8381, SME_PRED2_NOT_FULL_SPEC, Operation speculatively executed, SME 2D predicated with at least one inactive element

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8381--SME-PRED2-NOT-FULL-SPEC--Operation-speculatively-executed--SME-2D-predicated-with-at-least-one-inactive-element>

##### `0x8381`, SME\_PRED2\_NOT\_FULL\_SPEC, Operation speculatively executed, SME 2D predicated with at least one inactive element

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated 2D SME operation which targets the ZA array counted by [SME\_PRED2\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8384--SME-PRED2-SPEC--Operation-speculatively-executed--SME-2D-predicated?lang=en#event_sme_pred2_spec) where at least one element is Inactive.

That is, at least one element in the Governing predicates is FALSE.

For outer product instructions which are widening, predication is considered with respect to the input element size.
