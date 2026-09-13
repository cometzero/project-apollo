# ​0x80C4, FP_SP_SCALE_OPS_SPEC, Scalable element arithmetic operations speculatively executed, largest type is single-precision floating-point

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80C4--FP-SP-SCALE-OPS-SPEC--Scalable-element-arithmetic-operations-speculatively-executed--largest-type-is-single-precision-floating-point>

##### `0x80C4`, FP\_SP\_SCALE\_OPS\_SPEC, Scalable element arithmetic operations speculatively executed, largest type is single-precision floating-point

The counter increments by *v* for each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) scalable element arithmetic operation, due to an instruction where the largest type was single-precision floating-point.

Where *v* is a value such that (*v*×(VL÷128)) is the number of arithmetic operations carried out by the operation or instruction which causes the counter to increment.

The counter does not count operations that are counted by [FP\_FIXED\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80C1--FP-FIXED-OPS-SPEC--Non-scalable-element-arithmetic-operations-speculatively-executed--floating-point?lang=en#event_fp_fixed_ops_spec) or [FP\_SCALE2\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80D0--FP-SCALE2-OPS-SPEC--Scalable-tile-arithmetic-operations-speculatively-executed--floating-point?lang=en#event_fp_scale2_ops_spec).
