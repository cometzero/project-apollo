# Peripheral Protection Controllers

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Peripheral-Protection-Controllers>

### Peripheral Protection Controllers

Peripheral Protection Controllers in the system enable the software to control whether a peripheral is accessible to the Secure or Non-secure world, and to control privileged access or unprivileged access. PPC protected peripherals can raise interrupt on security violation and response with bus error or RAZ/WI depending on the global [SECRESPCFG](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/SECRESPCFG?lang=en "The Security Violation Response Configuration Register is used to define the response to an access that causes security violation on the Bus Fabric.") configuration.

For more information, see Arm® CoreLink™ SIE-200 System IP for Embedded Technical Reference Manual and Arm® CoreLink™ SIE-300 AXI5 System IP for Embedded Technical Reference Manual. In CRSAS Ma1, peripherals that are aliased to two memory areas, one Secure, and another Non-secure, are protected by PPCs. The PPC defines which region the peripheral resides in.

Within CRSAS Ma1, subordinate peripheral interfaces are protected using PPCs. These are controlled by the Secure Access Configuration Register Block and Non-secure Access Configuration Register Block. For more information on these register blocks, see [Secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.") and [Non-secure Access Configuration register block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block?lang=en "The Non-secure Access Configuration Register Block implements program visible states that allow software to control various security gating units within the design. This register block base address is 4008_0000. These registers are Non-secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored."). These registers also control Security Control Expansion Signals to drive external PPCs.

Two groups of peripherals protected behind Peripheral Protection Controllers are currently defined in CRSAS Ma1 and these are as follows:

- Peripheral Interconnect Peripheral Protection Controller 0 (PPC0). This group includes the following peripherals:

  - Memory Protection Controller configuration register block
  - Secure Access Configuration Register Block
  - Non-secure Access Configuration Register Block
  - Message Handling Units
  - Timestamp-based Watchdog Control Frames
  - Timestamp-based Watchdog Refresh Frames
  - All Timestamp based Timers
  - Message Handling Units (MHUs)
  - Debug System Access
  - Watchdog Refresh Frames. Secure or Non-secure mapping of Watchdog Refresh Frames is fixed, only their privilege levels are configurable.
  - All NPUs
- Peripheral Interconnect Peripheral Protection Controller 1 (PPC1). This group includes the following peripherals:

  - System Control Register Block
  - SLOWCLK Watchdog Timer
  - PPUs
  - SLOWCLK Timers

> ### Note
>
> Care should be taken if unprivileged access to bus manager in the system is permitted, for example, DMA or NPUs. If unprivileged access is permitted, then unprivileged code has the potential to use these managers to access and modify privileged memory or peripherals. We recommend that only privileged programming access is permitted to these managers.

For more information, see [Secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.").
