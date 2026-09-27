# SLOWCLK AON Timers

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Timers-and-Watchdogs/SLOWCLK-AON-Timers>

### SLOWCLK AON Timers

The second class of timers and watchdogs are simple CMSDK based 32-bit timers that run on SLOWCLK. They reside in PD\_AON power domain and are reset by nWARMRESETAON. A single timer and a single Secure privileged Watchdog are provided and are expected to be used when the system is in HIBERNATION{0-1} when potentially only SLOWCLK is available and running and all other clocks are off.

These timers are mapped to the following addresses:

- SLOWCLK Timer at address 0x4802\_F000 and aliased to 0x5802\_F000.
- Secure Privileged SLOWCLK Watchdog Timer at address 0x5802\_E000.

The SLOWCLK Timer can be configured by software to be Secure or Non-secure access only, and privileged or unprivileged access through the Peripheral Protection Controller that is controlled through registers in the Secure Access Configuration Register Block and the Non-secure Access Configuration Register Block. For more information, see [Secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.") and [Non-secure Access Configuration register block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block?lang=en "The Non-secure Access Configuration Register Block implements program visible states that allow software to control various security gating units within the design. This register block base address is 4008_0000. These registers are Non-secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored."). The watchdog is Secure privilege access only. All CMSDK timers and watchdog timer generate interrupts, but the Secure Watchdog can request a Cold reset of the system if double timeout occurs.

For more information on CMSDK Timers and watchdog, see Arm® Cortex®-M System Design Kit Technical Reference Manual.
