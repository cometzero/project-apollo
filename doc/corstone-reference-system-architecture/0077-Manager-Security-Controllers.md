# Manager Security Controllers

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Manager-Security-Controllers>

### Manager Security Controllers

Manager Security Controllers (MSC) in the system transform memory transactions issued by non-CPU managers, that does not support Arm TrustZone for Armv8-M, into memory transactions suitable to Arm TrustZone for Armv8-M systems.

Within CRSAS Ma1, Manager peripheral interfaces are protected using MSCs. These are controlled by the [Secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored."). MSC protected Managers can raise interrupt on security violation and response with bus error or RAZ/WI depending on the global [SECRESPCFG](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/SECRESPCFG?lang=en "The Security Violation Response Configuration Register is used to define the response to an access that causes security violation on the Bus Fabric.") configuration.

For more information, see Arm® CoreLink™ SIE-200 System IP for Embedded Technical Reference Manual and Arm® CoreLink™ SIE-300 AXI5 System IP for Embedded Technical Reference Manual.
