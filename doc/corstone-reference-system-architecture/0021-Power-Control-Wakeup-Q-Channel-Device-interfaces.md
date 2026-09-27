# Power Control Wakeup Q-Channel Device interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Power-Control-Wakeup-Q-Channel-Device-interfaces>

### Power Control Wakeup Q-Channel Device interfaces

CRSAS Ma1 provides power control Wakeup Q-Channel Device interfaces to allow expansion logic to request for specific power domains to power up. The Q-Channel interfaces and the domains they control are:

- PWRMGMTWAKE Q-Channel Device Interface for PD\_MGMT. This interface must exist when PILEVEL = 2.
- PWRSYSWAKE Q-Channel Device Interface for PD\_SYS.
- PWRDEBUGWAKE Q-Channel Device Interface for PD\_DEBUG.
- PWRCPU<n>WAKE Q-Channel PD\_CPU<n>. This interface must exist when PILEVEL > 0.

These interfaces all reside in the PD\_AON domain. Because they are power up requests, also referred to as wake up request, we recommend that at minimum, only the QACTIVE signal of each interface is implemented. Therefore, when using these to wake a domain, you must drive and hold the appropriate QACTIVE signal to request to turn on the domain until the domain is ON. For example, to wake PD\_SYS, you must set PWRSYSWAKEQACTIVE Q-Channel signal to request to turn ON until the SYSPWR Q-Channel or P-Channel Device Interface for PD\_SYS indicates that the power domain is ON.

These Wakeup Device Q-Channel interfaces are either asynchronous or are synchronous to the clock used in each domain that each of the Q-Channel interfaces control. The choice is IMPLEMENTATION DEFINED.
