# ​0x8387, SME_PRED2_PARTIAL_SPEC, Operation speculatively executed, SME 2D predicated with partially active elements

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8387--SME-PRED2-PARTIAL-SPEC--Operation-speculatively-executed--SME-2D-predicated-with-partially-active-elements>

##### `0x8387`, SME\_PRED2\_PARTIAL\_SPEC, Operation speculatively executed, SME 2D predicated with partially active elements

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated 2D SME operation which targets the ZA array counted by [SME\_PRED2\_NOT\_FULL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8381--SME-PRED2-NOT-FULL-SPEC--Operation-speculatively-executed--SME-2D-predicated-with-at-least-one-inactive-element?lang=en#event_sme_pred2_not_full_spec) where neither all elements are Active nor all elements are Inactive.

That is, the elements in the Governing predicates are neither all TRUE nor all FALSE.

For outer product instructions which are widening, predication is considered with respect to the input element size.
