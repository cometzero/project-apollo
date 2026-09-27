# System interconnect infrastructure

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/System-interconnect-infrastructure>

### System interconnect infrastructure

The system interconnect infrastructure provides a bus infrastructure that transfers memory mapped access from bus managers to subordinates in the system. CRSAS Ma1 defines two key interconnects that form the System Interconnect and they are:

Main Interconnect
:   This interconnect is expected to provide the highest amount of bus throughput, and is primarily, but not exclusively, for code and data accesses that targets memories or high throughput interfaces. For example:

    - In-subsystem volatile memories
    - Flash, DRAM controllers or ROM that reside outside the system
    - Other high throughput devices.

    While the performance and protocol of the interconnect is IMPLEMENTATION DEFINED, we recommend that this interconnect is implemented to match the throughput capability of the processor. The Main Interconnect provides access support for all memory regions that are not private to the processors. However, access to the following regions are forwarded to the Peripheral Interconnect:

    - 0x4000\_0000 to 0x5FFF\_FFFF.
    - 0xE010\_0000 to 0xFFFF\_FFFF.

Peripheral Interconnect
:   This interconnect is expected to provide access to lower performance peripherals. For example:

    - System and Watchdog Timers,
    - System and other security Configuration Registers
    - Power control logic

    A Cortex-M MVE based processor has direct interface to access this Interconnect. Any access that does not reside in the following region must be routed to the Main interconnect:

    - 0x4000\_0000 to 0x5FFF\_FFFF.
    - 0xE010\_0000 to 0xFFFF\_FFFF.

    While the performance and protocol of the interconnect is IMPLEMENTATION DEFINED, we recommend that this interconnect is implemented to have a lower throughput performance compared to Main Interconnect and support a bus protocol that match those needed by the peripherals. The latency of the interface is also expected to be reduced.

The interconnect must be able to achieve the following:

- Transfer the following key properties of the access, from a manager to a subordinate, which is required to ensure that any security-related infrastructure can have all the necessary information to make decisions on access rights.

  - Security attribute indicating an access is marked as Secure or Non-secure.
  - The privilege level of the access, which is either privileged or unprivileged, or of a similar type.
  - Bus access address, and read/write attribute, and optionally, manager identity.
- Complete an access that has been issued. At completion of an access, minimally communicate as a response that the access is successful or has failed.
- Support the ability to atomically read and modify a memory location. For example, through the implementation of read lock and write conditional type exclusive memory access.

The Interconnect resides across PD\_SYS and potentially across PD\_AON and even PD\_MGMT if it exists. The interconnect runs primarily on SYSCLK.

TCM Interconnect
:   This interconnect provides access to the Tightly Coupled Memories (TCM) that are internal to CPU<n> from

    - TCM subordinate interface
    - Main interconnect
    - The DMA

The TCM interconnects follows the mapping and properties of the [TCM subordinate interface](/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en "A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.").

- **[ACC\_WAIT Control](/documentation/102803/0000/Functional-Description/System-interconnect-infrastructure/ACC-WAIT-Control?lang=en)**
   CRSAS Ma1 provides a set of controls to let you add access control gates or block access to the system expansion interfaces.
