# ​0x4002, SAMPLE_FILTRATE, Statistical Profiling sample taken and not removed by filtering

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4002--SAMPLE-FILTRATE--Statistical-Profiling-sample-taken-and-not-removed-by-filtering>

##### `0x4002`, SAMPLE\_FILTRATE, Statistical Profiling sample taken and not removed by filtering

The counter counts each sample counted by [SAMPLE\_FEED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4001--SAMPLE-FEED--Statistical-Profiling-sample-taken?lang=en#event_sample_feed) that is not removed by filtering.

Sample records that are not removed by filtering, but are discarded before being written to the Profiling Buffer because of a Profiling Buffer management event or because Discard mode is implemented and enabled, are counted.

PMCEID0\_EL0[34] reads as 1 if this event is implemented and 0 otherwise.
