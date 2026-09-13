# ​0x8122, SAMPLE_FEED_DS, Statistical Profiling sample taken, selected Data Source

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8122--SAMPLE-FEED-DS--Statistical-Profiling-sample-taken--selected-Data-Source>

##### `0x8122`, SAMPLE\_FEED\_DS, Statistical Profiling sample taken, selected Data Source

The counter counts each SPE sample that is a load operations where [PMSDSFR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-10-PMSDSFR-EL1--Sampling-Data-Source-Filter-Register?lang=en#reg_aarch64_pmsdsfr_el1)[`S`] is 1 and `S` is bits [5:0] of the sampled Data Source.

The values of [PMSFCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-12-PMSFCR-EL1--Sampling-Filter-Control-Register?lang=en#reg_aarch64_pmsfcr_el1).FDS are ignored when generating this event.

Samples that are removed by filtering, or discarded, and not written to the Profiling Buffer are counted.
