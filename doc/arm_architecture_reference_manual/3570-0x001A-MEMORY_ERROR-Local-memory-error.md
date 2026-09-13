# ​0x001A, MEMORY_ERROR, Local memory error

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001A--MEMORY-ERROR--Local-memory-error>

##### `0x001A`, MEMORY\_ERROR, Local memory error

The counter counts each occurrence of a memory error signaled by a memory closely coupled to this PE.

The definition of local memories is IMPLEMENTATION DEFINED but includes caches, tightly-coupled memories, and TLB arrays.

Memory error refers to a physical error detected by the hardware, such as a parity or ECC error. It includes errors that are correctable and those that are not. It does not include errors as defined in the architecture, such as MMU faults.

PMCEID0\_EL0[26] reads as 1 if this event is implemented and 0 otherwise.
