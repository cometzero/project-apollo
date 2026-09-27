# Expansion Power Control Dependency interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Expansion-Power-Control-Dependency-interface>

### Expansion Power Control Dependency interface

CRSAS Ma1 provides an optional set of 2, up to 4-bit width Q-Channel interfaces that allow external power domains to use the Power Dependency Control Matrix to keep power domains within the subsystem from entering a lower power state.

These signals are:

PDCMONQREQn[<PDCMQCHWIDTH-1>:0]
:   Power Dependency Control Matrix QREQn inputs.

    When each bit is set to ‘1’, it indicates that the external domain that drives it is in functional power mode.

PDCMONQACCEPTn[<PDCMQCHWIDTH-1>:0]
:   Power Dependency Control Matrix QACCEPTn outputs.

    Each bit acknowledges an associated bit on PDCMONQREQn by returning the request input value. This acts as a four-phase handshake so that the driver of each request bit can determine that the request has been seen by receiving unit.

PDCMRETQREQn[<PDCMQCHWIDTH-1>:0]
:   Power Dependency Control Matrix QREQn inputs.

    When each bit is set to ‘1’, it indicates that the external domain that drives it is in functional power mode.

PDCMRETQACCEPTn[<PDCMQCHWIDTH-1>:0]
:   Power Dependency Control Matrix QACCEPTn outputs.

    Each bit acknowledges an associated bit on PDCMRETQREQn by returning the request input value. This acts as a four-phase handshake so that the driver of each request bit can determine that the request has been seen by receiving unit.

These signals provides a way for an external power domain to request for a domain within the system to remain powered so that the external domain can access the internal power domain or at least request that the internal domain retain its register context. For example, the external domain may want to access the Main interconnect in the PD\_SYS domain.

1. External domain raises an interrupt with the host processor, which if not already ON will wake up PD\_SYS.
2. Host processor sets the relevant bit in PDCM\_PD\_SYS\_SENSE.S\_PDCMONQREQ{0-<PDCMQCHWIDTH-1>}.

The external system can now keep PD\_SYS powered using one of the PDCMONQREQn signals.

Similarly, if the external domain required PD\_SYS to maintain state, but did not currently require access to it:

1. External domain raises an interrupt with the host processor, which if not already ON will wake up PD\_SYS.
2. Host processor sets the relevant bit in PDCM\_PD\_SYS\_SENSE.S\_PDCMRETQREQ{0-<PDCMQCHWIDTH-1>}.

The external system can now ensure PD\_SYS retains state using one of the PDCMRETQREQn signals.

The four-phase handshake must be used to ensure that there is no race condition between ending a bus access that wakes-up the domain and activating the keep-up of the domain.

These are asynchronous signals that either reside in the PD\_AON power domain or in the PD\_MGMT domain, and the choice is IMPLEMENTATION DEFINED. For more information on registers that use these signals and description of related functionality, see [System Control Register Block](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block?lang=en "The System Control Register Block implements registers for power, clocks, resets, and other general system control. This module resides at base address 5802_1000 in the Secure region. The System Control Register Block is Secure privileged access only. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes results in its write data ignored.") and [Power Control Infrastructure](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure?lang=en "CRSAS Ma1 supports three possible power infrastructure levels:").
