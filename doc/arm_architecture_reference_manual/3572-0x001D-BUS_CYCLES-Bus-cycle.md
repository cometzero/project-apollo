# ​0x001D, BUS_CYCLES, Bus cycle

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001D--BUS-CYCLES--Bus-cycle>

##### `0x001D`, BUS\_CYCLES, Bus cycle

The counter increments on every cycle of the interface at the boundary of the PE and its closely-coupled caches. Where this boundary lies with respect to any implemented caches is IMPLEMENTATION DEFINED.

> #### Note
>
> If the implementation clocks the external memory interface at the same rate as the processor hardware, then the counter counts every cycle.

PMCEID0\_EL0[29] reads as 1 if this event is implemented and 0 otherwise.
