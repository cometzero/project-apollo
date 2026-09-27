# Message Handling Unit

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Message-Handling-Unit>

### Message Handling Unit

When NUMCPU > 0, CRSAS Ma1 implements two Message Handling Units (MHUs) to allow processors to interrupt each other to pass message. Two MHUs are provided so that it is possible for software to place one MHU in the Secure world and another in the Non-secure world. Both MHUs reside in the PD\_SYS power domain and are reset using the nWARMRESETSYS.

See [Message Handling Unit register map](/documentation/102803/0000/Programmers-model/Peripheral-Region/Message-Handling-Unit-register-map?lang=en "The CRSAS Ma1 implements up to two Message Handling Units (MHUs). These allow software to raise interrupts to the CPU cores. Both MHUs are mapped twice into both Secure and Non-secure regions as follows, and a PPC then controls which area each MHU resides:") for details on the MHU registers. The MHUs in the system are expected to conform to the MHUv1 specification.

When NUMCPU = 0, there are no MHUs in the system.
