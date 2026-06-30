# Overview of MHU-320AE

Source: <https://developer.arm.com/documentation/107612/0001/Overview-of-MHU-320AE>

### Overview of MHU-320AE

Arm® CoreLink™ MHU-320AE Message Handling Unit facilitates interrupt-based communication between processing elements executing independent software stacks.

MHU-320AE consists of MHU Sender and MHU Receiver blocks. Each of these blocks has a programming interface for enabling software access to the MHU, as well as interrupt wires to notify the system of events related to the transfer of messages by the MHU.

MHU-320AE implements the [Message Handling Unit Architecture version 3.0](https://developer.arm.com/documentation/aes0072/aa) with configurable support for every extension in the architecture, including:

- Doorbell Extension (DBE)
- First-In First-Out (FIFO) Extension (FE)
- Fast Channel Extension (FCE)
- Arm® TrustZone® Extension (TZE)
- Realm Management Extension (RME)

For more information about the architecture extensions, see the [Message Handling Unit Architecture version 3.0](https://developer.arm.com/documentation/aes0072/aa).

> ### Note
>
> MHU-320AE enables unidirectional communication between two processing elements. Separate MHU instances are expected to be used to enable full duplex communication.

### Functional safety support

You can configure Functional Safety (FuSa) support so that MHU-320AE can be used in safety critical systems and applications. When FuSa support is enabled, MHU-320AE uses the following protection mechanisms:

- Lock-step of core MHU logic blocks
- RAM protection
- AMBA® AXI5-Stream or ACE5-Lite interconnect protection
- AMBA external interface protection
- Q-Channel protection
- Systematic fault watchdog
- Clock and reset duplication
- Fault Management Unit (FMU)

For more information about the Functional Safety (FuSa) configuration parameter, see the Arm® CoreLink™ MHU-320AE Message Handling Unit Configuration and Integration Manual.
