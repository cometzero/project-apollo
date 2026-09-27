# Basic Debug Configuration

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Debug-Infrastructure/Basic-Debug-Configuration>

### Basic Debug Configuration

When HASCSS = 0, there can only be one processor and the system does not include a common shared CoreSight SoC-600 based debug infrastructure. Instead, the following applies:

- The processor’s separate debug power domain, if it exists, is merged into a single power domain PD\_DEBUG, which is controlled using a single PPU, DEBUG\_PPU.
- The processor’s debug interfaces, if they exist depending on the DEBUGLEVEL configuration, are brought out as expansion interfaces. See [Debug and trace related interfaces](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces?lang=en "This section describes the debug and trace related interfaces of CRSAS Ma1.").
