# ​0x0062, BUS_ACCESS_SHARED, Bus access, Normal, Cacheable, Shareable

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0062--BUS-ACCESS-SHARED--Bus-access--Normal--Cacheable--Shareable>

##### `0x0062`, BUS\_ACCESS\_SHARED, Bus access, Normal, Cacheable, Shareable

The counter counts each access counted by [BUS\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0019--BUS-ACCESS--Bus-access?lang=en#event_bus_access) that is Normal, Cacheable, Shareable.

> #### Note
>
> It is IMPLEMENTATION DEFINED how the PE translates the attributes from the translation table entry for a region to the attributes on the bus.
>
> In particular, a region of memory designated as Normal, Cacheable, Inner Shareable, Not Outer Shareable by a translation table entry, might be marked as either shareable or Non-shareable at the boundary of the PE and its closely-coupled caches. This depends on where the IMPLEMENTATION DEFINED boundary lies, between Inner and Outer Shareable.
>
> If the Inner Shareable extends beyond the PE boundary, and the bus indicates the distinction between Inner and Outer Shareable, then either is counted as shareable for the purposes of defining this event.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
