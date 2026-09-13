# ​Appendix K8 Address Translation Examples

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K8-Address-Translation-Examples>

### Appendix K8 Address Translation Examples

This appendix gives examples of address translations using the translation regimes described in [The AArch64 Virtual Memory System Architecture](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture?lang=en#caciiijc) and [The AArch32 Virtual Memory System Architecture](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture?lang=en#chdbceda). It contains the following sections:

- [AArch64 Address translation examples](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K8-Address-Translation-Examples/-K8-1-AArch64-Address-translation-examples?lang=en#babffjef)
- [AArch32 Address translation examples](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K8-Address-Translation-Examples/-K8-2-AArch32-Address-translation-examples?lang=en#babjcfih)

> #### Note
>
> This chapter gives examples of translation table lookups for the Armv8 address translation stages. It does not define any part of the address translation mechanism. If any information in this appendix appears to contradict the information in [The AArch64 Virtual Memory System Architecture](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture?lang=en#caciiijc) or [The AArch32 Virtual Memory System Architecture](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture?lang=en#chdbceda) then the information in [The AArch64 Virtual Memory System Architecture](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture?lang=en#caciiijc) or [The AArch32 Virtual Memory System Architecture](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G5-The-AArch32-Virtual-Memory-System-Architecture?lang=en#chdbceda) must be taken as the definition of the required behavior.
