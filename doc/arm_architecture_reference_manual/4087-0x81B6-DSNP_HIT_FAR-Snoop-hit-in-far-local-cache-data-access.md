# ​0x81B6, DSNP_HIT_FAR, Snoop hit in far local cache, data access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B6--DSNP-HIT-FAR--Snoop-hit-in-far-local-cache--data-access>

##### `0x81B6`, DSNP\_HIT\_FAR, Snoop hit in far local cache, data access

The counter counts each snoop counted by [DSNP\_HIT](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B4--DSNP-HIT--Snoop-hit--data?lang=en#event_dsnp_hit) that hits in a cache outside the local PE cluster on the same device.

The event is counted by the PE generating the snoop, not the PE being snooped.
