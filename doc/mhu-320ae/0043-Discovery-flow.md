# Discovery flow

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/Discovery/Discovery-flow>

### Discovery flow

To verify that the pages relate to MHU-320AE registers, software can check these pointers against the discovery registers, which start at offset 0x0FD0 for each MHU page. These registers allow discovery of the MHU-320AE version as well as information whether the page contains MHU or FMU registers.

To discover the page type, software can:

1. Read from 0x0FE0 to determine the PIDR0.PART\_0 value.
2. Read from 0x0FE4 to determine the PIDR1.PART\_1 value.
3. Concatenate PART\_1 (4 bits) and PART\_0 (8 bits), to discover the 12-bit part number, PART\_1 || PART\_0. A value of:

- 0x0F7 indicates that this page contains MHU registers.
- 0x49C indicates that this page contains Sender FMU registers.
- 0x49D indicates that this page contains Receiver MHU registers.

The type of MHU page can be further determined by:

1. If a read from 0x0FBC returns non-zero data, this page contains MHU SRAS or RRAS registers.
2. If a read from 0x0FBC returns zero, read from 0x000 to determine the MHU block identifier:

- 0x0 indicates that this page contains Postbox registers
- 0x1 indicates that this page contains Mailbox registers
- 0x2 indicates that this page contains Sender Security Control registers
- 0x3 indicates that this page contains Receiver Security Control registers

When this information is known, software can obtain additional information from registers that are specific to each page, such as architecture version and the supported architectural features.

For more information on discovery and feature registers, see the [Message Handling Unit Architecture version 3.0](https://developer.arm.com/documentation/aes0072/aa).
