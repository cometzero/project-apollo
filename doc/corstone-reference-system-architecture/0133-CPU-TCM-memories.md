# CPU TCM memories

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/CPU-TCM-memories>

### CPU TCM memories

The processors in CRSAS Ma1 are configured to implement Tightly Coupled Memories (TCM) for Instruction and Data. These memories reside in the following location from the perspective of each CPU core:

- 0x0000\_0000 to 0x00FF\_FFFF and 0x1000\_0000 to 0x10FF\_FFFF for Instruction TCM. Both regions are aliased, and each provides up to 16MB of TCM space.
- 0x2000\_0000 to 0x20FF\_FFFF and 0x3000\_0000 to 0x30FF\_FFFF for Data TCM. Both regions are aliased, and each provides up to 16MB of TCM space.

Each CPU has access to its own local TCMs through its private address and other CPUs TCMs through the Main Interconnect. A CPU does not have access to its own TCMs through the Main Interconnect. Other managers on the Main interconnect have access to the TCMs. A TCM DMA subordinate interface to allow expansion managers to access the TCMs is provided. For more information, see [TCM subordinate interface](/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en "A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.").

All TCMs always start at the base address of each region. Any memory areas in that region that are not used are reserved and return a bus error response if accessed.
