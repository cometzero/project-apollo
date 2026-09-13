# ​0x0038, REMOTE_ACCESS_RD, Access to a remote device, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0038--REMOTE-ACCESS-RD--Access-to-a-remote-device--read>

##### `0x0038`, REMOTE\_ACCESS\_RD, Access to a remote device, read

The counter counts each access counted by [REMOTE\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0031--REMOTE-ACCESS--Access-to-a-remote-device?lang=en#event_remote_access) that is a [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega).

PMCEID1\_EL0[24] reads as 1 if this event is implemented and 0 otherwise.
