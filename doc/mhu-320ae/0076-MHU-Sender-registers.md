# MHU Sender registers

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers>

### MHU Sender registers

The MHU Sender registers include the register blocks that are part of the MHU Sender.

The offsets of the blocks, within the MHU Sender are IMPLEMENTATION DEFINED. However, we recommend the following offsets.

- When TrustZone (TZE) is implemented for the MHUS
  - 0x0\_0000 - Sender Security Control (SSC) registers
  - 0x1\_0000 - Postbox (PBX) registers
  - 0x2\_0000 - MHU Sender RAS (SRAS) registers
- When TZE is not implemented for the MHUS
  - 0x0\_0000 - PBX registers
  - 0x1\_0000 - SRAS registers
