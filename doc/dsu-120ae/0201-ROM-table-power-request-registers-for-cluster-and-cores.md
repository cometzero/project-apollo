# ROM table power request registers for cluster and cores

Source: <https://developer.arm.com/documentation/107721/0001/ROM-tables/ROM-table-power-request-registers-for-cluster-and-cores>

### ROM table power request registers for cluster and cores

Your debugger can program up the appropriate Debug Power Control Registers to request a powerup for the cluster, cores, or complexes from the corresponding Power Policy Unit (PPU).

Your debugger can use the power control register, DBGPCR<n>, located in the cluster ROM table, to make a request to powerup core<n> or complex<n>, where n corresponds to the ROMENTRY number for the core or complex.

Similarly, your debugger can use the power control register, DBGPCR0, located in the DebugBlock ROM table, to make a request to powerup the DSU-120AE DynamIQ™ cluster.

Each corresponding core or cluster PPU then reacts to the request that was made as appropriate.
