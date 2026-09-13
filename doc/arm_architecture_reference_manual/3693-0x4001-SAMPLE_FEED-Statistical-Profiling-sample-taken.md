# ​0x4001, SAMPLE_FEED, Statistical Profiling sample taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4001--SAMPLE-FEED--Statistical-Profiling-sample-taken>

##### `0x4001`, SAMPLE\_FEED, Statistical Profiling sample taken

The counter counts each time the sample interval counter reaches zero and is reloaded, and the sample does not collide with the previous sample.

Samples that are removed by filtering, or discarded, and not written to the Profiling Buffer are counted.

PMCEID0\_EL0[33] reads as 1 if this event is implemented and 0 otherwise.
