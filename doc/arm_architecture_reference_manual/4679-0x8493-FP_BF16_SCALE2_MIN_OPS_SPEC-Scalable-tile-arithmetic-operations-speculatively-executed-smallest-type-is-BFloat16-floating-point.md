# ​0x8493, FP_BF16_SCALE2_MIN_OPS_SPEC, Scalable tile arithmetic operations speculatively executed, smallest type is BFloat16 floating-point

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8493--FP-BF16-SCALE2-MIN-OPS-SPEC--Scalable-tile-arithmetic-operations-speculatively-executed--smallest-type-is-BFloat16-floating-point>

##### `0x8493`, FP\_BF16\_SCALE2\_MIN\_OPS\_SPEC, Scalable tile arithmetic operations speculatively executed, smallest type is BFloat16 floating-point

The counter increments by *v* for each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) scalable tile arithmetic operation, due to an instruction where the smallest type was BFloat16 floating-point.

Where *v* is a value such that (*v*×(VL÷128)²) is the number of arithmetic operations carried out by the operation or instruction which causes the counter to increment.

The counter does not count operations that are counted by [FP\_FIXED\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80C1--FP-FIXED-OPS-SPEC--Non-scalable-element-arithmetic-operations-speculatively-executed--floating-point?lang=en#event_fp_fixed_ops_spec) or [FP\_SCALE\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80C0--FP-SCALE-OPS-SPEC--Scalable-element-arithmetic-operations-speculatively-executed--floating-point?lang=en#event_fp_scale_ops_spec).
