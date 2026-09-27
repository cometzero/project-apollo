# Power Control Q-Channel and P-Channel Expansion Device interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Power-Control-Q-Channel-and-P-Channel-Expansion-Device-interfaces>

### Power Control Q-Channel and P-Channel Expansion Device interfaces

CRSAS Ma1 provides power control Q-Channel or P-Channel Device interfaces to allow expansion logic to handshake and coordinate the expansion logic power state.

Each power domain that supports expansion is provided with either Q-Channel or P-Channel interfaces as follows:

- MGMTPWR Q-Channel or P-Channel Device interface for PD\_MGMT. This interface resides in the PD\_MGMT power domain and must exist when PILEVEL = 2. When PILEVEL < 2, this interface is not required, but if it exists, it resides in PD\_AON domain and can be tied or used to handshake Warm reset entry for expansion logic residing in the PD\_AON domain.
- SYSPWR Q-Channel or P-Channel Device interface for PD\_SYS.
- DEBUGPWR Q-Channel or P-Channel Device interface for PD\_DEBUG.
- CPU<n>PWR Q-Channel or P-Channel Device interface for PD\_CPU<n>. This interface must exist when PILEVEL > 0. When PILEVEL = 0, this interface is not required, but if it exists, it resides in PD\_SYS domain and must be loop backed and tied.
- CRYPTOPWR Q-Channel or P-Channel Device interface for PD\_CRYPTO. This interface must exist when both PILEVEL = 2 and HASCRYPTO = 1.

These Q-Channel or P-Channel Device interfaces are driven by expansion logic that resides within their respective power domain that they control and are used to do the following:

- Used by the expansion logic to indicate through the QACTIVE or PACTIVE signal that the expansion logic is IDLE or hint that it wants to enter a different power state.
- For a power controller to request the expansion logic to enter a different power state.
- Allow the expansion logic to accept for deny the request to enter a different power state.

The choice between Q-Channel or P-Channel interface is IMPLEMENTATION DEFINED. The Q-Channel or P-Channel interfaces do not support the waking of the power domain, since they reside within the power domain that is being controlled. Instead, associated Power Control Wakeup Q-Channel Device interfaces described in [Power Control Wakeup Q-Channel Device interfaces](/documentation/102803/0000/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Power-Control-Wakeup-Q-Channel-Device-interfaces?lang=en "CRSAS Ma1 provides power control Wakeup Q-Channel Device interfaces to allow expansion logic to request for specific power domains to power up. The Q-Channel interfaces and the domains they control are:") should be used to request for specific power domains to power up.

Currently, each domain is described as having at least one Q-Channel or P-Channel interface. However, an implementation can provide multiple Q-Channel, multi-bit Q-Channel or multiple P-Channel interfaces per domain in order, for example, to sequence expansion logic when entering lower power states. The number of Power Control Q-Channel or P-Channel per domain is therefore IMPLEMENTATION DEFINED.

These Power Control Device Q-Channel or P-Channel interfaces are either asynchronous interfaces or are synchronous to the clock used in each domain that each of the Q-Channel or P-Channel interfaces control. The choice is IMPLEMENTATION DEFINED.
