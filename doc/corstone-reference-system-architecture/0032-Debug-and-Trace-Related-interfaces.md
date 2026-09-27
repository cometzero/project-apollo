# Debug and Trace Related interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Debug-and-Trace-Related-interfaces>

### Debug and Trace Related interfaces

This section describes the debug and trace related interfaces of CRSAS Ma1.

- **[Debug Access interface](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/Debug-Access-interface?lang=en)**
   When DEBUGLEVEL > 0, CRSAS Ma1 provides interfaces for debug access from an external Debug Access Port or an external debug infrastructure. Depending on the HASCSS configuration, the interface or interfaces provide the following:
- **[Debug Timestamp interface](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/Debug-Timestamp-interface?lang=en)**
   When DEBUGLEVEL = 2, CRSAS Ma1 provides one or more 64-bit timestamp input or inputs. This timestamp is expected to be driven by a timestamp generator in the subsystem expansion. Depending on HASCSS configuration, the interface or interfaces are as follows:
- **[Cross Trigger Channel interface](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/Cross-Trigger-Channel-interface?lang=en)**
   When DEBUGLEVEL > 0, CRSAS Ma1 includes one or more sets of Cross Trigger Channel inputs and Cross Trigger Channel outputs to allow partners to expand the cross trigger infrastructure as follows.
- **[Cross Trigger Interface](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/Cross-Trigger-Interface?lang=en)**
   When DEBUGLEVEL > 0 and HASCSS > 0, CRSAS Ma1 includes a shared Cross Trigger Interface (CTI) module. Some trigger signals to and from the CTI are used within the system, while a number is made available to system expansion. The following table lists the trigger signals that are available for system expansion.
- **[Debug APB Expansion interface](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/Debug-APB-Expansion-interface?lang=en)**
   When DEBUGLEVEL > 0 and HASCSS = 1, CRSAS Ma1 provides a Debug APB expansion interface so that partners can add more debug functionality to the Debug System. This interface is only accessible through:
- **[CPU<n> External Peripheral interface EPPB](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/CPU-n--External-Peripheral-interface-EPPB?lang=en)**
   Each CPU<n> in the system provides an interface that allows users to add peripherals to the External PPB region that are private to each processor.
- **[ATB Trace interfaces](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/ATB-Trace-interfaces?lang=en)**
   When DEBUGLEVEL = 2, CRSAS Ma1 provides interfaces to output trace data to an expansion Trace Port Interface Unit (TPIU). The number and types of interfaces vary depending on the HASCSS configuration as follows:
- **[Debug Authentication interface](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces/Debug-Authentication-interface?lang=en)**
   The debug authentication signals of the subsystem reside in the PD\_MGMT power domain, when PILEVEL = 2 its states are saved and restored when entering and then leaving the HIBERNATION1 lower power state, respectively. The state retention is IMPLEMENTATION DEFINED and may be performed using shadow registers in PD\_AON. Throughout HIBERNATION1 low power state these signals must be driven to PD\_AON if used in PD\_AON and remain static.
