# ​0x8396, SME_ST_TILE_SPEC, SME predicated tile store

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8396--SME-ST-TILE-SPEC--SME-predicated-tile-store>

##### `0x8396`, SME\_ST\_TILE\_SPEC, SME predicated tile store

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that writes to memory counted by [SME\_LDST\_TILE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8394--SME-LDST-TILE-SPEC--SME-predicated-tile-load-store?lang=en#event_sme_ldst_tile_spec) that was due to an instruction with at least one governing predicate which is targeting the ZA array.

That is, due to any of the following instructions:

- SME2: ST1B (scalar plus scalar, tile slice), ST1D (scalar plus scalar, tile slice), ST1H (scalar plus scalar, tile slice), ST1Q, or ST1W (scalar plus scalar, tile slice).
