# ​0x8077, SVE_PRED_PARTIAL_SPEC, Operation speculatively executed, SIMD predicated with partially active elements

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8077--SVE-PRED-PARTIAL-SPEC--Operation-speculatively-executed--SIMD-predicated-with-partially-active-elements>

##### `0x8077`, SVE\_PRED\_PARTIAL\_SPEC, Operation speculatively executed, SIMD predicated with partially active elements

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated SIMD operation counted by [SVE\_PRED\_NOT\_FULL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8079--SVE-PRED-NOT-FULL-SPEC--Operation-speculatively-executed--SVE-predicated-with-at-least-one-inactive-element?lang=en#event_sve_pred_not_full_spec) where neither all elements are Active nor all elements are Inactive.

That is, all elements in the Governing predicate or predicates are neither all TRUE nor all FALSE.

When FEAT\_SME is implemented, both SVE and SME operations with at least one Governing predicate operand are counted.

> #### Note
>
> For outer product instructions which are widening, predication is considered with respect to the input element size.
