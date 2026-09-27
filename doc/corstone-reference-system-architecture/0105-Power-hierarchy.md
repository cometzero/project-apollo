# Power hierarchy

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/Power-hierarchy>

### Power hierarchy

The system at PILEVEL = 1 supports several power domains:

- PD\_AON
- PD\_DEBUG
- PD\_SYS
- PD\_VMR<i>, does not exist if NUMVMBANK = 0
- PD\_CRYPTO
- PD\_NPU<m>, does not exist if NUMNPU = 0
- PD\_CPU<n>
- PD\_CPU<n>EPU
- PD\_CPU<n>RAM
- PD\_CPU<n>TCM

These power domains are hierarchical and the following figure shows the voltage and power domain hierarchy. In the diagram, PD\_MGMT is now merged and part of PD\_AON.

Figure 1. Voltage and Power domain hierarchy of a subsystem with PILEVEL = 1

![Voltage and Power domain hierarchy of a subsystem with PILEVEL = 1](images/0105-Power-hierarchy-img01.svg)

The figure also shows several bounded power regions:

BR\_DEBUG
:   This is controlled by a single PPU, DEBUG\_PPU.

    The power domain in BR\_DEBUG is:

    - PD\_DEBUG. This is a combined power gated logic and memory domain for all debug logic in the system.

BR\_SYS
:   This is controlled by a single PPU, SYS\_PPU.

    The power domains in BR\_SYS are:

    - PD\_SYS
    - PD\_VMR<i>, one for each VM<i>, where i is 0 to NUMVMBANK-1. PD\_VMR<i> does not exist when NUMVMBANK = 0.

BR\_CPU< n>
:   Each is controlled by a single PPU, CPU<n>\_PPU.

    The power domains in BR\_CPU<n> are:

    - PD\_CPU<n>
    - PD\_CPU<n>EPU
    - PD\_CPU<n>RAM
    - PD\_CPU<n>TCM

BR\_CRYPTO
:   This is controlled by a single PPU, CRYPTO\_PPU.

    The power domain in BR\_CRYPTO is:

    - PD\_CRYPTO

BR\_NPU<m>
:   Each NPU bounded region is controlled by a single PPU, NPU<m>\_PPU.

    The power domain in BR\_NPU<m> is:

    - PD\_NPU<m>
