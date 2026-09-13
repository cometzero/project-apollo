# ​0x8356, SVE_BITPERM_SPEC, Operation speculatively executed, SVE in-element permute

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8356--SVE-BITPERM-SPEC--Operation-speculatively-executed--SVE-in-element-permute>

##### `0x8356`, SVE\_BITPERM\_SPEC, Operation speculatively executed, SVE in-element permute

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) SVE permute operation counted by [SVE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8056--SVE-SPEC--Operation-speculatively-executed--SVE-data-processing?lang=en#event_sve_spec) due to an instruction that permutes bits within elements of a vector.

This includes operations which are due to the following instructions:

- SVE: `BDEP`, `BEXT`, or `BGRP`.
