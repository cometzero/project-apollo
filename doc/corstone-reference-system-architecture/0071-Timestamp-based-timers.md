# Timestamp-based timers

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Timers-and-Watchdogs/Timestamp-based-timers>

### Timestamp-based timers

The first class of timer and watchdogs are timestamp-based. They use the timestamp value provided on the System Timestamp Interface.

For more information on the System Timestamp Interface, see [System Timestamp Interface](/documentation/102803/0000/Interfaces/System-timestamp-interface?lang=en "CRSAS Ma1 provides a system timestamp input from an expansion timestamp counter. This timestamp is expected to be driven by a timestamp generator in the subsystem expansion. This resides in the PD_AON power domain and nWARMRESETAON reset domain.").

The timestamp-based Timers provided in CRSAS Ma1 have the following features:

- Memory-mapped System Timer with register access through the Peripheral Interconnect
- 64-bit timestamp input, generating events through comparison with a timer value
- An ‘auto-increment’ feature to support regular event generation
- Down counter emulation
- Maskable level interrupt generation

Timestamp-based Watchdog timers are simplified timers that support the following:

- Memory-mapped System Timer with register access through the Peripheral Interconnect
- 64-bit timestamp input, generating events through comparison with a timer value
- An ‘auto-increment’ feature to support refreshing the watchdog
- Watchdog reset request generation on double watchdog timeout
- Separate refresh register access frame to support refreshing from a different security or privilege level

See [Timestamp-based timers registers](/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en "CRSAS Ma1 implements four timestamp-based timers in the system, TIMER<x> where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.") and [Timestamp-based Watchdogs registers](/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en "CRSAS Ma1 implements two timestamp-based watchdogs in the system. All reside in the PD_SYS power domain and are reset by nWARMRESETSYS. One watchdog timer is Secure access only, while another is Non-secure. Each Watchdog Timer implements two register frames, a Control Frame and a Refresh Frame. The Control Frame is always fixed privileged while the Refresh Frame accessibility to unprivileged access is configurable and controlled by PPC0. See PERIPHSPPPC0 and PERIPHNSPPPC0.") for details on the timer registers.

A total of four timestamp-based timers are provided along with two timestamp-based watchdog timers. These are mapped to the following addresses:

- Timer 0 at address 0x4800\_0000 and aliased to 0x5800\_0000.
- Timer 1 at address 0x4800\_1000 and aliased to 0x5800\_1000.
- Timer 2 at address 0x4800\_2000 and aliased to 0x5800\_2000.
- Timer 3 at address 0x4800\_3000 and aliased to 0x5800\_3000.
- Secure Watchdog Timer control frame at address 0x5804\_0000 and refresh frame at 0x5804\_1000.
- Non-secure Watchdog Timer control frame at address 0x4804\_0000 and refresh frame at 0x4804\_1000.

Timer 0, Timer 1, Timer 2, and Timer 3 can be configured by software to be a Secure or a Non-secure timer through the Peripheral Protection Controller (PPC), and the software can control that PPC through the Secure Access Configuration Register Block. See [Secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored."). Security mapping of both watchdog timers are permanently assigned, with one as Non-secure and another as Secure. The control frames are permanently restricted to only privileged accesses while the refresh frames are configurable through PPC to be privileged only or both privileged and unprivileged accessible. All timers and watchdog timers generate interrupts, and the Non-secure watchdog can generate an additional interrupt on a second timeout event for notifying the Secure world. This allows the Secure world to handle the Non-Secure watchdog double timeout instead of directly applying reset to the system immediately. The Secure Watchdog can request a reset of the system if double timeout occurs. The Non-secure Watchdog can be configured by software to do the same if necessary, but by default this is not allowed.

All timestamp-based timers and watchdogs, except for Timer 3, reside in PD\_SYS power domain and are reset by nWARMRESETSYS, while the Timer 3 resides in the PD\_AON power domain and is reset by nWARMRESETAON. Therefore, Timer 3 can generate interrupts to wake the system even if the system is in the Hibernation state where PD\_SYS is turned off or in retention.
