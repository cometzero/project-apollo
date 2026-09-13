# ​0x812E, SAMPLE_FEED_EVENT, Statistical Profiling sample taken, matching events

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x812E--SAMPLE-FEED-EVENT--Statistical-Profiling-sample-taken--matching-events>

##### `0x812E`, SAMPLE\_FEED\_EVENT, Statistical Profiling sample taken, matching events

The counter counts each sample counted by [SAMPLE\_FEED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4001--SAMPLE-FEED--Statistical-Profiling-sample-taken?lang=en#event_sample_feed) that meets the Events packet filter constraints.

That is, each sample with all the events in the filter sets defined by [PMSEVFR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-11-PMSEVFR-EL1--Sampling-Event-Filter-Register?lang=en#reg_aarch64_pmsevfr_el1) and, if implemented, [PMSNEVFR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-17-PMSNEVFR-EL1--Sampling-Inverted-Event-Filter-Register?lang=en#reg_aarch64_pmsnevfr_el1) are counted. The values of [PMSFCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-7-Statistical-Profiling-Extension-registers/-D24-7-12-PMSFCR-EL1--Sampling-Filter-Control-Register?lang=en#reg_aarch64_pmsfcr_el1).{FnE,FE} are ignored when generating this event.

Samples that are removed by filtering, or discarded, and not written to the Profiling Buffer are counted.
