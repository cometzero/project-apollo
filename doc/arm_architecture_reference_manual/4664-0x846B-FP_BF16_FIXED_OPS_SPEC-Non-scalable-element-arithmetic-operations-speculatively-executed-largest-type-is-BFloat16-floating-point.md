# ​0x846B, FP_BF16_FIXED_OPS_SPEC, Non-scalable element arithmetic operations speculatively executed, largest type is BFloat16 floating-point

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x846B--FP-BF16-FIXED-OPS-SPEC--Non-scalable-element-arithmetic-operations-speculatively-executed--largest-type-is-BFloat16-floating-point>

##### `0x846B`, FP\_BF16\_FIXED\_OPS\_SPEC, Non-scalable element arithmetic operations speculatively executed, largest type is BFloat16 floating-point

The counter increments by *v* for each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) non-scalable element arithmetic operation, due to an instruction where the largest type was BFloat16 floating-point.

Where *v* is the number of arithmetic operations carried out by the operation or instruction which causes the counter to increment.

The counter does not count operations that are counted by [FP\_SCALE\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80C0--FP-SCALE-OPS-SPEC--Scalable-element-arithmetic-operations-speculatively-executed--floating-point?lang=en#event_fp_scale_ops_spec) or [FP\_SCALE2\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80D0--FP-SCALE2-OPS-SPEC--Scalable-tile-arithmetic-operations-speculatively-executed--floating-point?lang=en#event_fp_scale2_ops_spec).
