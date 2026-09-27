# Security Control Expansion signals

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Security-Control-Expansion-signals>

### Security Control Expansion signals

CRSAS Ma1 provides additional status and control signals to handle additional Manager Security Controllers (MSC), Memory Protection Controllers (MPC), Peripheral Protection Controllers (PPC) and Bridges with write buffers in the expansion system. These signals allow all the components to be controlled using the same set of security control registers already implemented within the subsystem.

All signals in this section are synchronous to SYSSYSCLK, and the SYSSYSCLK Q-Channel Device Interface is needed to control the availability of SYSSYSCLK. These signals reside in the PD\_SYS power domain and in the nWARMRESETSYS reset domain.

> ### Note
>
> While CRSAS Ma1 defines a full set of signals in this document, many of these interfaces and some of their individual bits can be unimplemented or disabled. These are defined as configuration options in [Configuration options](/documentation/102803/0000/Configuration-options?lang=en "The CRSAS Ma1 specification is configurable, which allow systems based on this specification to scale across the performance, power, and area requirement of the market."). How each configuration option is implemented is IMPLEMENTATION DEFINED.

- **[Memory Protection Controller Expansion](/documentation/102803/0000/Interfaces/Security-Control-Expansion-signals/Memory-Protection-Controller-Expansion?lang=en)**
   CRSAS Ma1 supports up to 16 MPCs to be added to the expansion system.
- **[Peripheral Interconnect Peripheral Protection Controller Expansion](/documentation/102803/0000/Interfaces/Security-Control-Expansion-signals/Peripheral-Interconnect-Peripheral-Protection-Controller-Expansion?lang=en)**
   CRSAS Ma1 supports up to four additional PPCs to be added to the Peripheral Interconnect in the expansion system. The following signals are provided to control the PPC <i> where i is {0-3}.
- **[Main Interconnect Peripheral Protection Controller Expansion](/documentation/102803/0000/Interfaces/Security-Control-Expansion-signals/Main-Interconnect-Peripheral-Protection-Controller-Expansion?lang=en)**
   CRSAS Ma1 supports up to four additional PPCs to be added to the Main Interconnect in the expansion system. The following signals are provided to control each PPC<i> where i is {0-3}.
- **[Manager Security Controller Expansion](/documentation/102803/0000/Interfaces/Security-Control-Expansion-signals/Manager-Security-Controller-Expansion?lang=en)**
   CRSAS Ma1 supports up to 16 additional Manager Security Controllers (MSC) to be added to the expansion system. The following signals are provided to control each MSC<i> where i is {0-15}.
- **[Bridge Buffer Error Expansion](/documentation/102803/0000/Interfaces/Security-Control-Expansion-signals/Bridge-Buffer-Error-Expansion?lang=en)**
   CRSAS Ma1 supports up to 16 additional bridges with buffer error signalling to be added to the expansion system.
- **[Other Security Expansion signals](/documentation/102803/0000/Interfaces/Security-Control-Expansion-signals/Other-Security-Expansion-signals?lang=en)**
   The following table lists other signals that are related to Security that is needed by PPCs and MSCs in the expansion system.
