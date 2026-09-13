# ​0x8385, SME_PRED2_EMPTY_SPEC, Operation speculatively executed, SME 2D predicated with no active elements

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8385--SME-PRED2-EMPTY-SPEC--Operation-speculatively-executed--SME-2D-predicated-with-no-active-elements>

##### `0x8385`, SME\_PRED2\_EMPTY\_SPEC, Operation speculatively executed, SME 2D predicated with no active elements

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated 2D SME operation which targets the ZA array counted by [SME\_PRED2\_NOT\_FULL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8381--SME-PRED2-NOT-FULL-SPEC--Operation-speculatively-executed--SME-2D-predicated-with-at-least-one-inactive-element?lang=en#event_sme_pred2_not_full_spec) where all elements are Inactive.

That is, all elements in the Governing predicates are FALSE.

For outer product instructions which are widening, predication is considered with respect to the input element size.
