# System and Security Control

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/System-and-Security-Control>

### System and Security Control

CRSAS Ma1 provides several registers in the system to allow various features of the system to be discovered, configured and controlled. These registers are grouped into four register blocks:

Secure Access Configuration Register Block
:   The Secure Access Configuration Register Block provides registers to configure Peripheral Protection Controllers (PPC) and Manager Security Controllers (MSC) that reside in the system and in the expansion system through the Security Control Expansion interface. These are Secure access-only registers. For more information on the registers implemented in this block, see
    [Secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.").

Non-secure Access Configuration Register Block
:   The Non-secure Access Configuration Register Block provides registers to configure Peripheral Protection Controllers (PPC) that resides in the system and in the expansion system through the Security Control Expansion interface. These are Non-secure access-only registers. For more information on the registers implemented in this block, see
    [Non-secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block?lang=en "The Non-secure Access Configuration Register Block implements program visible states that allow software to control various security gating units within the design. This register block base address is 4008_0000. These registers are Non-secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.").

System Information Register Block
:   The System Information Register Block provides information on the system configuration and identity. For more information on the registers implemented in this block, see
    [SYSINFO Register Block](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block?lang=en "The System Information Register Block provides information on the system configuration and identity. This register block is read-only and is accessible by accesses of any security attributes. This module resides at base address 5802_0000 in the Secure region, and 4802_0000 in the Non-secure region.").

System Control Register Block
:   The System Control Register Block implements registers for power, clocks, resets and other general system control. For more information on the registers implemented in this block, see
    [System Control Register Block](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block?lang=en "The System Control Register Block implements registers for power, clocks, resets, and other general system control. This module resides at base address 5802_1000 in the Secure region. The System Control Register Block is Secure privileged access only. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes results in its write data ignored.").
