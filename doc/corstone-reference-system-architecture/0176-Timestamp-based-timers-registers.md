# Timestamp-based timers registers

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers>

### Timestamp-based timers registers

CRSAS Ma1 implements four timestamp-based timers in the system, TIMER<x> where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See [Secure access configuration register block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.").

All timestamp timers, except for Timer3, reside in the PD\_SYS power domain and are reset by nWARMRESETSYS, while the Timer 3 resides in the PD\_AON power domain and is reset by nWARMRESETAON.

For more information, see [System timer components](/documentation/102803/0000/System-timer-components?lang=en "The system timer components are:") appendix.
