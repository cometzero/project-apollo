# ​Chapter G5 The AArch32 Virtual Memory System Architecture

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture>

### Chapter G5 The AArch32 Virtual Memory System Architecture

This chapter describes the A-profile AArch32 *Virtual Memory System Architecture* (VMSA). It includes the following sections:

- [About VMSAv8-32](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-1-About-VMSAv8-32?lang=en#chdgjbea)
- [The effects of disabling address translation stages on VMSAv8-32 behavior](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-2-The-effects-of-disabling-address-translation-stages-on-VMSAv8-32-behavior?lang=en#chdhjbij)
- [Translation tables](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-3-Translation-tables?lang=en#chdfehah)
- [The VMSAv8-32 Short-descriptor translation table format](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-4-The-VMSAv8-32-Short-descriptor-translation-table-format?lang=en#cfbddghf)
- [The VMSAv8-32 Long-descriptor translation table format](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-5-The-VMSAv8-32-Long-descriptor-translation-table-format?lang=en#chdebich)
- [Memory access control](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-6-Memory-access-control?lang=en#chdiggbh)
- [Memory region attributes](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-7-Memory-region-attributes?lang=en#chdbdaai)
- [Translation Lookaside Buffers](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-8-Translation-Lookaside-Buffers?lang=en#chdbfdih)
- [TLB maintenance requirements](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-9-TLB-maintenance-requirements?lang=en#chdegjea)
- [Caches in VMSAv8-32](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-10-Caches-in-VMSAv8-32?lang=en#beijache)
- [VMSAv8-32 memory aborts](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-11-VMSAv8-32-memory-aborts?lang=en#caccbjcj)
- [Exception reporting in a VMSAv8-32 implementation](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-12-Exception-reporting-in-a-VMSAv8-32-implementation?lang=en#chdiaafi)
- [Address translation instructions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-13-Address-translation-instructions?lang=en#beiegcha)
- [Pseudocode description of VMSAv8-32 memory system operations](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-14-Pseudocode-description-of-VMSAv8-32-memory-system-operations?lang=en#chdgcgdb)
- [About the System registers for VMSAv8-32](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-15-About-the-System-registers-for-VMSAv8-32?lang=en#beicccif)
- [Functional grouping of VMSAv8-32 System registers](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture/-G5-16-Functional-grouping-of-VMSAv8-32-System-registers?lang=en#cbheafhd)

> #### Note
>
> This chapter must be read with [The AArch32 System Level Memory Model](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G4-The-AArch32-System-Level-Memory-Model?lang=en#chdihfbb).
