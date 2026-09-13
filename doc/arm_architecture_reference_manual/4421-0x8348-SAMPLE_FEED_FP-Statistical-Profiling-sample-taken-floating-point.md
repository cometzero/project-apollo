# ​0x8348, SAMPLE_FEED_FP, Statistical Profiling sample taken, floating-point

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8348--SAMPLE-FEED-FP--Statistical-Profiling-sample-taken--floating-point>

##### `0x8348`, SAMPLE\_FEED\_FP, Statistical Profiling sample taken, floating-point

The counter counts each sample counted by [SAMPLE\_FEED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4001--SAMPLE-FEED--Statistical-Profiling-sample-taken?lang=en#event_sample_feed) that is a floating-point data-processing, load, or store operation.

The values of [PMSFCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-12-PMSFCR-EL1--Sampling-Filter-Control-Register?lang=en#reg_aarch64_pmsfcr_el1).{FP,FT} and, if FEAT\_SPE\_EFT is implemented, [PMSFCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-12-PMSFCR-EL1--Sampling-Filter-Control-Register?lang=en#reg_aarch64_pmsfcr_el1).FPm, are ignored when generating this event.

Samples that are removed by filtering, or discarded, and not written to the Profiling Buffer are counted.
