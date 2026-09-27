# Peripheral Interconnect Expansion interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Peripheral-Interconnect-Expansion-interfaces>

### Peripheral Interconnect Expansion interfaces

CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces from the Peripheral Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system that is expected to require lower latency access to peripherals.

For more information, see [System interconnect infrastructure](/documentation/102803/0000/Functional-Description/System-interconnect-infrastructure?lang=en "The system interconnect infrastructure provides a bus infrastructure that transfers memory mapped access from bus managers to subordinates in the system. CRSAS Ma1 defines two key interconnects that form the System Interconnect and they are:").

The AMBA protocol used for this interface can either be AHB5 or AXI5 and must at least support the following properties:

- 32-bit address
- 32-bit or 64-bit data
- Synchronous to SYSSYSCLK
- On the nWARMRESETSYS reset
- TrustZone Support enabled

We recommend that these interfaces are 32-bit wide and use the AHB5 protocol.

The types of Manager and Subordinate Expansion interfaces on the Peripheral Interconnect are as follows:

Manager Peripheral Expansion interface
:   This interface provides access to other subordinates in the system and is mapped to the following address range:

    - 0x4010\_0000 to 0x47FF\_FFFF
    - 0x4810\_0000 to 0x4FFF\_FFFF
    - 0x5010\_0000 to 0x57FF\_FFFF
    - 0x5810\_0000 to 0x5FFF\_FFFF
    - 0xE020\_0000 to 0xEFFF\_FFFF
    - 0xF020\_0000 to 0xFFFF\_FFFF

    There can be zero or more such interfaces on the subsystem. If there are no such interfaces, all access to the preceding address range it targets responds with bus error. Additionally, if any implemented interface is not used or any of the preceding region is not implemented, a default subordinate must be used to respond with decode error. If there are more than one such interfaces, it is IMPLEMENTATION DEFINED how the preceding address range is divided across the interfaces. If implemented all these interfaces must export information to allow a debug access to be distinguished from an access by another manager in the system. We recommend that one such interface is provided in an implementation of the subsystem.

Subordinate Peripheral Expansion interface
:   This interface provides access to the Peripheral bus from expansion managers. This interface can be used to access all memory mapped regions in the system except to regions private to the processors. However, we recommend that this interface is not used to access areas outside the following memory mapped regions because of potential memory throughput limitations due to bus protocol and bus width conversion incurred at implementation:

    - 0x4000\_0000 to 0x4FFF\_FFFF
    - 0x5000\_0000 to 0x5FFF\_FFFF
    - 0xE010\_0000 to 0xEFFF\_FFFF
    - 0xF010\_0000 to 0xFFFF\_FFFF

    We recommend that one such interface is provided in an implementation of the subsystem. If any implemented interface is not used, the interface must be tied to idle.
