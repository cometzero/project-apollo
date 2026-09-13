# ​0x8075, SVE_PRED_EMPTY_SPEC, Operation speculatively executed, SIMD predicated with no active elements

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8075--SVE-PRED-EMPTY-SPEC--Operation-speculatively-executed--SIMD-predicated-with-no-active-elements>

##### `0x8075`, SVE\_PRED\_EMPTY\_SPEC, Operation speculatively executed, SIMD predicated with no active elements

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated SIMD operation counted by [SVE\_PRED\_NOT\_FULL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8079--SVE-PRED-NOT-FULL-SPEC--Operation-speculatively-executed--SVE-predicated-with-at-least-one-inactive-element?lang=en#event_sve_pred_not_full_spec) where all elements are Inactive.

That is, all elements in the Governing predicate or predicates are FALSE.

When FEAT\_SME is implemented, both SVE and SME operations with at least one Governing predicate operand are counted.

> #### Note
>
> For outer product instructions which are widening, predication is considered with respect to the input element size.
