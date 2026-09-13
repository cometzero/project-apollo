# ​0x8074, SVE_PRED_SPEC, Operation speculatively executed, SIMD predicated

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8074--SVE-PRED-SPEC--Operation-speculatively-executed--SIMD-predicated>

##### `0x8074`, SVE\_PRED\_SPEC, Operation speculatively executed, SIMD predicated

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicated SIMD operation.

All of the following SVE operations are counted as predicated SIMD operations:

- Data-processing or load operations that write to one or more SVE Z vector destination registers under a Governing predicate using either zeroing or merging predication.
- Predicated stores of one or more SVE Z vector registers.

It is IMPLEMENTATION DEFINED whether data-processing operations due to instructions with a single Governing predicate operand that determines the Active elements which do not write to any SVE Z vector destination registers using either zeroing or merging predication are counted. For example, INCP.

Operations where all predicates are FALSE which result in no effective change in the architectural state are counted.

When FEAT\_SPE is implemented, Arm recommends this event is implemented consistently with the PRED field in the SVE data-processing format Operation Type packet.

All speculatively executed SME operations due to instructions with at least one Governing predicate operand that determines the Active elements are counted as predicated SIMD operations.

> #### Note
>
> For outer product instructions which are widening, predication is considered with respect to the input element size.
