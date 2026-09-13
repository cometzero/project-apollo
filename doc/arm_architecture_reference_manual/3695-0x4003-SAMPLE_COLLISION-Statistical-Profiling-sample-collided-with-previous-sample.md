# ​0x4003, SAMPLE_COLLISION, Statistical Profiling sample collided with previous sample

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4003--SAMPLE-COLLISION--Statistical-Profiling-sample-collided-with-previous-sample>

##### `0x4003`, SAMPLE\_COLLISION, Statistical Profiling sample collided with previous sample

The counter counts each time the sample interval counter reaches zero and is reloaded, and the sample collides with a previous sample.

For more information, see [‘Sample collisions’](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D17-The-Statistical-Profiling-Extension/-D17-3-Controlling-when-an-operation-is-sampled/-D17-3-7-Sample-collisions?lang=en#chdhjfja).

PMCEID0\_EL0[35] reads as 1 if this event is implemented and 0 otherwise.
