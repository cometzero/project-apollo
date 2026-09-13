# ​0x8076, SVE_PRED_FULL_SPEC, Operation speculatively executed, SIMD predicated with all active elements

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8076--SVE-PRED-FULL-SPEC--Operation-speculatively-executed--SIMD-predicated-with-all-active-elements>

##### `0x8076`, SVE\_PRED\_FULL\_SPEC, Operation speculatively executed, SIMD predicated with all active elements

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated SIMD operation counted by [SVE\_PRED\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8074--SVE-PRED-SPEC--Operation-speculatively-executed--SIMD-predicated?lang=en#event_sve_pred_spec) where all elements are Active.

That is, all elements in the Governing predicate or predicates are all TRUE.

When FEAT\_SME is implemented, both SVE and SME operations with at least one Governing predicate operand are counted.

> #### Note
>
> For outer product instructions which are widening, predication is considered with respect to the input element size.
