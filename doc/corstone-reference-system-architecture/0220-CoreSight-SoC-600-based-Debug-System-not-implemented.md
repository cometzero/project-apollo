# CoreSight SoC-600 based Debug System not implemented

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-not-implemented>

### CoreSight SoC-600 based Debug System not implemented

The HASCSS parameter lets you define if the CoreSight SoC-600 based Debug System is implemented:

- CoreSight SoC-600 based Debug System does not exist, HASCSS = 1.
- CoreSight SoC-600 based Debug System exists, HASCSS = 0.

When the Common CoreSight Debug Infrastructure does not exist, the Debug System Access Region is not used and therefore the following regions are reserved. These regions when accessed return a bus error response.

- 0xE010\_0000 to 0xE01F\_FFFF
- 0xF010\_0000 to 0xF01F\_FFFF

Without the CoreSight based Debug System, All Debug related interfaces of each processor core are made available as expansion interfaces. A system integrator has to create a debug infrastructure to provide debug access to each core. This infrastructure has to use the debug authentication and debug access control signals to control accessibility to the cores and the system. For more information on these signals, see [Debug Authentication interface](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/Debug-Authentication-interface?lang=en "The debug authentication signals of the subsystem reside in the PD_MGMT power domain, when PILEVEL = 2 its states are saved and restored when entering and then leaving the HIBERNATION1 lower power state, respectively. The state retention is IMPLEMENTATION DEFINED and may be performed using shadow registers in PD_AON. Throughout HIBERNATION1 low power state these signals must be driven to PD_AON if used in PD_AON and remain static.").
