# ​0x81B5, DSNP_HIT_NEAR, Snoop hit in near local cache, data access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B5--DSNP-HIT-NEAR--Snoop-hit-in-near-local-cache--data-access>

##### `0x81B5`, DSNP\_HIT\_NEAR, Snoop hit in near local cache, data access

The counter counts each snoop counted by [DSNP\_HIT](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B4--DSNP-HIT--Snoop-hit--data?lang=en#event_dsnp_hit) that hits in a cache outside of the cache hierarchy of this PE in the local PE cluster.

The event is counted by the PE generating the snoop, not the PE being snooped.
