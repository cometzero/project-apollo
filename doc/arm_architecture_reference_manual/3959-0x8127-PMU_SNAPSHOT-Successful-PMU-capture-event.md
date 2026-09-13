# ​0x8127, PMU_SNAPSHOT, Successful PMU capture event

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8127--PMU-SNAPSHOT--Successful-PMU-capture-event>

##### `0x8127`, PMU\_SNAPSHOT, Successful PMU capture event

The counter counts each PMU snapshot Capture event that was successful, that is, [PMSSCR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-22-PMSSCR-EL1--Performance-Monitors-Snapshot-Status-and-Capture-Register?lang=en#reg_aarch64_pmsscr_el1).NC is set to 0.

It is CONSTRAINED UNPREDICTABLE whether the counter counts successful Capture events when the PE is in Debug state.
