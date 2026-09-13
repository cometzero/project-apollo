# Cluster PPU mode control

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Cluster-PPU-mode-control>

### Cluster PPU mode control

The Power Policy Units (PPUs), that are integrated into the cluster, control all the PPU modes for all components in the cluster. There is one PPU for the DSU-120AE DynamIQ™ cluster which is responsible for controlling the PPU modes of the cluster.

A component such as a System Control Processor (SCP) can program the cluster PPU through the utility bus to set the required power policy. The cluster PPU controls the low-level details of powering up, powering down, and resetting domains as necessary to implement the requested policy. The hardware performs any actions to reach the requested power mode, such as gating clocks, cleaning and invalidating caches, or disabling coherency.
