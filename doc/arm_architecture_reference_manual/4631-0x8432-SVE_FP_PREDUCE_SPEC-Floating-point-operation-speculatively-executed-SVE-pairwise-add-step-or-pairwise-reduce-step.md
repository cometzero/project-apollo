# ​0x8432, SVE_FP_PREDUCE_SPEC, Floating-point operation speculatively executed, SVE pairwise add step or pairwise reduce step

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8432--SVE-FP-PREDUCE-SPEC--Floating-point-operation-speculatively-executed--SVE-pairwise-add-step-or-pairwise-reduce-step>

##### `0x8432`, SVE\_FP\_PREDUCE\_SPEC, Floating-point operation speculatively executed, SVE pairwise add step or pairwise reduce step

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point pairwise add step or pairwise reduce step operation counted by [SVE\_FP\_VREDUCE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x803E--SVE-FP-VREDUCE-SPEC--Floating-point-operation-speculatively-executed--SVE-pairwise-or-reduction?lang=en#event_sve_fp_vreduce_spec) due to any of the following instructions:

- SVE2: FADDP, FMAXNMP, FMAXP, FMINNMP, or FMINP.
