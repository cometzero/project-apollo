# ​0x4000, SAMPLE_POP, Statistical Profiling sample population

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4000--SAMPLE-POP--Statistical-Profiling-sample-population>

##### `0x4000`, SAMPLE\_POP, Statistical Profiling sample population

The counter counts each operation that might be sampled, whether or not the operation was sampled.

The counter does not count when profiling is disabled.

PMCEID0\_EL0[32] reads as 1 if this event is implemented and 0 otherwise.
