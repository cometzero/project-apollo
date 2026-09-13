# ​0x8230, LOCAL_MEM, Access to memory attached to this device

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8230--LOCAL-MEM--Access-to-memory-attached-to-this-device>

##### `0x8230`, LOCAL\_MEM, Access to memory attached to this device

The counter counts each [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) or [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj) access to external memory attached to this device.

In a multi-socket system this means attached to the socket that contains the PE. For more information, see [REMOTE\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0031--REMOTE-ACCESS--Access-to-a-remote-device?lang=en#event_remote_access).

In systems where there multiple types of memory attached to this device with different performance characteristics, it is IMPLEMENTATION DEFINED whether accesses to all external memory types are counted by this event, or are classified as remote accesses and counted by [REMOTE\_MEM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8238--REMOTE-MEM--Access-to-memory-attached-to-a-remote-device?lang=en#event_remote_mem).

For example, in a system with an expansion memory connected to the device that has significantly higher latency than the main system memory, accesses to the main system memory might be counted by this event and accesses to the expansion memory by [REMOTE\_MEM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8238--REMOTE-MEM--Access-to-memory-attached-to-a-remote-device?lang=en#event_remote_mem).
