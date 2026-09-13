# ​Chapter B2 The AArch64 Application Level Memory Model

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model>

### Chapter B2 The AArch64 Application Level Memory Model

This chapter gives an application level view of the memory model. It contains the following sections:

- [About the Arm memory model](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-1-About-the-Arm-memory-model?lang=en#chdddghg)
- [Atomicity in the Arm architecture](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-2-Atomicity-in-the-Arm-architecture?lang=en#chdhfcde)
- [Ordering requirements defined by the formal concurrency model](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-3-Ordering-requirements-defined-by-the-formal-concurrency-model?lang=en#beifddeh)
- [Additional ordering requirements outside of the scope of the formal concurrency model](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-4-Additional-ordering-requirements-outside-of-the-scope-of-the-formal-concurrency-model?lang=en#sec_additional_ordering_requirements_outside_formal_concurrency_model)
- [Restrictions on the effects of speculation](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-5-Restrictions-on-the-effects-of-speculation?lang=en#chdhjgda)
- [Memory barriers](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-6-Memory-barriers?lang=en#beigfafg)
- [Caches and memory hierarchy](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-7-Caches-and-memory-hierarchy?lang=en#chddgjhd)
- [Alignment support](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-8-Alignment-support?lang=en#chdidcci)
- [Endian support](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-9-Endian-support?lang=en#chdfjgfj)
- [Memory types and attributes](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-10-Memory-types-and-attributes?lang=en#chddaiha)
- [Mismatched memory attributes](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-11-Mismatched-memory-attributes?lang=en#chdghffd)
- [Synchronization and semaphores](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-12-Synchronization-and-semaphores?lang=en#chdcgdja)

> #### Note
>
> In this chapter, System register names usually link to the description of the register in [AArch64 System Register Descriptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions?lang=en#autogen_registers_aarch64), for example. [SCTLR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-174-SCTLR-EL1--System-Control-Register--EL1-?lang=en#reg_aarch64_sctlr_el1).
