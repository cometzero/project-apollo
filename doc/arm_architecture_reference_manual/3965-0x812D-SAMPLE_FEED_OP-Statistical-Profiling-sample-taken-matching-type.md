# ​0x812D, SAMPLE_FEED_OP, Statistical Profiling sample taken, matching type

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x812D--SAMPLE-FEED-OP--Statistical-Profiling-sample-taken--matching-type>

##### `0x812D`, SAMPLE\_FEED\_OP, Statistical Profiling sample taken, matching type

The counter counts each sample counted by [SAMPLE\_FEED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4001--SAMPLE-FEED--Statistical-Profiling-sample-taken?lang=en#event_sample_feed) that meets the sample type filter constraints.

The sample type filter constraints are specified by [PMSFCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-12-PMSFCR-EL1--Sampling-Filter-Control-Register?lang=en#reg_aarch64_pmsfcr_el1).TYPE and, if FEAT\_SPE\_EFT is implemented, [PMSFCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-12-PMSFCR-EL1--Sampling-Filter-Control-Register?lang=en#reg_aarch64_pmsfcr_el1).TYPEm.

The value of [PMSFCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-12-PMSFCR-EL1--Sampling-Filter-Control-Register?lang=en#reg_aarch64_pmsfcr_el1).FT is ignored when generating this event.

No event is generated if the type filter constraint controls are all zero.

Samples that are removed by filtering, or discarded, and not written to the Profiling Buffer are counted.
