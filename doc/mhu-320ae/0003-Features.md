# Features

Source: <https://developer.arm.com/documentation/107612/0001/Overview-of-MHU-320AE/Features>

### Features

MHU-320AE provides services for message transfer through multiple channels and channel types, interrupt generation, registers, and programming.

MHU-320AE supports error detection and correction features. MHU-320AE provides flexibility during configuration allowing individual features to be added or removed, allowing the MHU to be tailored to specific use cases.

### Message transfer

MHU-320AE provides the following features for transferring messages:

- Support for the following channel types:
  - Up to 128 doorbell channels. Each channel holds 32 individual single-bit flags.
  - Up to 1024 32-bit fast channels or 512 64-bit fast channels
  - Up to 64 First In First Out (FIFO) channels holding up to 1024 bytes of data for each channel
- Support for different system topologies:
  - Choice of a monolithic, single domain MHU instantiation, or distributed instantiations
  - Separate clock and power Q-Channel interfaces for each domain for independent low-power control
  - Use of AXI5-Stream or ACE5-Lite as the communications interface between MHU Sender and MHU Receiver blocks

### Interrupt generation

MHU-320AE provides support for the following interrupt types:

- Postbox and mailbox combined interrupts
- Channel transfer interrupts
- Channel transfer acknowledge interrupts
- Fast channel group interrupts
- FIFO tidemark and flush interrupts

### Registers and programming

MHU-320AE provides the following programming features:

- Use of APB5 or ACE5-Lite as the programming interface separately in the MHU Sender and MHU Receiver
- TrustZone or Realm support for providing access security

### Error correction and containment

MHU-320AE provides the following error correction features:

- Arm® RASv1.1-architecture compliant error reporting for:
  - Software access errors
  - Error Correcting Code (ECC) errors
- Error recovery and fault handling interrupts.

For more information about RASv1.1 architecture, see the RAS System Architecture chapter of the [Arm® Architecture Reference Manual for A-profile architecture](https://developer.arm.com/documentation/ddi0487).

### Hardware error detection

Hardware error features are available only if Functional Safety (FuSa) support is enabled.

MHU-320AE provides the following hardware error detection features:

- Lock-step of core MHU logic blocks
- AMBA parity on ACE5-Lite, AXI5-Stream, APB5, and Q-Channel interfaces
- Duplicated reset and clock signals with consistency detection
- Duplicated interrupt outputs
- End-to-end Cyclic Redundancy Check (CRC) protection over AXI5-Stream and ACE5-Lite
- Fault Monitoring Unit (FMU) for error logging that can be placed together with the MHU Sender or MHU Receiver block or both
