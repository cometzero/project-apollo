# ​0x815D, STALL_BACKEND_BUSY_SMCU, Backend stall cycles, SMCU busy

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x815D--STALL-BACKEND-BUSY-SMCU--Backend-stall-cycles--SMCU-busy>

##### `0x815D`, STALL\_BACKEND\_BUSY\_SMCU, Backend stall cycles, SMCU busy

The counter counts each cycle counted by [CPU\_CYCLES](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0011--CPU-CYCLES--Cycle?lang=en#event_cpu_cycles) when the backend is not able to accept an operation because the SMCU is busy, for any reason.

For example:

- The PE is stalled awaiting allocation of processing resources on an SMCU.
- The PE has been allocated processing resources on an SMCU. However, the SMCU cannot process operations at the rate at which they are issued by the PE in Streaming SVE mode.
