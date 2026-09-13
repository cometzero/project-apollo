# Clocks and resets

Source: <https://developer.arm.com/documentation/107721/0001/Clocks-and-resets>

### Clocks and resets

The DynamIQ Shared Unit-120AE (DSU-120AE) has separate clock signals for each of the standalone cores (those cores not in a complex), and for each complex. There are also clocks for the internal logic, and some of the external interfaces of the DSU-120AE.

The DSU-120AE has a cluster-wide Cold reset, a DebugBlock reset, and a reset to be used with Memory Built-In Self Test (MBIST) testing. Implicit resets in the cluster logic and cores can also occur due to power state changes driven from the Power Policy Units (PPUs).
