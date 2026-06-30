# Interconnect configuration

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interconnect/Interconnect-configuration>

### Interconnect configuration

The internal interconnect is configured automatically in accordance with the number of cores and ITS blocks in the system. The configuration produces a balanced tree structure with minimum Clock Domain Crossings (CDCs).

The Arm internal scripts limit a single interconnect crossbar to 16 destinations. To work around this limitation, you can use domains in the config file. For example, instead of 32 GCIs in one domain, you can use two domains that each contain 16 GCIs.
