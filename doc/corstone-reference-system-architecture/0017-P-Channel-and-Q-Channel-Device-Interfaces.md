# P-Channel and Q-Channel Device Interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces>

### P-Channel and Q-Channel Device Interfaces

Each P-Channel or Q-Channel Device Interface independently allows external expansion logic to handshake with the system to ensure that:

For warm reset control
:   All external managers and subordinate interfaces in a Warm reset domain are in safe state and isolated from the cold reset domain before asserting Warm reset. It also allows external manager to request for a power domain to wake.

For clock control
:   All external dependent logic can prepare itself before the hierarchical gating of clocks.

During system integration, expansion logic that resides within a power or clock domain associated with each P-Channel or Q-Channel normally merges all P-Channel or Q-Channel interfaces within the expansion domain to drive each interface.

When merging, the following rules must be obeyed to prevent system deadlocks:

- All bus managers in the expansion system must, either individually or collectively have a full Q-Channel interface, or a P-Channel interface.

  Each Q-Channel interface must be able to deny a quiescence request if the logic that it controls has outstanding operations on the bus or is unable to enter quiescent state for any other reason. Similarly, each P-Channel interface must be able to deny a request to enter a different PSTATE if the logic is unable to enter the requested state. The exception is the WARM\_RST power state where manages are expected to suspend their activity cleanly, activate internal reset domain crossing protections and always accept the request.

  Each P-Channel interface for power control must be able to support all power states that the domain implements.
- All bus subordinates in the expansion system must, either individually or collectively have a Q-Channel or P-Channel interface that must be able to delay the acceptance of a quiescence request or a Power state request if the current bus operation is about to complete.

  The LPI interface must also be able to deny a quiescence request or a power state request if the logic that it controls has other outstanding operations that prevent it from entering quiescent or the requested state. The exception is the WARM\_RST power state where subordinates are expected to suspend their activity cleanly, activate internal reset domain crossing protections and always accept the request.
- You must sequence the Q-Channels associated with these external bus interfaces in such a way to ensure that all bus managers are in quiescent state before any bus subordinates are requested to enter quiescent state.

  Similarly, with P-Channels, you must ensure that all bus managers and subordinate of these interfaces can enter the new requested state in the right order depending on their dependencies before the P-Channel accepts entering that state.

  An implementation of the system can depend on external sequencing to be added by a system integrator to do this for their expansion logic, or alternatively, implement multiple Q-Channels or P-Channel interfaces for each domain to separately handshake managers, subordinates, and even intermediate components in the domain in sequence.

If a Q-Channel Device interface is not used, its associated QACTIVE and QDENY signals must be tied LOW and the QREQn output looped back into its QACCEPTn input. Similarly, if a P-Channel Device interface is not used, then its associated PACTIVE and PDENY must be tied LOW, and the PREQn output looped back into its PACCEPTn input.

> ### Note
>
> Not used means there is no consumer of the corresponding clock or power, this not to be confused with the case where the consumer of the corresponding clock or power has no LPI interface.

Individual signals of the Q-Channel Device interfaces are sometimes described as a vector. For example, a Q-Channel Device interface could have x bits for each signal. In this case, bit i of all signals within 0 to x-1 forms a single bit Q-Channel interface. For example, QACTIVE[1], QREQn[1], QACCEPTn[1] and QDENY[1] form a Q-Channel interface and there are x Q-Channel interfaces. When a Q-Channel device interface is defined as a vector in this document, unless otherwise stated, it means the following:

- QACTIVE[x-1:0] are considered as ORed together at the controller,
- Collectively all Q-Channel i has to enter Q\_STOPPED state before the entire interface is considered to be in the Q\_STOPPED state. And similarly, all Q-Channel i has to enter Q\_RUN state before the entire interface is considered to be in the Q\_RUN state.
- When transitioning the entire interface between Q\_RUN state to Q\_STOPPED state, if any of the individual bit i Q-Channel denies the transition, all other Q-Channel must also return to the original Q-Channel state.

When P-Channel Device interface is used, the P-Channel encoding replicates the PCK-600 PPU’s Device P-Channel bit assignment, with each DEVPACTIVE bit used to request entry to a Power mode and Operating mode, and DEVPSTATE vector representing the power mode being requested.

For more information, see Arm® CoreLink™ PCK-600 Power Control Kit Technical Reference Manual and Arm® Power Policy Unit Architecture Specification.

For more information on the Q-Channel and P-Channel protocol, see Low Power Interface Specification - Arm® Q-Channel and P-Channel Interfaces.

- **[Clock control Q-Channel device interfaces](/documentation/102803/0000/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Clock-control-Q-Channel-device-interfaces?lang=en)**
   CRSAS Ma1 defines a Q-Channel Device interface for each of the output clocks to allow expansion logic to control the availability of each clock output. These are used to support high-level clock gating. Each interface can either be single bit or a vector, and is IMPLEMENTATION DEFINED.
- **[Power Control Q-Channel and P-Channel Expansion Device interfaces](/documentation/102803/0000/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Power-Control-Q-Channel-and-P-Channel-Expansion-Device-interfaces?lang=en)**
   CRSAS Ma1 provides power control Q-Channel or P-Channel Device interfaces to allow expansion logic to handshake and coordinate the expansion logic power state.
- **[Power Control P-Channel Expansion Device Interfaces](/documentation/102803/0000/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Power-Control-P-Channel-Expansion-Device-Interfaces?lang=en)**
   CRSAS Ma1 provides power control P-Channel Device interfaces to allow expansion of existing power domain hierarchy with new power domains by coordinating allowed power states of external power domain in the power domain hierarchy.
- **[Power Control Wakeup Q-Channel Device interfaces](/documentation/102803/0000/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Power-Control-Wakeup-Q-Channel-Device-interfaces?lang=en)**
   CRSAS Ma1 provides power control Wakeup Q-Channel Device interfaces to allow expansion logic to request for specific power domains to power up. The Q-Channel interfaces and the domains they control are:
