# MHU Receiver registers

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers>

### MHU Receiver registers

The MHU Receiver (MHUR) registers include the register blocks that are part of the MHU Receiver.

The offsets of the blocks, within the MHU Receiver are IMPLEMENTATION DEFINED. However, we recommend the following offsets.

- When TrustZone (TZE) is implemented for the MHUR
  - 0x0\_0000 - Receiver Security Control (RSC) registers
  - 0x1\_0000 - Mailbox (MBX) registers
  - 0x2\_0000 - MHU Receiver RAS (RRAS) registers
- When TZE is not implemented for the MHUR
  - 0x0\_0000 - MBX registers
  - 0x1\_0000 - RRAS registers
