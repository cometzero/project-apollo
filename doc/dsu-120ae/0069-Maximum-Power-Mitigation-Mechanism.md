# Maximum Power Mitigation Mechanism

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Maximum-Power-Mitigation-Mechanism>

### Maximum Power Mitigation Mechanism

The DynamIQ Shared Unit-120AE (DSU-120AE) implements a Maximum Power Mitigation Mechanism (MPMM) feature that can be used to limit high activity events within the cluster, or trade off bandwidth versus power.

Larger configurations of the DSU-120AE support a very large bandwidth, and this can cause a lot of dynamic power to be consumed. It might be impractical or too expensive for a system implementer to build the System On Chip (SoC) power supply to support the maximum current draw from the DSU-120AE at the same time as the cores, Graphics Processing Unit (GPU), and any other components are also consuming their maximum current. To assist with overall power mitigation, the DSU-120AE implements a cluster MPMM.

The MPMM mechanism provides a number of gears. Each gear restricts the bandwidth available by an increasing amount. The restriction is implemented by limiting the number of transactions that can access the tag pipeline and therefore the RAMs in the L3 cache slice. The gear in use can either be programmed using the MPMM registers through the utility bus, or controlled through input signals. The system can then trade off bandwidth versus power based on information of what other system components are doing.

For more information on MPMM, see the Maximum Power Mitigation Mechanism section of the System design chapter in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
