# Debug Infrastructure

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Debug-Infrastructure>

### Debug Infrastructure

CRSAS Ma1 supports two possible configurations that define the extent of its debug system infrastructure. These are as follows:

- HASCSS = 0: In this Basic Debug configuration, a CoreSight SoC-600 based common debug infrastructure is not defined and does not exist. Instead, all debug interfaces are brought out from the processor as expansion interfaces. When HASCSS = 0, NUMCPU must be 0.
- HASCSS = 1: In this Full Debug configuration, a CoreSight Soc-600 based common debug infrastructure exists and is called the Debug System.

A debug access to any of the systems obeys normal memory map and decode rules, but must not cause a security violation interrupt to be generated, if the debugger performs an operation that would normally cause one.

- **[Basic Debug Configuration](/documentation/102803/0000/Functional-Description/Debug-Infrastructure/Basic-Debug-Configuration?lang=en)**
   When HASCSS = 0, there can only be one processor and the system does not include a common shared CoreSight SoC-600 based debug infrastructure. Instead, the following applies:
- **[Full Debug Configuration](/documentation/102803/0000/Functional-Description/Debug-Infrastructure/Full-Debug-Configuration?lang=en)**
   When HASCSS = 1 and DEBUGLEVEL > 0, the system contains a CoreSight SoC-600 based debug infrastructure. This infrastructure provides the following functionality:
