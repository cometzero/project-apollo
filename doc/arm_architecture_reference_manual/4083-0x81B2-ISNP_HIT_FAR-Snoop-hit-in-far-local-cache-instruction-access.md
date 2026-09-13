# ​0x81B2, ISNP_HIT_FAR, Snoop hit in far local cache, instruction access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B2--ISNP-HIT-FAR--Snoop-hit-in-far-local-cache--instruction-access>

##### `0x81B2`, ISNP\_HIT\_FAR, Snoop hit in far local cache, instruction access

The counter counts each snoop counted by [ISNP\_HIT](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B0--ISNP-HIT--Snoop-hit--instruction?lang=en#event_isnp_hit) that hits in a cache outside the local PE cluster on the same device.

The event is counted by the PE generating the snoop, not the PE being snooped.
