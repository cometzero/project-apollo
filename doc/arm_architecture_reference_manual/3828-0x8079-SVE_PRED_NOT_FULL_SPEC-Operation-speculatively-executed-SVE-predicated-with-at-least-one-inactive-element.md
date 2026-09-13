# ​0x8079, SVE_PRED_NOT_FULL_SPEC, Operation speculatively executed, SVE predicated with at least one inactive element

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8079--SVE-PRED-NOT-FULL-SPEC--Operation-speculatively-executed--SVE-predicated-with-at-least-one-inactive-element>

##### `0x8079`, SVE\_PRED\_NOT\_FULL\_SPEC, Operation speculatively executed, SVE predicated with at least one inactive element

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated SIMD data-processing, load, or store operation counted by [SVE\_PRED\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8074--SVE-PRED-SPEC--Operation-speculatively-executed--SIMD-predicated?lang=en#event_sve_pred_spec) where at least one element is Inactive.

That is, at least one element in the Governing predicate or predicates is FALSE.

When FEAT\_SME is implemented, both SVE and SME operations with at least one Governing predicate operand are counted.

> #### Note
>
> For outer product instructions which are widening, predication is considered with respect to the input element size.
