# ​0x812F, SAMPLE_FEED_LAT, Statistical Profiling sample taken, exceeding minimum latency

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x812F--SAMPLE-FEED-LAT--Statistical-Profiling-sample-taken--exceeding-minimum-latency>

##### `0x812F`, SAMPLE\_FEED\_LAT, Statistical Profiling sample taken, exceeding minimum latency

The counter counts each sample counted by [SAMPLE\_FEED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4001--SAMPLE-FEED--Statistical-Profiling-sample-taken?lang=en#event_sample_feed) that meets the sample latency filter constraints.

That is, each sample with a total latency greater than or equal to the minimum latency defined by [PMSLATFR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-16-PMSLATFR-EL1--Sampling-Latency-Filter-Register?lang=en#reg_aarch64_pmslatfr_el1).MINLAT are counted. The value of [PMSFCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-12-PMSFCR-EL1--Sampling-Filter-Control-Register?lang=en#reg_aarch64_pmsfcr_el1).FL is ignored when generating this event.

Samples that are removed by filtering, or discarded, and not written to the Profiling Buffer are counted.
