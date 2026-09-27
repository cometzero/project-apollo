# Main Interconnect Expansion interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Main-Interconnect-Expansion-interfaces>

### Main Interconnect Expansion interfaces

CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.

For more information, see [System interconnect infrastructure](/documentation/102803/0000/Functional-Description/System-interconnect-infrastructure?lang=en "The system interconnect infrastructure provides a bus infrastructure that transfers memory mapped access from bus managers to subordinates in the system. CRSAS Ma1 defines two key interconnects that form the System Interconnect and they are:").

The AMBA protocol used for this interface can either be AHB5 or AXI5 and must at least support the following properties:

- 32-bit address
- 32-bit, 64-bit, or 128-bit data
- Synchronous to SYSSYSCLK
- On the nWARMRESETSYS reset
- TrustZone Support enabled

We recommend that these interfaces are 64-bit or 128-bit wide and use the AXI5 protocol.

The types of Manager and Subordinate Expansion interfaces on the Main Interconnect are as follows:

Manager Code Main Expansion interface
:   This interface provides access to Code Memory and is mapped to the following address range:

    - 0x0100\_0000 to 0x09FF\_FFFF
    - 0x1100\_0000 to 0x19FF\_FFFF

    There must be at least one such interface on the subsystem. If there are more than one such interfaces, it is IMPLEMENTATION DEFINED how the preceding address range is divided across the interfaces. If any implemented interface is not used or any of the preceding region is not implemented, a default subordinate must be used to respond with bus error. This interface must export information to allow a debug access to be distinguished from an access by another manager in the system. We recommend that one such interface is provided in an implementation of the subsystem.

Manager Main Expansion interface
:   This interface provides access to other subordinates in the system and is mapped to the following address range:

    - 0x2800\_0000 to 0x2FFF\_FFFF
    - 0x3800\_0000 to 0x3FFF\_FFFF
    - 0x6000\_0000 to 0xDFFF\_FFFF

    There can be zero or more such interfaces on the subsystem. If there are no such interfaces, all access to the above address range results in decode error. decodes error. Additionally, if any implemented interface is not used or any of the preceding regions is not implemented, a default subordinate must be used to respond to the access targeting the interface and any address region not implemented with decode error. If there are more than one such interfaces, it is IMPLEMENTATION DEFINED how the preceding address range is divided across the interfaces. If implemented, all these interfaces must export information to allow a debug access to be distinguished from an access by another manager in the system. We recommend that one such interface is provided in an implementation of the subsystem.

Subordinate Main Expansion interface
:   This interface provides access to system from expansion managers. This interface can be used to access all memory mapped regions in the system except for regions private to the processors. We recommend that one such interface is provided in an implementation of the subsystem. If any implemented interface is not used, the interface must be tied to idle.
