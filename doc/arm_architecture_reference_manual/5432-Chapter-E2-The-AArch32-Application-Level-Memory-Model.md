# ​Chapter E2 The AArch32 Application Level Memory Model

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model>

### Chapter E2 The AArch32 Application Level Memory Model

This chapter gives an application level description of the memory model for software executing in AArch32 state. This means it describes the memory model for execution in EL0 when EL0 is using AArch32 in the following sections:

- [About the Arm memory model](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-1-About-the-Arm-memory-model?lang=en#cjacaffc)
- [Atomicity in the Arm architecture](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-2-Atomicity-in-the-Arm-architecture?lang=en#aa32chdhfcde)
- [Definition of the memory model](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-3-Definition-of-the-memory-model?lang=en#aa32chdbaghd)
- [Ordering of translation table walks](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-4-Ordering-of-translation-table-walks?lang=en#chdghdba)
- [Caches and memory hierarchy](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-5-Caches-and-memory-hierarchy?lang=en#cegecbbc)
- [Alignment support](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-6-Alignment-support?lang=en#aa32chdidcci)
- [Endian support](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-7-Endian-support?lang=en#cegiigdc)
- [Memory types and attributes](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-8-Memory-types-and-attributes?lang=en#aa32chddaiha)
- [Mismatched memory attributes](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-9-Mismatched-memory-attributes?lang=en#cegddhaj)
- [Synchronization and semaphores](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E2-The-AArch32-Application-Level-Memory-Model/-E2-10-Synchronization-and-semaphores?lang=en#cegdaeag)

> #### Note
>
> In this chapter, System register names usually link to the description of the register in [AArch32 System Register Descriptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G8-AArch32-System-Register-Descriptions?lang=en#autogen_registers_aarch32), for example [SCTLR](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G8-AArch32-System-Register-Descriptions/-G8-2-General-system-control-registers/-G8-2-127-SCTLR--System-Control-Register?lang=en#reg_aarch32_sctlr).
