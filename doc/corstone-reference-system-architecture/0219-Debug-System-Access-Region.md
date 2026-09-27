# Debug System Access Region

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Debug-System-Access-Region>

### Debug System Access Region

CRSAS Ma1 supports two key configuration options for the debug system:

- HASCSS = 0. CoreSight SoC-600 based Debug System does not exist. See [CoreSight SoC-600 based Debug System not implemented](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-not-implemented?lang=en "The HASCSS parameter lets you define if the CoreSight SoC-600 based Debug System is implemented:").
- HASCSS = 1. CoreSight SoC-600 based Debug System exists. See [CoreSight SoC-600 based Debug System implemented](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented?lang=en "When the CoreSight based System Debug infrastructure exists within an implementation of CRSAS Ma1 (HASCSS=1), the system provides several Memory Access Ports (MEM-APs) to provide access to each CPU and to the shared debug components in the system.").

- **[CoreSight SoC-600 based Debug System not implemented](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-not-implemented?lang=en)**
   The HASCSS parameter lets you define if the CoreSight SoC-600 based Debug System is implemented:
- **[CoreSight SoC-600 based Debug System implemented](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented?lang=en)**
   When the CoreSight based System Debug infrastructure exists within an implementation of CRSAS Ma1 (HASCSS=1), the system provides several Memory Access Ports (MEM-APs) to provide access to each CPU and to the shared debug components in the system.
