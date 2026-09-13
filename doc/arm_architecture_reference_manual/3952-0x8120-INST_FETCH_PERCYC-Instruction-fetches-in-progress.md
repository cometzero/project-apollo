# ​0x8120, INST_FETCH_PERCYC, Instruction fetches in progress

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8120--INST-FETCH-PERCYC--Instruction-fetches-in-progress>

##### `0x8120`, INST\_FETCH\_PERCYC, Instruction fetches in progress

The counter increments by the number of instruction fetches counted by [INST\_FETCH](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8124--INST-FETCH--Instruction-memory-access?lang=en#event_inst_fetch) in progress on each [Processor cycle](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacgcfhh).

The ratio [INST\_FETCH\_PERCYC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8120--INST-FETCH-PERCYC--Instruction-fetches-in-progress?lang=en#event_inst_fetch_percyc) ÷ [INST\_FETCH](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8124--INST-FETCH--Instruction-memory-access?lang=en#event_inst_fetch) is the mean duration of instruction fetches in [Processor cycles](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacgcfhh).
