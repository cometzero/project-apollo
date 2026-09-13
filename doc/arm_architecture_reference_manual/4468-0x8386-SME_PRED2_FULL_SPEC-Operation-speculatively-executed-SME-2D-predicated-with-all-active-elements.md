# ​0x8386, SME_PRED2_FULL_SPEC, Operation speculatively executed, SME 2D predicated with all active elements

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8386--SME-PRED2-FULL-SPEC--Operation-speculatively-executed--SME-2D-predicated-with-all-active-elements>

##### `0x8386`, SME\_PRED2\_FULL\_SPEC, Operation speculatively executed, SME 2D predicated with all active elements

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated 2D SME operation which targets the ZA array counted by [SME\_PRED2\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8384--SME-PRED2-SPEC--Operation-speculatively-executed--SME-2D-predicated?lang=en#event_sme_pred2_spec) where all elements are Active.

That is, all elements in the Governing predicates are TRUE.

For outer product instructions which are widening, predication is considered with respect to the input element size.
