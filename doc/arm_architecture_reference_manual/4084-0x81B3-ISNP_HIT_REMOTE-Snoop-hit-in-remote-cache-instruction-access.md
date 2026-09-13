# ​0x81B3, ISNP_HIT_REMOTE, Snoop hit in remote cache, instruction access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B3--ISNP-HIT-REMOTE--Snoop-hit-in-remote-cache--instruction-access>

##### `0x81B3`, ISNP\_HIT\_REMOTE, Snoop hit in remote cache, instruction access

The counter counts each snoop counted by [ISNP\_HIT](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B0--ISNP-HIT--Snoop-hit--instruction?lang=en#event_isnp_hit) that hits in a cache on a remote device.

The event is counted by the PE generating the snoop, not the PE being snooped.
